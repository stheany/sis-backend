"""
Environment routes SIS API.  Used for creating, retrieving and updating application environment.
"""
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from application.services.environmentService \
    import environments_get, environment_post, environment_put, environment_by_id_get
from application.utils.rbac import rbac

environment_route = Blueprint("environment_route", __name__, url_prefix="/api/v1/sis")


@environment_route.route('/list-environment', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def list_environment() -> Response:
    """
    Endpoints for listing all the environments.
    :return: JSON representation of a list of environments and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/list-environment"""
        return environments_get()


@environment_route.route('/create-environment', methods=['POST'])
@jwt_required()
@rbac.check_allowed_access
def create_environment() -> Response:
    """
    Endpoints for creating new environment.
    :return: JSON representation of environment and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-environment"""
        return environment_post()


@environment_route.route('/edit-environment', methods=['PUT'])
@jwt_required()
@rbac.check_allowed_access
def edit_environment() -> Response:
    """
    Endpoints for updating the existing environment.
    :return: JSON representation of environment and relevant metadata.
    """
    if request.method == "PUT":
        """[PUT] /api/v1/sis/edit-environment"""
        return environment_put()


@environment_route.route('/environment-detail-by-id', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def environment_detail_by_id() -> Response:
    """
    Endpoints for retrieving the existing environment by environment id.
    :return: JSON representation of environment and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/environment-detail-by-id"""
        return environment_by_id_get()
