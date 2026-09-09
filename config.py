# config.py
import os
from datetime import timedelta
from settings import (
    APP_SECRET_KEY,
    JWT_SECRET_KEY,
    CSRF_SESSION_KEY,
    SQLALCHEMY_DATABASE_URI,
    FLASK_DEBUG,
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USE_TLS,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_DEFAULT_SENDER,
)

# Environment-driven debug (use 0 in prod)
DEBUG = FLASK_DEBUG == "1"

# Flask secrets
SECRET_KEY = APP_SECRET_KEY

# JWT
JWT_SECRET_KEY = JWT_SECRET_KEY
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
PROPAGATION_EXCEPTIONS = True
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Connection pool hardening — prevents stale/dead Oracle connections
# pool_pre_ping: issues a cheap "SELECT 1 FROM DUAL" before handing out
#   any pooled connection; transparently replaces dead ones.
# pool_recycle: forcibly retire connections older than 1800 s (30 min)
#   so they are never older than Oracle's idle timeout (often 60 min).
# pool_size / max_overflow: explicit caps to avoid connection exhaustion.
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 1800,
    "pool_size": 10,
    "max_overflow": 5,
}

# Mail
MAIL_SERVER         = MAIL_SERVER
MAIL_PORT           = MAIL_PORT
MAIL_USE_TLS        = MAIL_USE_TLS
MAIL_USERNAME       = MAIL_USERNAME
MAIL_PASSWORD       = MAIL_PASSWORD
MAIL_DEFAULT_SENDER = MAIL_DEFAULT_SENDER

# Misc Flask settings
CSRF_ENABLED = True
CSRF_SESSION_KEY = CSRF_SESSION_KEY
# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2