"""
Thin REST client for BKLV's real auth + balance-inquiry surface — distinct
from the SOAP makeFullFundTransfer client in worker/bklv_tasks.py. Lives at
the repo root (not under application/ or worker/) so both the web process
and the Celery worker can import it directly without pulling in the other
side's package-level dependencies (application/__init__.py's Flask/SQLAlchemy
setup, or worker/__init__.py's Celery/iroha setup) — same reason settings.py
itself lives at the root and is imported directly by both sides.

ASSUMPTIONS — flagged here because they're guesses, not confirmed against a
real response body. Implemented defensively (checks several plausible field
names, raises with the raw body on a miss) so a wrong guess fails loudly
instead of silently misreading a field:
  - POST {auth_url} with {"username","password","rememberMe":true} is a
    JHipster-style UAA login (the exact shape of the real sample call), whose
    default response is {"id_token": "<JWT>"} — also checks "token" and
    "access_token" in case the real deployment differs.
  - GET {balance_url_base}/<bic> returns a JSON body with the current
    balance under "balance", "availableBalance", or "amount", and (also a
    guess) its currency under "currency", "ccy", or "currencyCode".
Confirm both against the real BKLV API and adjust _TOKEN_FIELDS /
_BALANCE_FIELDS / _CURRENCY_FIELDS below if they differ.

PER-BANK ENDPOINTS — each participant bank runs its own BKLV gateway (there
is no single shared BKLV hub); SIS calls a specific bank's own endpoint for
a debit or credit involving that bank, not one central URL for everyone.
BKLV_BANK_ENDPOINTS holds that per-BIC mapping ("BIC1=baseurl1,BIC2=baseurl2"),
e.g. "ABAAKHPPXXX=http://bklv-mock-aba:8001,ACLBKHPPXXX=http://bklv-mock-acleda:8002".
A bank's auth/balance URLs are derived from its base URL
({base}/api/authenticate, {base}/tps/api/balance-inquiry/fast-core/<bic>).
Any BIC not listed there falls back to the single BKLV_AUTH_URL /
BKLV_BALANCE_URL_BASE pair (the shared mock covering banks that don't have
their own dedicated instance for this demo).
"""
import logging
import os
import threading
import time

import requests

from settings import (
    BKLV_AUTH_URL,
    BKLV_BALANCE_URL_BASE,
    BKLV_REST_PASSWORD,
    BKLV_REST_TIMEOUT,
    BKLV_REST_USERNAME,
    BKLV_REST_VERIFY_SSL,
)

logger = logging.getLogger(__name__)

_TOKEN_FIELDS = ('id_token', 'token', 'access_token')
_BALANCE_FIELDS = ('balance', 'availableBalance', 'amount')
_CURRENCY_FIELDS = ('currency', 'ccy', 'currencyCode')

_TOKEN_TTL_SECONDS = 15 * 60


def _parse_bank_endpoints(raw: str) -> dict:
    endpoints = {}
    for pair in (raw or '').split(','):
        pair = pair.strip()
        if not pair or '=' not in pair:
            continue
        bic, base = pair.split('=', 1)
        bic = bic.strip().upper()
        base = base.strip().rstrip('/')
        if bic and base:
            endpoints[bic] = base
    return endpoints


_BANK_BASE_URLS = _parse_bank_endpoints(os.environ.get('BKLV_BANK_ENDPOINTS', ''))

# Tokens are cached per auth_url now, not globally — ABA's gateway and
# ACLEDA's gateway are independent auth realms, each with its own token.
_lock = threading.Lock()
_cached_tokens = {}  # auth_url -> (token, cached_at_monotonic)


class BklvClientError(Exception):
    """Any failure talking to BKLV's REST API — auth, network, or an unrecognized response shape."""


def bank_transfer_endpoint(bic: str):
    """
    Returns this bank's own makeFullFundTransfer URL (SOAP, used by
    worker/bklv_tasks.py — a different surface from the REST auth/balance
    calls in this module) if BKLV_BANK_ENDPOINTS configures a dedicated
    gateway for this BIC, else None — meaning the caller should fall back
    to the shared BKLV_SOAP_URL. Each bank's own gateway exposes this at
    the same path, /cb-adapter/BakongWebService/NBCInterface — only the
    host differs per bank (e.g. http://ABA-bklv/..., http://AC-bklv/...).
    """
    base = _BANK_BASE_URLS.get((bic or '').upper())
    return f"{base}/cb-adapter/BakongWebService/NBCInterface" if base else None


