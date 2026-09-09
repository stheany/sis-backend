"""
Permission services is used for interacting between permission dao and routes.
Actually, it is getting the request from user input and do a logic corresponding to the input.
"""
import copy
from datetime import datetime

from flask import request, jsonify, Response

from application.dao.actionDao import ActionDao
from application.dao.menuDao import MenuDao
from application.dao.permissionDao import PermissionDao
from application.models.permission import Permission
from application.schemas.actionSchema import ActionSchema
from application.schemas.menuSchema import MenuSchema
from application.utils.responseMessage import get_const


def permission_post() -> Response:
    """
    Create a new permission.
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}
    role_id = body.get('role_id', None)
    menu_id = body.get('menu_id', None)
    action_id = body.get('action_id', None)
    created_by = body.get('created_by', None)
    current_date = datetime.now()

    if created_by is None:
        response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
        response["detail"]["error_message"] = "Created by ID not found!"
        response["detail"]["error_code"] = 31
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify

    elif (role_id is None) or (menu_id is None) or (action_id is None):
        response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
        response["detail"]["error_message"] = "Role ID or Menu ID or Action ID not found!"
        response["detail"]["error_code"] = 32
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify

    else:
        permission_obj: Permission = Permission({
            'role_id': role_id,
            'menu_id': menu_id,
            'action_id': action_id,
            'created_by': created_by,
            'created_at': current_date
        })
        PermissionDao.add_permission(permission_obj)

        response = copy.deepcopy(get_const('SUCCESS_200'))
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response['http_code']

        return response_jsonify



def permission_put() -> Response:
    """
    Update the existing permission by permission id from request body.
    :return: A response as json object for the PUT API request.
    """
    body = request.get_json(silent=True) or {}
    role_id = body.get("role_id", None)
    menu_id = body.get("menu_id", None)
    action_id = body.get("action_id", None)
    updated_by = body.get("updated_by", None)
    permission_id = request.args.get("permission_id", None)
    current_datetime = datetime.now()

    if permission_id is None:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "Permission ID is required!"
        response["detail"]["error_code"] = 40
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    try:
        permission_id = int(permission_id)
    except (ValueError, TypeError):
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "Permission ID must be an integer!"
        response["detail"]["error_code"] = 41
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    if (role_id is None) or (menu_id is None) or (action_id is None) or (updated_by is None):
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "Role ID, Menu ID, Action ID, and Updated By are required!"
        response["detail"]["error_code"] = 32
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    permission_obj: Permission = PermissionDao.get_permission_by_id(
        permission_id=permission_id)

    if not permission_obj:
        response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
        response["detail"]["error_message"] = "Permission not found!"
        response["detail"]["error_code"] = 33
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify

    permission_obj.role_id = role_id
    permission_obj.menu_id = menu_id
    permission_obj.action_id = action_id
    permission_obj.updated_by = updated_by
    permission_obj.updated_at = current_datetime

    PermissionDao.update_permission(
        permission_id=permission_id, permission=permission_obj)

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']

    return response_jsonify


def check_allow_permission_by_role_id(role_id: int) -> dict:
    """
    Checking allow actions and menus permission based on role id.
    :param role_id: Role ID which uniquely identifies the Permission.
    :return: Boolean true or false
    """
    permission_list = PermissionDao.get_permissions_by_role_id(role_id=role_id)

    allowed = {"actions": [], "menus": []}
    for permission in permission_list:
        action_obj = ActionDao \
            .get_action_by_id_and_status(action_id=permission.action_id, status=1) if permission.action_id else None
        action = ActionSchema().dump(action_obj)

        menu_obj = MenuDao \
            .get_menu_by_id_and_status(menu_id=permission.menu_id, status=1) if permission.menu_id else None
        menu = MenuSchema().dump(menu_obj)

        if action:
            allowed["actions"].append(
                {'action_id': action['action_id'], 'name': action['name'], 'url': action['url']})
        if menu:
            allowed["menus"].append(
                {'menu_id': menu['menu_id'], 'name': menu['name'], 'url': menu['url']})

    return allowed
