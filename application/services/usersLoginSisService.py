"""
UserLoginSis services is used for interacting between UserLoginSis dao and routes.
Actually, it is getting the request from user input and do a logic corresponding to the input.
"""
import copy
import re
from datetime import datetime

from flask import request, jsonify, Response

from application.dao.usersLoginSisDao import UsersLoginSisDao
from application.models.usersLoginSis import UsersLoginSis
from application.schemas.usersLoginSisSchema import UsersLoginSisSchema
from application.utils.responseMessage import get_const
from application.utils.password_utils import hash_password


def user_login_sis_post() -> Response:
    """
    Create a new user login to sis.
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}
    username = body.get("username", None)
    password = body.get("password", None)
    first_name = body.get("first_name", None)
    last_name = body.get("last_name", None)
    full_name = body.get("full_name", None)
    description = body.get("description", None)
    email = body.get("email", None)
    status = body.get("status", None)
    created_by = body.get("created_by", None)
    current_datetime = datetime.now()
    encrypt_password = hash_password(password) if password else None

    if not body:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "Request body is required!"
        response["detail"]["error_code"] = 40
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify

    if not username or not password:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "Username or password not specified!"
        response["detail"]["error_code"] = 40
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify

    if len(password) < 8:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "Password must be at least 8 characters."
        response["detail"]["error_code"] = 44
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify

    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "Invalid email format."
        response["detail"]["error_code"] = 43
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify

    user_login_sis_obj: UsersLoginSis = UsersLoginSisDao.get_user_login_sis_by_username(
        username=username)

    if user_login_sis_obj:
        response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
        response["detail"]["error_message"] = "User already existed!"
        response["detail"]["error_code"] = 41
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify
    else:
        user_login_sis_obj: UsersLoginSis = UsersLoginSis({
            'username': username,
            'password': encrypt_password,
            'first_name': first_name,
            'last_name': last_name,
            'full_name': full_name,
            'description': description,
            'email': email,
            'status': status,
            'created_by': created_by,
            'created_at': current_datetime
        })
        UsersLoginSisDao.add_user_login_sis(user_login_sis=user_login_sis_obj)

        response = copy.deepcopy(get_const('SUCCESS_200'))
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response['http_code']

        return response_jsonify


def users_login_sis_get() -> Response:
    """
    Retrieve all the user login sis from the database by using query parameters.
    :return: A response as json object for the GET API request.
    """
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 5, type=int)
    order_by = request.args.get(
        "orderBy", default=UsersLoginSis.users_login_sis_id)
    order_method = request.args.get("orderMethod", default="asc")

    all_user_login_sis: list[UsersLoginSis] = UsersLoginSisDao.get_user_login_sis(page=page,
                                                                                  size=size,
                                                                                  order_by=order_by,
                                                                                  order_method=order_method)

    serialized_data = UsersLoginSisSchema(many=True).dump(all_user_login_sis)

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response['detail']['data'] = serialized_data
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']

    return response_jsonify


def users_login_sis_by_id_get() -> Response:
    """
    Retrieve the Users login to sis based on user id from request body.
    :return: A response as json object for the GET API request.
    """
    user_id = request.args.get('user_id')

    if not user_id:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "user_id is required."
        response["detail"]["error_code"] = 40
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "user_id must be a valid integer."
        response["detail"]["error_code"] = 41
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    user_login_sis_obj: UsersLoginSis = UsersLoginSisDao.get_user_login_sis_by_id(user_id)

    if user_login_sis_obj is None:
        response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
        response["detail"]["error_message"] = "User Login SIS Obj not found!"
        response["detail"]["error_code"] = 37
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify
    else:
        serialized_data = UsersLoginSisSchema().dump(user_login_sis_obj)
        response = copy.deepcopy(get_const('SUCCESS_200'))
        response['detail']['data'] = serialized_data
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response['http_code']

        return response_jsonify
