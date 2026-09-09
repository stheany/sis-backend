"""
Flexcube services is used for interacting between flexcube dao and routes.
Actually, it is getting the request from user input and do a logic corresponding to the input.
"""
import copy
import logging
import os
from datetime import datetime

import cx_Oracle
from flask import jsonify, request, Response

from application.dao.flexcubeDao import FlexcubeDao
from application.models.flexcube import Flexcube
from application.schemas.flexcubeSchema import FlexcubeSchema
from application.utils.responseMessage import get_const, error_response
from application.utils.password_utils import hash_password

from xml.etree.ElementTree import Element, SubElement, tostring  # safe XML

RESPONSE_TYPE_XML = (1, 'xml')
RESPONSE_TYPE_JSON = (2, 'json')


def flexcube_post() -> Response:
    """
    Create a new flexcube based on request body.
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}

    username = body.get("username", None)
    password = body.get("password", None)
    environment_id = body.get("environment_id", None)
    flexcube_url = body.get("flexcube_url", None)

    source = body.get("source", None)
    ubscomp = body.get("ubscomp", None)
    user_id = body.get("user_id", None)
    branch = body.get("branch", None)
    module_id = body.get("module_id", None)
    service = body.get("service", None)
    created_by = body.get("created_by", None)

    if not body:
        return error_response("BAD_REQUEST_400", "body is required!", 40)

    if not username:
        return error_response("BAD_REQUEST_400", "Flexcube username is required!", 40)

    if not password:
        return error_response("BAD_REQUEST_400", "Flexcube password is required!", 40)

    if not environment_id:
        return error_response("BAD_REQUEST_400", "Flexcube environment id is required!", 40)

    if not flexcube_url:
        return error_response("BAD_REQUEST_400", "Flexcube url is required!", 40)

    if len(password) < 8:
        return error_response("BAD_REQUEST_400", "Flexcube password must be at least 8 characters!", 40)    

    encrypt_password = hash_password(password) if password else None

    flexcube_obj: Flexcube = Flexcube({
        'username': username,
        'password': encrypt_password,
        'environment_id': environment_id,
        'flexcube_url': flexcube_url,
        'source': source,
        'ubscomp': ubscomp,
        'user_id': user_id,
        'branch': branch,
        'module_id': module_id,
        'service': service,
        'created_by': created_by,
        'created_at': datetime.now()
    })
    check_success = FlexcubeDao.add_flexcube(flexcube_obj)
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


def flexcube_put() -> Response:
    """
    Update the existing flexcube by flexcube id from request body.
    :return: A response as json object for the PUT API request.
    """
    flexcube_id = request.args.get("flexcube_id", type=str)

    if not flexcube_id:
        return error_response("BAD_REQUEST_400", "No flexcube id please specify it!", 25)

    try:
        flexcube_id = int(flexcube_id)
    except ValueError:
        return error_response("BAD_REQUEST_400", "Flexcube id must be an integer!", 26)

    body = request.get_json(silent=True) or {}

    if not body: 
        return error_response("BAD_REQUEST_400", "body is required!", 40)

    username = body.get("username", None)
    password = body.get("password", None)
    environment_id = body.get("environment_id", None)
    flexcube_url = body.get("flexcube_url", None)
    source = body.get("source", None)
    ubscomp = body.get("ubscomp", None)
    user_id = body.get("user_id", None)
    branch = body.get("branch", None)
    module_id = body.get("module_id", None)
    service = body.get("service", None)
    updated_by = body.get("updated_by", None)
    encrypt_password = hash_password(password) if password else None

    flexcube_obj: Flexcube = FlexcubeDao.get_flexcube_by_id(flexcube_id=flexcube_id)

    if not flexcube_obj:
        return error_response("NOT_FOUND_HANDLER_404", f"Flexcube with id: {flexcube_id} not found!", 27)

    flexcube_obj.username = username
    flexcube_obj.password = encrypt_password if encrypt_password else flexcube_obj.password
    flexcube_obj.environment_id = environment_id
    flexcube_obj.flexcube_url = flexcube_url
    flexcube_obj.source = source
    flexcube_obj.ubscomp = ubscomp
    flexcube_obj.user_id = user_id
    flexcube_obj.branch = branch
    flexcube_obj.module_id = module_id
    flexcube_obj.service = service
    flexcube_obj.updated_by = updated_by
    flexcube_obj.updated_at = datetime.now()
    FlexcubeDao.update_flexcube(flexcube_id=flexcube_id, flexcube=flexcube_obj)

    response = copy.deepcopy(get_const("SUCCESS_200"))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify


def flexcubes_get() -> Response:
    """
    Retrieve all the flexcubes from the database by using query parameters.
    :return: A response as json object for the GET API request.
    """
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=10, type=int)
    order_by = request.args.get("orderBy", default=Flexcube.flexcube_id)
    order_method = request.args.get("orderMethod", default="asc")

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response['detail']['data'] = FlexcubeSchema(many=True) \
        .dump(FlexcubeDao.get_flexcubes(page=page,
                                        size=size,
                                        order_by=order_by,
                                        order_method=order_method))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify


def flexcube_by_id_get() -> Response:
    """
    Retrieve the flexcube based on flexcube id from request
    :return: A response as json object for the GET API request.
    """
    flexcube_id = request.args.get("flexcube_id", type=str)

    if not flexcube_id:
        return error_response("BAD_REQUEST_400", "No flexcube id please specify it!", 25)

    try:
        flexcube_id = int(flexcube_id)
    except ValueError:
        return error_response("BAD_REQUEST_400", "Flexcube id must be an integer!", 26)

    flexcube_obj: Flexcube = FlexcubeDao.get_flexcube_by_id(flexcube_id=flexcube_id)

    if not flexcube_obj:
        return error_response("NOT_FOUND_HANDLER_404", f"Flexcube with id: {flexcube_id} not found!", 27)

    response = copy.deepcopy(get_const("SUCCESS_200"))
    response["detail"]["data"] = FlexcubeSchema().dump(flexcube_obj)
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify


def flexcube_date_get():
    """
    Service layer to fetch Flexcube business date from external Oracle DB.
    Handles errors and formats the API response.
    """
    try:
        flexcube_date = FlexcubeDao.get_external_flexcube_date()

        if not flexcube_date:
            response = copy.deepcopy(get_const('SERVER_ERROR_500'))
            response['detail']["error_message"] = "No date returned from Flexcube"
        else:
            response = copy.deepcopy(get_const('SUCCESS_200'))
            response['detail']["data"] = {"flexcube_date": flexcube_date}

    except Exception as e:
        logging.getLogger(__name__).exception("flexcube_date_get failed")
        response = copy.deepcopy(get_const('SERVER_ERROR_500'))
        response['detail']["error_message"] = "An internal error occurred."

    response_json = jsonify(response)
    response_json.status_code = response["http_code"]
    return response_json


def flexcube_account_balance_get() -> Response:
    """
    Retrieve Flexcube account balances with safe filtering, sorting, and pagination.
    Returns JSON by default; `response_type=xml` for XML output.
    """
    response_type = (request.args.get("response_type") or "json").strip().lower()
    if response_type not in {"json", "xml"}:
        resp = copy.deepcopy(get_const("BAD_REQUEST_400"))
        resp["detail"]["error_code"] = 6
        resp["detail"]["error_message"] = "Invalid response type (use json or xml)"
        out = jsonify(resp)
        out.status_code = resp["http_code"]
        return out

    ccy = request.args.get("ccy")
    customer_ac = request.args.get("customerAccountNumber")
    account_class = request.args.get("accountClass")
    branch_code = request.args.get("branchCode")
    order_by = request.args.get("orderBy")
    order_method = request.args.get("orderMethod")
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 10))
    except ValueError:
        page, size = 1, 10

    try:
        rows = FlexcubeDao.fetch_account_balances(
            ccy=ccy,
            customer_account_number=customer_ac,
            account_class=account_class,
            branch_code=branch_code,
            order_by=order_by,
            order_method=order_method,
            page=page,
            size=size,
        )
    except ValueError:
        resp = copy.deepcopy(get_const("BAD_REQUEST_400"))
        resp["detail"]["error_code"] = 6
        resp["detail"]["error_message"] = "Invalid query parameter."
        out = jsonify(resp)
        out.status_code = resp["http_code"]
        return out
    except Exception as e:
        logging.getLogger(__name__).exception("flexcube_account_balance_get failed")
        resp = copy.deepcopy(get_const("SERVER_ERROR_500"))
        resp["detail"]["error_code"] = 5
        resp["detail"]["error_message"] = "An internal error occurred."
        out = jsonify(resp)
        out.status_code = resp["http_code"]
        return out

    if response_type == "json":
        data = [
            {
                "branchCode": r[0],
                "customerAccountNumber": r[1],
                "accountDescription": r[2],
                "ccy": r[3],
                "accountClass": r[4],
                "availableBalance": r[5],
                "currentBalance": r[6],
            }
            for r in rows
        ]
        resp = copy.deepcopy(get_const("SUCCESS_200"))
        resp["detail"]["data"] = data
        out = jsonify(resp)
        out.status_code = resp["http_code"]
        return out

    # response_type == "xml" (use ElementTree to escape safely)
    root = Element("DATA")
    for r in rows:
        cur_acc = SubElement(root, "CUR_ACC")
        SubElement(cur_acc, "BRANCH_CODE").text = str(r[0])
        SubElement(cur_acc, "CUSTOMER_ACCOUNT_NUMBER").text = str(r[1])
        SubElement(cur_acc, "ACCOUNT_DESCRIPTION").text = str(r[2])
        SubElement(cur_acc, "CCY").text = str(r[3])
        SubElement(cur_acc, "ACCOUNT_CLASS").text = str(r[4])
        SubElement(cur_acc, "AVAILABLE_BALANCE").text = str(r[5])
        SubElement(cur_acc, "CURRENT_BALANCE").text = str(r[6])

    xml_bytes = tostring(root, encoding="utf-8", xml_declaration=True)
    return Response(xml_bytes, mimetype="application/xml")