# Import flask packages
import copy
import logging
import time

from celery import Celery
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError, OperationalError
from application.utils import banner

from application.utils.responseMessage import get_const
from settings import CORS_ALLOWED_ORIGINS as _cors_origins
from settings import CELERY_BROKER_URL as _celery_broker, CELERY_RESULT_BACKEND as _celery_backend

# define the database object
db = SQLAlchemy()

# define Marshmallow
ma = Marshmallow()

# define Flask-Mail
mail = Mail()

# define celery
celery = Celery('worker',
                broker=_celery_broker,
                backend=_celery_backend)

def create_app():
    # Import model
    from application.models.tokenBlocklist import TokenBlocklist

    # Define the WSGI application object
    app = Flask(__name__)

    # Define configuration variables from config.py
    app.config.from_object('config')

    # define CORS — restrict to configured origins; falls back to '*' if not configured
    CORS(app,
         origins=_cors_origins if _cors_origins else "*",
         supports_credentials=True)

    # Define jwt manager
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        _log = logging.getLogger(__name__)
        jti = jwt_payload["jti"]
        # Retry up to 3 times on transient Oracle disconnects (ORA-3113, DPI-1080, etc.)
        for attempt in range(3):
            try:
                token = db.session.query(TokenBlocklist.jti) \
                    .filter_by(jti=jti) \
                    .scalar()
                return token is not None
            except (OperationalError, DatabaseError) as exc:
                db.session.rollback()
                db.session.remove()
                if attempt < 2:
                    _log.warning(
                        "Token blocklist DB error (attempt %d/3), retrying: %s",
                        attempt + 1, exc,
                    )
                    time.sleep(0.2 * (attempt + 1))
                else:
                    # All retries exhausted — fail open (do NOT block the user for a DB hiccup)
                    _log.error(
                        "Token blocklist check failed after 3 attempts — "
                        "treating token as valid: %s", exc,
                    )
                    return False
            except Exception as exc:
                db.session.rollback()
                db.session.remove()
                _log.exception("Unexpected error in token blocklist check: %s", exc)
                return False

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload: dict) -> bool:
        response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
        response["detail"]["error_message"] = "Token has been revoked. Please login again!"
        response["detail"]["error_code"] = 10
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload: dict) -> bool:
        response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
        response["detail"]["error_message"] = "Token has been expired. Please login again!"
        response["detail"]["error_code"] = 11
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
        response["detail"]["error_message"] = "Request does not contain an access token!"
        response["detail"]["error_code"] = 12
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
        response["detail"]["error_message"] = "Invalid access token!"
        response["detail"]["error_code"] = 14
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    # initialize database
    db.init_app(app)
    db.app = app

    # initialize Marshmallow
    ma.init_app(app)

    # initialize Flask-Mail
    mail.init_app(app)

    # Sample HTTP error handling
    @app.errorhandler(404)
    def not_found(error):
        logging.getLogger(__name__).warning("404 error: %s", error)
        response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
        response["detail"]["error_message"] = "The requested resource was not found."
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    @app.errorhandler(Exception)
    def handle_exception(e):
        logging.getLogger(__name__).exception("Unhandled exception")
        response = copy.deepcopy(get_const("SERVER_ERROR_500"))
        response["detail"]["error_message"] = "An internal error occurred."
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    # Import routes
    from application.routes.actionRoute import action_route
    from application.routes.environmentRoute import environment_route
    from application.routes.flexcubeRoute import flexcube_route
    from application.routes.irohaRoute import iroha_route
    from application.routes.menuRoute import menu_route
    from application.routes.permissionRoute import permission_route
    from application.routes.roleRoute import role_route
    from application.routes.systemRoute import system_route
    from application.routes.systemToSisRoute import system_to_sis_route
    from application.routes.userRoute import user_route
    from application.routes.ncsBklvSoapRoute import ncs_bklv_soap_route

    # Register blueprint(s)
    app.register_blueprint(system_to_sis_route)
    app.register_blueprint(action_route)
    app.register_blueprint(system_route)
    app.register_blueprint(environment_route)
    app.register_blueprint(flexcube_route)
    app.register_blueprint(menu_route)
    app.register_blueprint(role_route)
    app.register_blueprint(user_route)
    app.register_blueprint(iroha_route)
    app.register_blueprint(permission_route)
    app.register_blueprint(ncs_bklv_soap_route)

    return app
