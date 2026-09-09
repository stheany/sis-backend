# settings.py
from __future__ import annotations
import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def _require(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v

def _get_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}

def _get_int(name: str, default: Optional[int] = None) -> Optional[int]:
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    return int(v)

def _mask(name: str, value: Optional[str], secret: bool = False) -> str:
    if value is None:
        return f"{name}=<NONE>"
    if secret and value:
        return f"{name}={value[:4]}***"
    return f"{name}={value}"

# ---------- App ----------
APP_SECRET_KEY = _require("APP_SECRET_KEY")
JWT_SECRET_KEY = _require("JWT_SECRET_KEY")
CSRF_SESSION_KEY = _require("CSRF_SESSION_KEY")
FLASK_ENV   = os.environ.get("FLASK_ENV", "production")
FLASK_DEBUG = _get_bool("FLASK_DEBUG", False)
FLASK_RUN_HOST = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
FLASK_RUN_PORT = _get_int("FLASK_RUN_PORT", 5000)
FLASK_RUN_CERT = os.environ.get("FLASK_RUN_CERT", "")
FLASK_RUN_KEY  = os.environ.get("FLASK_RUN_KEY", "")

# ---------- Oracle SIS DB ----------
import cx_Oracle  # or: import oracledb as cx_Oracle
DB_SERVICE_NAME = _require("DB_SERVICE_NAME")
DB_USERNAME     = _require("DB_USERNAME")
DB_PASSWORD     = _require("DB_PASSWORD")
DB_HOST         = _require("DB_HOST")
DB_PORT         = _get_int("DB_PORT", 1521)

DB_DSN = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE_NAME)
SQLALCHEMY_DATABASE_URI = f"oracle+cx_oracle://{DB_USERNAME}:{DB_PASSWORD}@{DB_DSN}"

# ---------- Flexcube (service name only) ----------
FLEXCUBE_DB_HOST         = _require("FLEXCUBE_DB_HOST")
FLEXCUBE_DB_PORT         = _get_int("FLEXCUBE_DB_PORT", 1521)
FLEXCUBE_DB_SERVICE_NAME = _require("FLEXCUBE_DB_SERVICE_NAME")
FLEXCUBE_DB_USERNAME     = _require("FLEXCUBE_DB_USERNAME")
FLEXCUBE_DB_PASSWORD     = _require("FLEXCUBE_DB_PASSWORD")
FLEXCUBE_URL             = os.environ.get("FLEXCUBE_URL")  # optional

FLEXCUBE_DB_DSN = cx_Oracle.makedsn(
    FLEXCUBE_DB_HOST,
    FLEXCUBE_DB_PORT,
    service_name=FLEXCUBE_DB_SERVICE_NAME
)

# ---- Flexcube HTTP / SOAP knobs (add these) ----
FLEXCUBE_HTTP_TIMEOUT = _get_int("FLEXCUBE_HTTP_TIMEOUT", 60)
FLEXCUBE_VERIFY_SSL   = _get_bool("FLEXCUBE_VERIFY_SSL", True)
SOAP_DEBUG            = _get_bool("SOAP_DEBUG", False)

# ---------- BKLV (Bakong Large Value) ----------
BKLV_SOAP_URL      = os.environ.get("BKLV_SOAP_URL", "")
BKLV_USERNAME      = os.environ.get("BKLV_USERNAME", "")
BKLV_PASSWORD      = os.environ.get("BKLV_PASSWORD", "")
BKLV_SOAP_TIMEOUT  = _get_int("BKLV_SOAP_TIMEOUT", 60)
BKLV_VERIFY_SSL    = _get_bool("BKLV_VERIFY_SSL", True)

# ---------- BKLV REST API (auth + balance inquiry) ----------
BKLV_AUTH_URL          = os.environ.get("BKLV_AUTH_URL", "")
BKLV_REST_USERNAME     = os.environ.get("BKLV_REST_USERNAME", "")
BKLV_REST_PASSWORD     = os.environ.get("BKLV_REST_PASSWORD", "")
BKLV_BALANCE_URL_BASE  = os.environ.get("BKLV_BALANCE_URL_BASE", "")
BKLV_REST_TIMEOUT      = _get_int("BKLV_REST_TIMEOUT", 30)
BKLV_REST_VERIFY_SSL   = _get_bool("BKLV_REST_VERIFY_SSL", True)

