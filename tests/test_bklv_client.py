"""
Tests for bklv_client.py — the REST client for BKLV's real auth +
balance-inquiry surface. Lives at the repo root (see that module's
docstring for why), so its test lives in this root-level tests/ dir rather
than application/tests/ or worker/.
"""
from unittest.mock import MagicMock, patch

import pytest

import bklv_client


@pytest.fixture(autouse=True)
def _reset_client_state(monkeypatch):
    """Each test gets its own token cache and its own configured URLs/creds."""
    monkeypatch.setattr(bklv_client, "_cached_token", None)
    monkeypatch.setattr(bklv_client, "_cached_token_at", 0.0)
    monkeypatch.setattr(bklv_client, "BKLV_AUTH_URL", "http://bklv.test/api/authenticate")
    monkeypatch.setattr(bklv_client, "BKLV_REST_USERNAME", "user")
    monkeypatch.setattr(bklv_client, "BKLV_REST_PASSWORD", "pass")
    monkeypatch.setattr(bklv_client, "BKLV_BALANCE_URL_BASE", "http://bklv.test/tps/api/balance-inquiry/fast-core")


def _response(status_code=200, json_body=None, text=""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.ok = 200 <= status_code < 300
    resp.json.return_value = json_body or {}
    resp.text = text
    return resp


def test_authenticate_returns_id_token():
    with patch.object(bklv_client.requests, "post", return_value=_response(json_body={"id_token": "abc123"})):
        token = bklv_client._get_token()
    assert token == "abc123"


def test_authenticate_accepts_alternate_token_field_names():
    with patch.object(bklv_client.requests, "post", return_value=_response(json_body={"access_token": "xyz"})):
        token = bklv_client._get_token()
    assert token == "xyz"


def test_authenticate_raises_on_http_error():
    with patch.object(bklv_client.requests, "post", return_value=_response(status_code=401, text="bad creds")):
        with pytest.raises(bklv_client.BklvClientError):
            bklv_client._get_token()


def test_authenticate_raises_when_no_known_token_field():
    with patch.object(bklv_client.requests, "post", return_value=_response(json_body={"nonsense": "value"})):
        with pytest.raises(bklv_client.BklvClientError):
            bklv_client._get_token()


def test_authenticate_raises_when_auth_url_not_configured(monkeypatch):
    monkeypatch.setattr(bklv_client, "BKLV_AUTH_URL", "")
    with pytest.raises(bklv_client.BklvClientError):
        bklv_client._get_token()


def test_get_balance_returns_numeric_balance():
    with patch.object(bklv_client.requests, "post", return_value=_response(json_body={"id_token": "tok"})), \
         patch.object(bklv_client.requests, "get", return_value=_response(json_body={"balance": 1234.5})):
        balance = bklv_client.get_balance("ABAAKHPPXXX")
    assert balance == 1234.5


def test_get_balance_accepts_alternate_balance_field_names():
    with patch.object(bklv_client.requests, "post", return_value=_response(json_body={"id_token": "tok"})), \
         patch.object(bklv_client.requests, "get", return_value=_response(json_body={"availableBalance": 42})):
        balance = bklv_client.get_balance("ABAAKHPPXXX")
    assert balance == 42.0


def test_get_balance_retries_once_on_401_then_succeeds():
    responses = [_response(status_code=401), _response(json_body={"balance": 999.0})]
    with patch.object(bklv_client.requests, "post", return_value=_response(json_body={"id_token": "tok"})), \
         patch.object(bklv_client.requests, "get", side_effect=responses):
        balance = bklv_client.get_balance("ABAAKHPPXXX")
    assert balance == 999.0


def test_get_balance_raises_when_no_known_balance_field():
    with patch.object(bklv_client.requests, "post", return_value=_response(json_body={"id_token": "tok"})), \
         patch.object(bklv_client.requests, "get", return_value=_response(json_body={"nonsense": 1})):
        with pytest.raises(bklv_client.BklvClientError):
            bklv_client.get_balance("ABAAKHPPXXX")


def test_get_balance_raises_when_bic_missing():
    with pytest.raises(bklv_client.BklvClientError):
        bklv_client.get_balance("")


def test_get_balance_raises_when_balance_url_not_configured(monkeypatch):
    monkeypatch.setattr(bklv_client, "BKLV_BALANCE_URL_BASE", "")
    with pytest.raises(bklv_client.BklvClientError):
        bklv_client.get_balance("ABAAKHPPXXX")


def test_token_is_cached_across_calls():
    with patch.object(bklv_client.requests, "post", return_value=_response(json_body={"id_token": "tok"})) as mock_post, \
         patch.object(bklv_client.requests, "get", return_value=_response(json_body={"balance": 1.0})):
        bklv_client.get_balance("BIC1")
        bklv_client.get_balance("BIC2")
    assert mock_post.call_count == 1


def test_get_account_balance_returns_balance_and_currency():
    with patch.object(bklv_client.requests, "post", return_value=_response(json_body={"id_token": "tok"})), \
         patch.object(bklv_client.requests, "get", return_value=_response(json_body={"balance": 1234.5, "currency": "USD"})):
        detail = bklv_client.get_account_balance("ABAAKHPPXXX")
    assert detail == {"balance": 1234.5, "currency": "USD"}


def test_get_account_balance_accepts_alternate_currency_field_names():
    with patch.object(bklv_client.requests, "post", return_value=_response(json_body={"id_token": "tok"})), \
         patch.object(bklv_client.requests, "get", return_value=_response(json_body={"balance": 1.0, "ccy": "KHR"})):
        detail = bklv_client.get_account_balance("ABAAKHPPXXX")
    assert detail["currency"] == "KHR"


def test_get_account_balance_currency_is_none_when_absent():
    """Only the balance is confirmed required — a response with no known currency field isn't an error."""
    with patch.object(bklv_client.requests, "post", return_value=_response(json_body={"id_token": "tok"})), \
         patch.object(bklv_client.requests, "get", return_value=_response(json_body={"balance": 1.0})):
        detail = bklv_client.get_account_balance("ABAAKHPPXXX")
    assert detail == {"balance": 1.0, "currency": None}
