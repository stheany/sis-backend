"""
System Authentication service is used for authentication between External system to SIS
"""
import copy
import logging
from datetime import datetime

from flask import request, jsonify, session, Response
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt

from application.dao.systemLoginSisDao import SystemLoginSisDao
from application.dao.tokenBlocklistDao import TokenBlocklistDao
from application.models.systemLoginSis import SystemLoginSis
from application.models.tokenBlocklist import TokenBlocklist
from application.schemas.systemLoginSisSchema import SystemLoginSisSchema
from application.utils.responseMessage import get_const, error_response
from application.utils.password_utils import verify_password


def login() -> Response:
    """
    Used for external system login to SIS
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}
    username = body.get("username", None)
    password = body.get("password", None)

    if not username or not password:
        response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    # system login sis object by username
    system_login_sis_obj: SystemLoginSis = SystemLoginSisDao.get_system_login_sis_by_username(username=username)

    if system_login_sis_obj:
        if verify_password(password, system_login_sis_obj.password):
            access_token = create_access_token(
                identity=system_login_sis_obj.system_login_sis_id)

            # store SystemLoginSis object in "system_login_sis" key for flask session
            session["system_login_sis"] = SystemLoginSisSchema().dump(system_login_sis_obj)

            response = copy.deepcopy(get_const('SUCCESS_200'))
            response["detail"]["data"] = {'access_token': access_token}
            response_jsonify = jsonify(response)
            response_jsonify.status_code = response["http_code"]
            return response_jsonify

    response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
    response["detail"]["error_code"] = 13
    response["detail"]["error_message"] = "System login not found!"
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify


def logout() -> Response:
    """
    Used for external system to logout from SIS.
    :return: A response as json object for the POST API request.
    """
    try:
        token = get_jwt()
        token_blocklist_obj: TokenBlocklist = TokenBlocklist({
            "jti": token['jti'],
            "created_at": datetime.now(),
            "remark": "System id {system_id} logout".format(
                system_id=session.get("system_login_sis", {}).get('system_id', 'unknown')
            )
        })
        TokenBlocklistDao.add_token_blocklist(token_blocklist=token_blocklist_obj)

        # when system logout from sis we remove "system_login_sis" key from flask session
        if "system_login_sis" in session.keys():
            session.pop("system_login_sis", None)

        response = copy.deepcopy(get_const('SUCCESS_200'))
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify
    except Exception as e:
        logging.getLogger(__name__).exception("Logout error")
        response = copy.deepcopy(get_const("SERVER_ERROR_500"))
        response["detail"]["error_message"] = "An internal error occurred."
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify
