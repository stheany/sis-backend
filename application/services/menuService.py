"""
Menu services is used for interacting between menu dao and routes.
Actually, it is getting the request from user input and do a logic corresponding to the input.
"""
from email.quoprimime import body_check
import copy
from datetime import datetime

from flask import request, jsonify, Response
from flask_sqlalchemy import Pagination

from application.dao.menuDao import MenuDao
from application.dao.usersLoginSisDao import UsersLoginSisDao
from application.models.menu import Menu
from application.models.usersLoginSis import UsersLoginSis
from application.schemas.menuSchema import MenuSchema
from application.utils.responseMessage import get_const


def menu_post() -> Response:
    """
    Create a new menu.
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}
    name = body.get('name', None)
    description = body.get('description', None)
    created_by = body.get('created_by', None)
    status = body.get('status', None)
    url = body.get('url', None)
    icon = body.get('icon', None)

    # check existed menu name
    existed_menu_name: Menu = MenuDao.get_menu_by_name(name=name)

    if name is None:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_code"] = 26
        response["detail"]["error_message"] = "Menu name is required!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    if existed_menu_name:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_code"] = 27
        response["detail"]["error_message"] = "Menu name already exist!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    # check no updated by id
    if created_by is None:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_code"] = 28
        response["detail"]["error_message"] = "Please specify created by id!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    # check existed menu that created by user id
    user_obj: UsersLoginSis = UsersLoginSisDao.get_user_login_sis_by_id(
        users_login_sis_id=created_by)

    if user_obj:
        menu_obj: Menu = Menu({
            'name': name,
            'description': description,
            'status': status,
            'url': url,
            'icon': icon,
            'created_by': created_by,
            'created_at': datetime.now(),
        })

        check_success = MenuDao.add_menu(menu_obj)
        if check_success:
            response = copy.deepcopy(get_const('SUCCESS_200'))
            response_jsonify = jsonify(response)
            response_jsonify.status_code = response['http_code']
            return response_jsonify
        else:
            response = copy.deepcopy(get_const('BAD_REQUEST_400'))
            response_jsonify = jsonify(response)
            response_jsonify.status_code = response['http_code']
            return response_jsonify
    else:
        response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
        response["detail"]["error_code"] = 29
        response["detail"]["error_message"] = "Created by user not found!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify


def menu_put() -> Response:
    """
    Update the existing menu by menu id from request body.
    :return: A response as json object for the PUT API request.
    """
    body = request.get_json(silent=True) or {}
    menu_id = request.args.get("menu_id",type=int)   
    name = body.get('name', None)
    description = body.get('description', None)
    updated_by = body.get('updated_by', None)
    status = body.get('status', None)
    url = body.get('url', None)
    icon = body.get('icon', None)
    current_datetime = datetime.now()

    if not body:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_code"] = 29
        response["detail"]["error_message"] = "Request body is required!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify 

    if updated_by is None:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_code"] = 29
        response["detail"]["error_message"] = "Please specify updated by id!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    if menu_id == "" or menu_id is None:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_code"] = 29
        response["detail"]["error_message"] = "No menu id please specify it!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    menu_obj: Menu = MenuDao.get_menu_by_id(menu_id=int(menu_id))
    if not menu_obj:
        response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
        response["detail"]["error_code"] = 30
        response["detail"]["error_message"] = f"Menu with id: {menu_id} not found!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    user_obj = UsersLoginSisDao.get_user_login_sis_by_id(
        users_login_sis_id=updated_by)
    if not user_obj:
        response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
        response["detail"]["error_code"] = 31
        response["detail"]["error_message"] = f"User with id: {updated_by} not found!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    menu_obj.name = name
    menu_obj.description = description
    menu_obj.updated_at = current_datetime
    menu_obj.updated_by = updated_by
    menu_obj.status = status
    menu_obj.url = url
    menu_obj.icon = icon
    MenuDao.update_menu(menu_id=int(menu_id), menu=menu_obj)

    response = copy.deepcopy(get_const("SUCCESS_200"))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify


def menus_get() -> Response:
    """
    Retrieve all the menus from the database by using query parameters.
    :return: A response as json object for the GET API request.
    """
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=5, type=int)
    order_by = request.args.get("orderBy", default=Menu.menu_id)
    order_method = request.args.get("orderMethod", default="asc")

    all_menus: list = MenuDao.get_menus(page=(page - 1),
                                        size=size,
                                        order_by=order_by,
                                        order_method=order_method)
    response = copy.deepcopy(get_const("SUCCESS_200"))
    response['detail']['data'] = MenuSchema(many=True).dump(all_menus)
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify


def menu_by_id_get() -> Response:
    """
    Retrieve the menu based on menu id from request
    :return: A response as json object for the GET API request.
    """
    menu_id = request.args.get("menu_id", type=str)
    if menu_id == "" or menu_id is None:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_code"] = 29
        response["detail"]["error_message"] = "No menu id please specify it!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    menu_obj: Menu = MenuDao.get_menu_by_id(menu_id=int(menu_id))

    if not menu_obj:
        response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
        response["detail"]["error_code"] = 30
        response["detail"]["error_message"] = f"Menu with id: {menu_id} not found!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    response = copy.deepcopy(get_const("SUCCESS_200"))
    response["detail"]["data"] = MenuSchema().dump(menu_obj)
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify
