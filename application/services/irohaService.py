"""
Iroha services is used for interacting between iroha dao and routes.
Actually, it is getting the request from user input and do a logic corresponding to the input.
"""
import copy

from datetime import datetime

from flask import request, jsonify, Response

from application.dao.irohaDao import IrohaDao
from application.models.iroha import Iroha
from application.schemas.irohaSchema import IrohaSchema
from application.utils.responseMessage import get_const, error_response


def iroha_post() -> Response:
    """
    Create a new iroha.
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}

    if not body:
        return error_response("BAD_REQUEST_400", "No request body!", 40)

    environment_id = body.get("environment_id", None)
    created_by = body.get("created_by", None)
    _ip = body.get("ip", None)
    port = body.get("port", None)
    account_id = body.get("account_id", None)

    if not environment_id:
        return error_response("BAD_REQUEST_400", "Environment ID is required!", 40)

    if not created_by:
        return error_response("BAD_REQUEST_400", "Created By is required!", 40)

    if not _ip:
        return error_response("BAD_REQUEST_400", "Iroha IP address is required!", 40)

    iroha_obj: Iroha = Iroha({
        'environment_id': environment_id,
        'created_at': datetime.now(),
        'created_by': created_by,
        'ip': _ip,
        'port': port,
        'account_id': account_id
    })
    check_success = IrohaDao.add_iroha(iroha_obj)
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


def iroha_put() -> Response:
    """
    Update the existing iroha by iroha id from request body.
    :return: A response as json object for the PUT API request.
    """
    iroha_id = request.args.get("iroha_id", None)

    if not iroha_id:
        return error_response("BAD_REQUEST_400", "No Iroha ID parameter!", 35)

    try:
        iroha_id = int(iroha_id)
    except ValueError:
        return error_response("BAD_REQUEST_400", "Iroha ID must be an integer!", 35)

    body = request.get_json(silent=True) or {}
    environment_id = body.get("environment_id", None)
    updated_by = body.get("updated_by", None)
    _ip = body.get("ip", None)
    port = body.get("port", None)
    account_id = body.get("account_id", None)

    if not updated_by:
        return error_response("BAD_REQUEST_400", "No Updated By parameter!", 36)

    iroha_obj: Iroha = IrohaDao.get_iroha_by_id(iroha_id=iroha_id)

    if not iroha_obj:
        return error_response("NOT_FOUND_HANDLER_404", "Iroha not found!", 34)

    iroha_obj.environment_id = environment_id
    iroha_obj.updated_at = datetime.now()
    iroha_obj.updated_by = updated_by
    iroha_obj.ip = _ip
    iroha_obj.port = port
    iroha_obj.account_id = account_id

    IrohaDao.update_iroha(iroha_id=iroha_id, iroha=iroha_obj)

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify


def irohas_get() -> Response:
    """
    Retrieve all the irohas from the database by using query parameters.
    :return: A response as json object for the GET API request.
    """
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=10, type=int)
    order_by = request.args.get("orderBy", default=Iroha.iroha_id)
    order_method = request.args.get("orderMethod", default="asc")

    all_irohas: list = IrohaDao.get_irohas(page=page,
                                           size=size,
                                           order_by=order_by,
                                           order_method=order_method)

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response['detail']['data'] = IrohaSchema(many=True).dump(all_irohas)
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify


def iroha_by_id_get() -> Response:
    """
    Retrieve the iroha based on iroha id from request
    :return: A response as json object for the GET API request.
    """
    iroha_id = request.args.get("iroha_id")

    if not iroha_id:
        return error_response("BAD_REQUEST_400", "No Iroha ID parameter!", 35)

    try:
        iroha_id = int(iroha_id)
    except ValueError:
        return error_response("BAD_REQUEST_400", "Iroha ID must be an integer!", 35)

    iroha_obj: Iroha = IrohaDao.get_iroha_by_id(iroha_id=iroha_id)

    if not iroha_obj:
        return error_response("NOT_FOUND_HANDLER_404", "Iroha not found!", 34)

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response['detail']['data'] = IrohaSchema().dump(iroha_obj)
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify
