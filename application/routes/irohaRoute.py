"""
Iroha routes SIS API.  Used for creating, retrieving and updating application iroha.
"""
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from application.services.irohaService \
    import irohas_get, iroha_post, iroha_put, iroha_by_id_get
from application.utils.rbac import rbac

iroha_route = Blueprint("iroha_route", __name__, url_prefix="/api/v1/sis")


@iroha_route.route('/list-iroha', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def list_iroha() -> Response:
    """
    Endpoints for listing all the irohas.
    :return: JSON representation of a list of irohas and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/list-iroha"""
        return irohas_get()


@iroha_route.route('/create-iroha', methods=['POST'])
@jwt_required()
@rbac.check_allowed_access
def create_iroha() -> Response:
    """
    Endpoints for creating new iroha.
    :return: JSON representation of iroha and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-iroha"""
        return iroha_post()


@iroha_route.route('/edit-iroha', methods=['PUT'])
@jwt_required()
@rbac.check_allowed_access
def edit_iroha() -> Response:
    """
    Endpoints for updating the existing iroha.
    :return: JSON representation of iroha and relevant metadata.
    """
    if request.method == "PUT":
        """[PUT] /api/v1/sis/edit-iroha"""
        return iroha_put()


@iroha_route.route('/iroha-detail-by-id', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def iroha_detail_by_id() -> Response:
    """
    Endpoints for retrieving the existing iroha by iroha id.
    :return: JSON representation of iroha and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/iroha-detail-by-id"""
        return iroha_by_id_get()
