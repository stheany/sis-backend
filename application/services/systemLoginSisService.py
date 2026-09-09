"""
SystemLoginSis services is used for interacting between SystemLoginSis dao and routes.
Actually, it is getting the request from user input and do a logic corresponding to the input.
"""
from datetime import datetime

from flask import Response, request, jsonify

from application.dao.systemLoginSisDao import SystemLoginSisDao
from application.models.systemLoginSis import SystemLoginSis
from application.utils.responseMessage import get_const, error_response
from application.utils.password_utils import hash_password


def create_system_user_post() -> Response:
    """
    Create a new system user that login to sis.
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}

    if not body:
        return error_response("BAD_REQUEST_400", "Request body is required.", 40)

    username = body.get("username", None)
    password = body.get("password", None)
    system_id = body.get("system_id", None)
    status = body.get("status", None)
    created_by = body.get("created_by", None)

    if not username or not password:
        return error_response("BAD_REQUEST_400", "Username and password are required.", 40)

    if len(password) < 8:
        return error_response("BAD_REQUEST_400", "Password must be at least 8 characters.", 44)

    system_login_sis_obj: SystemLoginSis = SystemLoginSisDao.get_system_login_sis_by_username(
        username=username)

    if system_login_sis_obj:
        return error_response("BAD_REQUEST_400", "System username already existed!", 20)

    encrypt_password = hash_password(password)
    system_login_sis_obj = SystemLoginSis({
        'username': username,
        'password': encrypt_password,
        'status': status,
        'system_id': system_id,
        'created_by': created_by,
        'created_at': datetime.now()
    })

    SystemLoginSisDao.add_system_login_sis(system_login_sis=system_login_sis_obj)

    response = get_const('SUCCESS_200')
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify


def edit_system_user_put() -> Response:
    """
    Updating the existing system login to sis based on request body.
    :return: A response as json object for the PATCH API request.
    """
    system_login_sis_id = request.args.get("system_login_sis_id", type=str)
    body = request.get_json(silent=True) or {}

    if system_login_sis_id is None or system_login_sis_id == "":
        return error_response("BAD_REQUEST_400", "No system login sis id — please specify it!", 21)

    if not body:
        return error_response("BAD_REQUEST_400", "Request body is required.", 40)

    username = body.get("username", None)
    password = body.get("password", None)
    system_id = body.get("system_id", None)
    status = body.get("status", None)
    updated_by = body.get("updated_by", None)

    system_login_sis_obj: SystemLoginSis = SystemLoginSisDao. \
        get_system_login_sis_by_id(system_login_sis_id=system_login_sis_id)

    if not system_login_sis_obj:
        return error_response("NOT_FOUND_HANDLER_404",
                              f"System login sis with id: {system_login_sis_id} not found!", 22)

    encrypt_password = hash_password(password) if password else system_login_sis_obj.password
    system_login_sis_obj.username = username
    system_login_sis_obj.password = encrypt_password
    system_login_sis_obj.status = status
    system_login_sis_obj.system_id = system_id
    system_login_sis_obj.updated_by = updated_by
    system_login_sis_obj.updated_at = datetime.now()
    SystemLoginSisDao.update_system_login_sis(
        system_login_sis_id=system_login_sis_id, system_login_sis=system_login_sis_obj)

    response = get_const("SUCCESS_200")
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify
