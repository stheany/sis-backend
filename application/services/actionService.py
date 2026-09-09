"""
Action services is used for interacting between action dao and routes.
Actually, it is getting the request from user input and do a logic corresponding to the input.
"""
from datetime import datetime

from flask import request, jsonify, Response

from application.dao.actionDao import ActionDao
from application.models.action import Action
from application.schemas.actionSchema import ActionSchema
from application.utils.responseMessage import get_const, error_response


def action_post() -> Response:
    """
    Create a new action.
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}

    if not body:
        return error_response("BAD_REQUEST_400", "Request body is required.", 40)

    name = body.get("name", None)
    description = body.get("description", None)
    created_by = body.get("created_by", None)
    status = body.get("status", None)

    if not name:
        return error_response("BAD_REQUEST_400", "Action name is required.", 40)

    action_obj: Action = Action({
        'name': name,
        'description': description,
        'created_by': created_by,
        'created_at': datetime.now(),
        'status': status
    })
    check_success = ActionDao.add_action(action_obj)
    if check_success:
        response = get_const('SUCCESS_200')
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response['http_code']
        return response_jsonify
    else:
        return error_response("BAD_REQUEST_400", "Failed to create action.", 41)


def action_put() -> Response:
    """
    Update the existing action by action id from request body.
    :return: A response as json object for the PUT API request.
    """
    action_id = request.args.get("action_id", type=str)
    body = request.get_json(silent=True) or {}

    if action_id is None or action_id == "":
        return error_response("BAD_REQUEST_400", "No action id — please specify it!", 16)

    try:
        action_id_int = int(action_id)
    except ValueError:
        return error_response("BAD_REQUEST_400", "action_id must be a valid integer.", 16)

    if not body:
        return error_response("BAD_REQUEST_400", "Request body is required.", 40)

    name = body.get("name", None)
    description = body.get("description", None)
    updated_by = body.get("updated_by", None)
    status = body.get("status", None)

    action_obj: Action = ActionDao.get_action_by_id(action_id=action_id_int)

    if not action_obj:
        return error_response("NOT_FOUND_HANDLER_404", f"Action with id: {action_id} not found!", 17)

    action_obj.name = name
    action_obj.description = description
    action_obj.updated_by = updated_by
    action_obj.updated_at = datetime.now()
    action_obj.status = status
    ActionDao.update_action(action_id=action_id_int, action=action_obj)

    response = get_const("SUCCESS_200")
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify


def actions_get() -> Response:
    """
    Retrieve all the actions from the database by using query parameters.
    :return: A response as json object for the GET API request.
    """
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=10, type=int)
    order_by = request.args.get("orderBy", default=Action.action_id)
    order_method = request.args.get("orderMethod", default="asc")

    response = get_const('SUCCESS_200')
    response['detail']['data'] = ActionSchema(many=True).dump(ActionDao.get_actions(
        page=page, size=size, order_by=order_by, order_method=order_method))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify


def action_by_id_get() -> Response:
    """
    Retrieve the action based on action id from request
    :return: A response as json object for the GET API request.
    """
    action_id = request.args.get("action_id", type=str)

    if action_id is None or action_id == "":
        return error_response("BAD_REQUEST_400", "No action id — please specify it!", 16)

    try:
        action_id_int = int(action_id)
    except ValueError:
        return error_response("BAD_REQUEST_400", "action_id must be a valid integer.", 16)

    action_obj: Action = ActionDao.get_action_by_id(action_id=action_id_int)

    if not action_obj:
        return error_response("NOT_FOUND_HANDLER_404", f"Action with id: {action_id} not found!", 17)

    response = get_const("SUCCESS_200")
    response["detail"]["data"] = ActionSchema().dump(action_obj)
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify
