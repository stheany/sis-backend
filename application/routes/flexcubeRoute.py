"""
Flexcube routes SIS API.  Used for creating, retrieving and updating application flexcube.
"""
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from application.services.flexcubeService \
    import flexcubes_get, flexcube_post, flexcube_put, flexcube_by_id_get
from application.utils.rbac import rbac

flexcube_route = Blueprint("flexcube_route", __name__, url_prefix="/api/v1/sis")


@flexcube_route.route('/list-flexcube', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def list_flexcube() -> Response:
    """
    Endpoints for listing all the flexcubes.
    :return: JSON representation of a list of flexcubes and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/list-flexcube"""
        return flexcubes_get()


@flexcube_route.route('/create-flexcube', methods=['POST'])
@jwt_required()
@rbac.check_allowed_access
def create_flexcube() -> Response:
    """
    Endpoints for creating new flexcube.
    :return: JSON representation of flexcube and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-flexcube"""
        return flexcube_post()


@flexcube_route.route('/edit-flexcube', methods=['PUT'])
@jwt_required()
@rbac.check_allowed_access
def edit_flexcube() -> Response:
    """
    Endpoints for updating the existing flexcube.
    :return: JSON representation of flexcube and relevant metadata.
    """
    if request.method == "PUT":
        """[PUT] /api/v1/sis/edit-flexcube"""
        return flexcube_put()


@flexcube_route.route('/flexcube-detail-by-id', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def flexcube_detail_by_id() -> Response:
    """
    Endpoints for retrieving the existing flexcube by flexcube id.
    :return: JSON representation of flexcube and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/flexcube-detail-by-id"""
        return flexcube_by_id_get()
