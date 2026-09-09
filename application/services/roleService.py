"""
Role services is used for interacting between role dao and routes.
Actually, it is getting the request from user input and do a logic corresponding to the input.
"""
import copy
from datetime import datetime

from flask import request, jsonify, Response

from application.dao.roleDao import RoleDao
from application.models.role import Role
from application.schemas.roleSchema import RoleSchema
from application.utils.responseMessage import get_const


def role_post() -> Response:
    """
    Create a new role.
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}
    name = body.get("name", None)
    description = body.get("description", None)
    status = body.get("status", None)
    created_by = body.get("created_by", None)
    current_datetime = datetime.now()

    if not name:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "Role name is required."
        response["detail"]["error_code"] = 40
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    role_obj: Role = Role({
        'name': name,
        'description': description,
        'status': status,
        'created_at': current_datetime,
        'created_by': created_by
    })
    RoleDao.add_role(role_obj)

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']

    return response_jsonify


def role_put() -> Response:
    """
    Update the existing role by role id from request body.
    :return: A response as json object for the PUT API request.
    """
    role_id = request.args.get('role_id', None)
    body = request.get_json(silent=True) or {}
    name = body.get('name', None)
    description = body.get('description', None)
    status = body.get('status', None)
    updated_by = body.get('updated_by', None)
    current_date = datetime.now()

    if not role_id:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "role_id is required."
        response["detail"]["error_code"] = 40
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    try:
        role_id = int(role_id)
    except (ValueError, TypeError):
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "role_id must be a valid integer."
        response["detail"]["error_code"] = 41
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    role_obj: Role = RoleDao.get_role_by_id(role_id=role_id)

    if not role_obj:
        response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
        response["detail"]["error_message"] = "Role not found!"
        response["detail"]["error_code"] = 42
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify

    role_obj.name = name
    role_obj.description = description
    role_obj.updated_by = updated_by
    role_obj.updated_at = current_date
    role_obj.status = status

    RoleDao.update_role(role_id=role_id, role=role_obj)

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']

    return response_jsonify


def roles_get() -> Response:
    """
    Retrieve all the roles from the database by using query parameters.
    :return: A response as json object for the GET API request.
    """
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=5, type=int)
    order_by = request.args.get("orderBy", default=Role.role_id)
    order_method = request.args.get("orderMethod", default="asc")

    all_roles: list = RoleDao.get_roles(page=page,
                                        size=size,
                                        order_by=order_by,
                                        order_method=order_method)

    serialized_data = RoleSchema(many=True).dump(all_roles)

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response['detail']['data'] = serialized_data
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']

    return response_jsonify


def role_by_id_get() -> Response:
    """
    Retrieve the role based on role id from request
    :return: A response as json object for the GET API request.
    """
    role_id = request.args.get("role_id")

    if not role_id:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "role_id is required."
        response["detail"]["error_code"] = 40
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    try:
        role_id = int(role_id)
    except (ValueError, TypeError):
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "role_id must be a valid integer."
        response["detail"]["error_code"] = 41
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    role_obj: Role = RoleDao.get_role_by_id(role_id=role_id)

    if not role_obj:
        response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
        response["detail"]["error_message"] = "Role not found!"
        response["detail"]["error_code"] = 42
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify

    serialized_data = RoleSchema().dump(role_obj)

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response['detail']['data'] = serialized_data
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']

    return response_jsonify