def _endpoints_for(bic: str):
    """
    Returns (auth_url, balance_url_base) for a BIC: its own dedicated
    gateway if BKLV_BANK_ENDPOINTS configures one, else the shared fallback
    (BKLV_AUTH_URL / BKLV_BALANCE_URL_BASE).
    """
    base = _BANK_BASE_URLS.get((bic or '').upper())
    if base:
        return f"{base}/api/authenticate", f"{base}/tps/api/balance-inquiry/fast-core"
    return BKLV_AUTH_URL, BKLV_BALANCE_URL_BASE


def _authenticate(auth_url: str) -> str:
    if not auth_url:
        raise BklvClientError("No BKLV auth URL configured for this bank")
    try:
        response = requests.post(
            auth_url,
            json={'username': BKLV_REST_USERNAME, 'password': BKLV_REST_PASSWORD, 'rememberMe': True},
            timeout=BKLV_REST_TIMEOUT,
            verify=BKLV_REST_VERIFY_SSL,
        )
    except requests.exceptions.RequestException as err:
        raise BklvClientError(f"BKLV auth request failed ({auth_url}): {err}") from err

    if not response.ok:
        raise BklvClientError(f"BKLV auth failed ({auth_url}): HTTP {response.status_code}: {response.text[:300]}")

    body = response.json()
    for field in _TOKEN_FIELDS:
        if body.get(field):
            return body[field]
    raise BklvClientError(f"BKLV auth response had none of {_TOKEN_FIELDS}: {body}")


def _get_token(auth_url: str, force_refresh: bool = False) -> str:
    with _lock:
        cached = _cached_tokens.get(auth_url)
        stale = cached is None or (time.monotonic() - cached[1]) > _TOKEN_TTL_SECONDS
        if force_refresh or stale:
            token = _authenticate(auth_url)
            _cached_tokens[auth_url] = (token, time.monotonic())
            return token
        return cached[0]


def get_account_balance(bic: str) -> dict:
    """
    Query BKLV's real current-account balance for a bank's BIC — routed to
    that bank's own gateway if BKLV_BANK_ENDPOINTS configures one, else the
    shared fallback endpoint.
    """
    if not bic:
        raise BklvClientError("bic is required")

    auth_url, balance_url_base = _endpoints_for(bic)
    if not balance_url_base:
        raise BklvClientError(f"No BKLV balance endpoint configured for bic={bic}")

    url = f"{balance_url_base.rstrip('/')}/{bic}"

    def _call(token: str):
        return requests.get(
            url,
            headers={'Authorization': f'Bearer {token}'},
            timeout=BKLV_REST_TIMEOUT,
            verify=BKLV_REST_VERIFY_SSL,
        )

    try:
        response = _call(_get_token(auth_url))
        if response.status_code == 401:
            response = _call(_get_token(auth_url, force_refresh=True))
    except requests.exceptions.RequestException as err:
        raise BklvClientError(f"BKLV balance inquiry request failed for bic={bic}: {err}") from err

    if not response.ok:
        raise BklvClientError(
            f"BKLV balance inquiry failed for bic={bic}: HTTP {response.status_code}: {response.text[:300]}"
        )

    body = response.json()
    balance = None
    for field in _BALANCE_FIELDS:
        if field in body and body[field] is not None:
            try:
                balance = float(body[field])
            except (TypeError, ValueError) as err:
                raise BklvClientError(f"BKLV balance field {field!r} was not numeric: {body[field]!r}") from err
            break
    if balance is None:
        raise BklvClientError(f"BKLV balance response had none of {_BALANCE_FIELDS}: {body}")

    currency = None
    for field in _CURRENCY_FIELDS:
        if body.get(field):
            currency = body[field]
            break

    return {'balance': balance, 'currency': currency}


def get_balance(bic: str) -> float:
    """
    Query BKLV's real current-account balance for a bank's BIC.
    Raises BklvClientError on any failure — see get_account_balance() for
    callers that also need the currency.
    """
    return get_account_balance(bic)['balance']
