"""
Action routes SIS API.  Used for creating, retrieving and updating application action.
"""
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from application.services.actionService import actions_get, action_post, action_put, action_by_id_get
from application.utils.rbac import rbac

action_route = Blueprint("action_route", __name__, url_prefix="/api/v1/sis")


@action_route.route('/list-action', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def list_action() -> Response:
    """
    Endpoints for listing all the actions.
    :return: JSON representation of a list of actions and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/list-action"""
        return actions_get()


@action_route.route('/create-action', methods=['POST'])
@jwt_required()
@rbac.check_allowed_access
def create_action() -> Response:
    """
    Endpoints for creating new action.
    :return: JSON representation of action and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-action"""
        return action_post()


@action_route.route('/edit-action', methods=['PUT'])
@jwt_required()
@rbac.check_allowed_access
def edit_action() -> Response:
    """
    Endpoints for updating the existing action.
    :return: JSON representation of action and relevant metadata.
    """
    if request.method == "PUT":
        """[PUT] /api/v1/sis/edit-action"""
        return action_put()


@action_route.route('/action-detail-by-id', methods=['GET'])
@jwt_required()
@rbac.check_allowed_access
def action_detail_by_id() -> Response:
    """
    Endpoints for retrieving the existing action by action id.
    :return: JSON representation of action and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/action-detail-by-id"""
        return action_by_id_get()
