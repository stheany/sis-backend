"""
Role routes SIS API.  Used for creating, retrieving and updating application role.
"""
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from application.services.roleService \
    import roles_get, role_post, role_put, role_by_id_get
from application.utils.rbac import rbac

role_route = Blueprint("role_route", __name__, url_prefix="/api/v1/sis")


@role_route.route('/list-role', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def list_role() -> Response:
    """
    Endpoints for listing all the roles.
    :return: JSON representation of a list of roles and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/list-role"""
        return roles_get()


@role_route.route('/create-role', methods=['POST'])
@jwt_required()
@rbac.check_allowed_access
def create_role() -> Response:
    """
    Endpoints for creating new role.
    :return: JSON representation of role and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-role"""
        return role_post()


@role_route.route('/edit-role', methods=['PUT'])
@jwt_required()
@rbac.check_allowed_access
def edit_role() -> Response:
    """
    Endpoints for updating the existing role.
    :return: JSON representation of role and relevant metadata.
    """
    if request.method == "PUT":
        """[PUT] /api/v1/sis/edit-role"""
        return role_put()


@role_route.route('/role-detail-by-id', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def role_detail_by_id() -> Response:
    """
    Endpoints for retrieving the existing role by role id.
    :return: JSON representation of role and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/role-detail-by-id"""
        return role_by_id_get()
