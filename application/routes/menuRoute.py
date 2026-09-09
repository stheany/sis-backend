"""
Menu routes SIS API.  Used for creating, retrieving and updating application menu.
"""
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from application.services.menuService import menus_get, menu_post, menu_put, menu_by_id_get
from application.utils.rbac import rbac

menu_route = Blueprint("menu_route", __name__, url_prefix="/api/v1/sis")


@menu_route.route('/list-menu', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def list_menu() -> Response:
    """
    Endpoints for listing all the menus.
    :return: JSON representation of a list of menus and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/list-menu"""
        return menus_get()


@menu_route.route('/create-menu', methods=['POST'])
@jwt_required()
@rbac.check_allowed_access
def create_menu() -> Response:
    """
    Endpoints for creating new menu.
    :return: JSON representation of menu and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-menu"""
        return menu_post()


@menu_route.route('/edit-menu', methods=['PUT'])
@jwt_required()
@rbac.check_allowed_access
def edit_menu() -> Response:
    """
    Endpoints for updating the existing menu.
    :return: JSON representation of menu and relevant metadata.
    """
    if request.method == "PUT":
        """[PUT] /api/v1/sis/edit-menu"""
        return menu_put()


@menu_route.route('/menu-detail-by-id', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def menu_detail_by_id() -> Response:
    """
    Endpoints for retrieving the existing menu by menu id.
    :return: JSON representation of menu and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/menu-detail-by-id"""
        return menu_by_id_get()