# ---------- NCS BKLV SOAP ----------
NCS_BKLV_SOAP_NAMESPACE = os.environ.get("NCS_BKLV_SOAP_NAMESPACE", "http://172.16.17.200/ws")
SOAP_ENV_NS = "http://www.w3.org/2003/05/soap-envelope"
PAIN001_NS = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.05"


# ---------- Iroha / Vault ----------
IROHA_HOST    = os.environ.get("IROHA_HOST")
VAULT_KEY     = os.environ.get("VAULT_KEY")
FIS_KEY       = os.environ.get("FIS_KEY")
NBC_KEY       = os.environ.get("NBC_KEY")
VAULT_ACCOUNT = os.environ.get("VAULT_ACCOUNT")
FIS_ACCOUNT   = os.environ.get("FIS_ACCOUNT")
NBC_ACCOUNT   = os.environ.get("NBC_ACCOUNT")

# ---------- CORS ----------
_raw_cors = os.environ.get("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS: list[str] = [o.strip() for o in _raw_cors.split(",") if o.strip()]
if not CORS_ALLOWED_ORIGINS:
    import warnings
    warnings.warn(
        "CORS_ALLOWED_ORIGINS is not set — defaulting to wildcard '*'. "
        "Set this variable to a comma-separated list of allowed origins in production.",
        stacklevel=2,
    )

# ---------- Mail ----------
MAIL_SERVER   = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT     = _get_int("MAIL_PORT", 587)
MAIL_USE_TLS  = _get_bool("MAIL_USE_TLS", True)
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

# ---------- RabbitMQ / Celery ----------
RABBIT_USER = os.environ.get("RABBIT_USER", "guest")
RABBIT_PASS = os.environ.get("RABBIT_PASS", "guest")
RABBIT_HOST = os.environ.get("RABBIT_HOST", "localhost")
RABBIT_PORT = _get_int("RABBIT_PORT", 5672)
CELERY_BROKER_URL     = f"amqp://{RABBIT_USER}:{RABBIT_PASS}@{RABBIT_HOST}:{RABBIT_PORT}/"
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "rpc://")

# ---------- Optional: debug summary ----------
if FLASK_DEBUG:
    print("[settings] loaded")
    print(" ", _mask("FLASK_ENV", FLASK_ENV))
    print(" ", _mask("DB_HOST", DB_HOST))
    print(" ", _mask("DB_PORT", str(DB_PORT)))
    print(" ", _mask("DB_SERVICE_NAME", DB_SERVICE_NAME))
    print(" ", _mask("DB_USERNAME", DB_USERNAME, secret=True))
    print(" ", _mask("FLEXCUBE_DB_HOST", FLEXCUBE_DB_HOST))
    print(" ", _mask("FLEXCUBE_DB_PORT", str(FLEXCUBE_DB_PORT)))
    print(" ", _mask("FLEXCUBE_DB_SERVICE_NAME", FLEXCUBE_DB_SERVICE_NAME))
    print(" ", _mask("FLEXCUBE_DB_USERNAME", FLEXCUBE_DB_USERNAME, secret=True))
    print(" ", _mask("FLEXCUBE_URL", FLEXCUBE_URL))
    print(" ", _mask("FLEXCUBE_HTTP_TIMEOUT", str(FLEXCUBE_HTTP_TIMEOUT)))
    print(" ", _mask("FLEXCUBE_VERIFY_SSL", str(FLEXCUBE_VERIFY_SSL)))
    print(" ", _mask("SOAP_DEBUG", str(SOAP_DEBUG)))
    print(" ", _mask("RABBIT_HOST", RABBIT_HOST))
    print(" ", _mask("RABBIT_PORT", str(RABBIT_PORT)))