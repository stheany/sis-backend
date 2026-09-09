"""
Permission routes SIS API.  Used for creating, retrieving and updating application permission.
"""
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from application.services.permissionService import permission_post, permission_put
from application.utils.rbac import rbac

permission_route = Blueprint("permission_route", __name__, url_prefix="/api/v1/sis")


@permission_route.route('/create-permission', methods=['POST'])
@jwt_required()
@rbac.check_allowed_access
def create_permission() -> Response:
    """
    Endpoints for creating new permission.
    :return: JSON representation of permission and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-permission"""
        return permission_post()


@permission_route.route('/edit-permission', methods=['PUT'])
@jwt_required()
@rbac.check_allowed_access
def edit_permission() -> Response:
    """
    Endpoints for updating the existing permission.
    :return: JSON representation of permission and relevant metadata.
    """
    if request.method == "PUT":
        """[PUT] /api/v1/sis/edit-permission"""
        return permission_put()
