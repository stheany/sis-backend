"""
UserRole services is used for interacting between UserRole dao and routes.
Actually, it is getting the request from user input and do a logic corresponding to the input.
"""
from datetime import datetime

from flask import Response, request, jsonify

from application.dao.roleDao import RoleDao
from application.dao.userRoleDao import UserRoleDao
from application.dao.usersLoginSisDao import UsersLoginSisDao
from application.models.role import Role
from application.models.userRole import UserRole
from application.models.usersLoginSis import UsersLoginSis
from application.utils.responseMessage import get_const, error_response


def user_role_post() -> Response:
    """
    Create a new user role.
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}
    user_id = body.get("user_id", None)
    role_id = body.get("role_id", None)
    created_by = body.get("created_by", None)
    current_datetime = datetime.now()

    if not body:
        return error_response("BAD_REQUEST_400", "Body is required.", 40)

    if user_id is None or role_id is None:
        return error_response("BAD_REQUEST_400", "user_id and role_id are required.", 40)

    user_login_sis_obj: UsersLoginSis = UsersLoginSisDao.get_user_login_sis_by_id(
        users_login_sis_id=user_id)
    role_obj: Role = RoleDao.get_role_by_id(role_id=role_id)

    if user_login_sis_obj is None or role_obj is None:
        return error_response("NOT_FOUND_HANDLER_404", "User Login SIS Obj or Role Obj not found!", 38)

    existing_mapping = UserRoleDao.get_user_role_by_user_and_role(
        users_login_sis_id=user_id,
        role_id=role_id
    )
    if existing_mapping is not None:
        return error_response("CONFLICT_409", "This role is already assigned to the user.", 46)

    user_role_obj: UserRole = UserRole({
        'users_login_sis_id': user_id,
        'role_id': role_id,
        'created_at': current_datetime,
        'created_by': created_by
    })
    UserRoleDao.add_user_role(user_role=user_role_obj)

    response = get_const('SUCCESS_200')
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify


def user_role_put() -> Response:
    """
    Update the existing user role base on request body.
    :return: A response as json object for the PUT API request.
    """
    user_role_id = request.args.get("user_role_id", None)
    body = request.get_json(silent=True) or {}
    user_id = body.get("user_id", None)
    role_id = body.get("role_id", None)
    updated_by = body.get("updated_by", None)
    current_datetime = datetime.now()

    # 1. Validate required inputs
    if not body:
        return error_response("BAD_REQUEST_400", "Body is required.", 40)

    if user_role_id is None or user_id is None or role_id is None:
        return error_response("BAD_REQUEST_400", "user_role_id, user_id, and role_id are required.", 38)

    # 2. Fetch the record being edited — fail fast before querying related objects
    user_role_obj: UserRole = UserRoleDao.get_user_role_by_id(user_role_id=user_role_id)
    if user_role_obj is None:
        return error_response("NOT_FOUND_HANDLER_404", "User Role not found!", 40)

    # 3. Validate the new related objects exist
    user_login_sis_obj: UsersLoginSis = UsersLoginSisDao.get_user_login_sis_by_id(
        users_login_sis_id=user_id)
    role_obj: Role = RoleDao.get_role_by_id(role_id=role_id)

    if user_login_sis_obj is None or role_obj is None:
        return error_response("NOT_FOUND_HANDLER_404", "User Login SIS Obj or Role Obj not found!", 39)

    # 4. Apply the update
    user_role_obj.users_login_sis_id = user_id
    user_role_obj.role_id = role_id
    user_role_obj.updated_at = current_datetime
    user_role_obj.updated_by = updated_by
    UserRoleDao.add_user_role(user_role=user_role_obj)

    response = get_const('SUCCESS_200')
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify
