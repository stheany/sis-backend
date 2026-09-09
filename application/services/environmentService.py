"""
Environment services is used for interacting between environment dao and routes.
Actually, it is getting the request from user input and do a logic corresponding to the input.
"""
import copy
from datetime import datetime

from flask import request, jsonify, Response

from application.dao.environmentDao import EnvironmentDao
from application.models.environment import Environment
from application.schemas.environmentSchema import EnvironmentSchema
from application.utils.responseMessage import get_const, error_response


def environment_post() -> Response:
    """
    Create a new environment.
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}

    name = body.get("name", None)
    description = body.get("description", None)
    url = body.get("url", None)
    created_by = body.get("created_by", None)

    if not body:
        return error_response("BAD_REQUEST_400", "Body is required!", 40)

    if not name:
        return error_response("BAD_REQUEST_400", "Environment name is required!", 40)

    if not url:
        return error_response("BAD_REQUEST_400", "URL is required!", 40)

    if not created_by:
        return error_response("BAD_REQUEST_400", "Created by is required!", 40)

    environment_obj: Environment = Environment({
        'name': name,
        'description': description,
        'url': url,
        'created_by': created_by,
        'created_at': datetime.now()
    })
    check_success = EnvironmentDao.add_environment(environment_obj)
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


def environment_put() -> Response:
    """
    Update the existing environment by environment id from request body.
    :return: A response as json object for the PUT API request.
    """
    environment_id = request.args.get("env_id", type=str)

    if not environment_id:
        return error_response("BAD_REQUEST_400", "No environment id please specify it!", 23)

    try:
        environment_id = int(environment_id)
    except ValueError:
        return error_response("BAD_REQUEST_400", "Environment id must be an integer!", 24)

    body = request.get_json(silent=True) or {}
    name = body.get("name", None)
    description = body.get("description", None)
    url = body.get("url", None)
    updated_by = body.get("updated_by", None)

    environment_obj: Environment = EnvironmentDao.get_environment_by_id(environment_id)

    if not body:
        return error_response("BAD_REQUEST_400", "Body is required!", 26)

    if not environment_obj:
        return error_response("NOT_FOUND_HANDLER_404", f"Environment with id: {environment_id} not found!", 25)
    
    if not updated_by:
        return error_response("BAD_REQUEST_400", "Updated by is required!", 27)

    environment_obj.name = name
    environment_obj.description = description
    environment_obj.url = url
    environment_obj.updated_by = updated_by
    environment_obj.updated_at = datetime.now()
    EnvironmentDao.update_environment(environment_id=environment_id, environment=environment_obj)

    response = copy.deepcopy(get_const("SUCCESS_200"))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify


def environments_get() -> Response:
    """
    Retrieve all the environments from the database by using query parameters.
    :return: A response as json object for the GET API request.
    """
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=10, type=int)
    order_by = request.args.get("orderBy", default=Environment.env_id)
    order_method = request.args.get("orderMethod", default="asc")

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response['detail']['data'] = EnvironmentSchema(many=True) \
        .dump(EnvironmentDao.get_environments(page=page,
                                              size=size,
                                              order_by=order_by,
                                              order_method=order_method))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify


def environment_by_id_get() -> Response:
    """
    Retrieve the environment based on environment id from request
    :return: A response as json object for the GET API request.
    """
    environment_id = request.args.get("env_id", type=str)

    if not environment_id:
        return error_response("BAD_REQUEST_400", "No environment id please specify it!", 23)

    try:
        environment_id = int(environment_id)
    except ValueError:
        return error_response("BAD_REQUEST_400", "Environment id must be an integer!", 24)

    environment_obj: Environment = EnvironmentDao.get_environment_by_id(environment_id)

    if not environment_obj:
        return error_response("NOT_FOUND_HANDLER_404", f"Environment with id: {environment_id} not found!", 25)

    response = copy.deepcopy(get_const("SUCCESS_200"))
    response["detail"]["data"] = EnvironmentSchema().dump(environment_obj)
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify
