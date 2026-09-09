"""
System services is used for interacting between system dao and routes.
Actually, it is getting the request from user input and do a logic corresponding to the input.
"""
from datetime import datetime

from flask import request, jsonify, Response

from application.dao.systemDao import SystemDao
from application.models.system import System
from application.schemas.systemSchema import SystemSchema
from application.utils.responseMessage import get_const, error_response

_UNIQUE_FIELD_CHECKS = (
    ('url', 'get_system_by_url', 42),
    ('ip_address', 'get_system_by_ip_address', 43),
    ('bic_code', 'get_system_by_bic_code', 44),
)

def _find_duplicate_system(values: dict, exclude_system_id: int = None):
    """
    Check url/ip_address/bic_code (whichever were supplied) against existing
    systems. Returns an error Response if any collide with a DIFFERENT
    system, else None.
    """
    for field, lookup_name, error_code in _UNIQUE_FIELD_CHECKS:
        value = values.get(field)
        if not value:
            continue
        owner: System = getattr(SystemDao, lookup_name)(value)
        if owner and owner.system_id != exclude_system_id:
            return error_response(
                "BAD_REQUEST_400",
                f"A system with {field} '{value}' already exists.",
                error_code
            )
    return None

def system_post() -> Response:
    """
    Create a new system.
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}

    if not body:
        return error_response("BAD_REQUEST_400", "Request body is required.", 40)

    system_name = body.get("system_name", None)
    short_name = body.get("short_name", None)
    bic_code = body.get("bic_code", None)
    settlement_account_number = body.get("settlement_account_number", None)
    url = body.get("url", None)
    ip_address = body.get("ip_address", None)
    created_by = body.get("created_by", None)
    status = body.get("status", None)

    if not system_name:
        return error_response("BAD_REQUEST_400", "system_name is required.", 40)

    duplicate_response = _find_duplicate_system({
        'url': url, 'ip_address': ip_address, 'bic_code': bic_code
    })
    if duplicate_response:
        return duplicate_response

    system_obj: System = System({
        'system_name': system_name,
        'short_name': short_name,
        'bic_code': bic_code,
        'settlement_account_number': settlement_account_number,
        'status': status,
        'url': url,
        'ip_address': ip_address,
        'created_by': created_by,
        'created_at': datetime.now()
    })
    check_success = SystemDao.add_system(system_obj)
    if check_success:
        response = get_const('SUCCESS_200')
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response['http_code']
        return response_jsonify
    else:
        return error_response("BAD_REQUEST_400", "Failed to create system.", 41)


def system_put() -> Response:
    """
    Update the existing system by system id from request body.
    :return: A response as json object for the PUT API request.
    """
    system_id = request.args.get("system_id", type=str)
    body = request.get_json(silent=True) or {}

    if system_id is None or system_id == "":
        return error_response("BAD_REQUEST_400", "No system id — please specify it!", 18)

    try:
        system_id_int = int(system_id)
    except ValueError:
        return error_response("BAD_REQUEST_400", "system_id must be a valid integer.", 18)

    if not body:
        return error_response("BAD_REQUEST_400", "Request body is required.", 40)

    system_name = body.get("system_name", None)
    short_name = body.get("short_name", None)
    bic_code = body.get("bic_code", None)
    settlement_account_number = body.get("settlement_account_number", None)
    url = body.get("url", None)
    ip_address = body.get("ip_address", None)
    updated_by = body.get("updated_by", None)
    status = body.get("status", None)

    system_obj: System = SystemDao.get_system_by_id(system_id=system_id_int)

    if not system_obj:
        return error_response("NOT_FOUND_HANDLER_404", f"System with id: {system_id} not found!", 19)

    duplicate_response = _find_duplicate_system(
        {'url': url, 'ip_address': ip_address, 'bic_code': bic_code},
        exclude_system_id=system_id_int
    )
    if duplicate_response:
        return duplicate_response

    system_obj.system_name = system_name
    system_obj.short_name = short_name
    system_obj.bic_code = bic_code
    system_obj.settlement_account_number = settlement_account_number
    system_obj.url = url
    system_obj.ip_address = ip_address
    system_obj.updated_by = updated_by
    system_obj.updated_at = datetime.now()
    system_obj.status = status
    SystemDao.update_system(system_id=system_id_int, system=system_obj)

    response = get_const("SUCCESS_200")
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify


def systems_get() -> Response:
    """
    Retrieve all the systems from the database by using query parameters.
    :return: A response as json object for the GET API request.
    """
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=10, type=int)
    order_by = request.args.get("orderBy", default=System.system_id)
    order_method = request.args.get("orderMethod", default="asc")

    response = get_const('SUCCESS_200')
    response['detail']['data'] = SystemSchema(many=True) \
        .dump(SystemDao.get_systems(page=page,
                                    size=size,
                                    order_by=order_by,
                                    order_method=order_method))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify


def system_by_id_get():
    """
    Retrieve the system based on system id from request
    :return: A response as json object for the GET API request.
    """
    system_id = request.args.get("system_id", type=str)

    if system_id is None or system_id == "":
        return error_response("BAD_REQUEST_400", "No system id — please specify it!", 18)

    try:
        system_id_int = int(system_id)
    except ValueError:
        return error_response("BAD_REQUEST_400", "system_id must be a valid integer.", 18)

    system_obj: System = SystemDao.get_system_by_id(system_id=system_id_int)

    if not system_obj:
        return error_response("NOT_FOUND_HANDLER_404", f"System with id: {system_id} not found!", 19)

    response = get_const("SUCCESS_200")
    response["detail"]["data"] = SystemSchema().dump(system_obj)
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify
