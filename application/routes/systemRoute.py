"""
System routes SIS API.  Used for creating, retrieving and updating application system.
"""
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from application.services.systemLoginSisService import create_system_user_post, edit_system_user_put
from application.services.systemService import system_by_id_get, systems_get, system_put, system_post
from application.utils.rbac import rbac

system_route = Blueprint("system_route", __name__, url_prefix="/api/v1/sis")


@system_route.route('/list-system', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def list_system() -> Response:
    """
    Endpoints for listing all the systems.
    :return: JSON representation of a list of systems and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/list-system"""
        return systems_get()


@system_route.route('/create-system', methods=['POST'])
@jwt_required()
@rbac.check_allowed_access
def create_system() -> Response:
    """
    Endpoints for creating new system.
    :return: JSON representation of system and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-system"""
        return system_post()


@system_route.route('/edit-system', methods=['PUT'])
@jwt_required()
@rbac.check_allowed_access
def edit_system() -> Response:
    """
    Endpoints for updating the existing system.
    :return: JSON representation of system and relevant metadata.
    """
    if request.method == "PUT":
        """[PUT] /api/v1/sis/edit-system"""
        return system_put()


@system_route.route('/system-detail-by-id', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def system_detail_by_id() -> Response:
    """
    Endpoints for retrieving the existing system by system id.
    :return: JSON representation of system and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/system-detail-by-id"""
        return system_by_id_get()


@system_route.route('/create-system-user', methods=['POST'])
@jwt_required()
@rbac.check_allowed_access
def create_system_user():
    """
    Endpoints for creating new system login sis user.
    :return: JSON representation of system and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-system-user"""
        return create_system_user_post()


@system_route.route('/edit-system-user', methods=['PUT'])
@jwt_required()
@rbac.check_allowed_access
def edit_system_user():
    """
    Endpoints for updating the existing system user that login to sis.
    :return: JSON representation of system and relevant metadata.
    """
    if request.method == "PUT":
        """[PUT] /api/v1/sis/edit-system-user"""
        return edit_system_user_put()
