"""
Settlement status service is used to get the list of settlement status based on settlement id from user request.
There are two types of settlement. They are Flexcube (settle cbs) and Iroha (settle iroha).
"""
import copy

from flask import request, jsonify, Response

from application.dao.settleCbsDao import SettleCbsDao
from application.dao.settleIrohaDao import SettleIrohaDao
from application.dao.statusDao import StatusDao
from application.models.settleCbs import SettleCbs
from application.models.settleIroha import SettleIroha
from application.models.status import Status
from application.schemas.settleCbsSchema import SettleCbsSchema
from application.schemas.settleIrohaSchema import SettleIrohaSchema
from application.utils.responseMessage import get_const, error_response
from application.dao.settleBklvDao import SettleBklvDao
from application.models.settleBklv import SettleBklv
from application.schemas.settleBklvSchema import SettleBklvSchema


def settlements_status_get() -> Response:
    """
    Used to get settlement status from the list of input id and settlement type parameter.
    :return: A list of settlement status.
    """
    body = request.get_json(silent=True) or {}
    settlement_type = request.args.get("settlement_type", None)

    data = []

    if not body:
        return error_response("BAD_REQUEST_400", "Body is required!", 40)

    if not settlement_type:
        return error_response("BAD_REQUEST_400", "No settlement type please specify it!", 9)

    settle_id_list = body.get("id", None)

    if settle_id_list is None:
        return error_response("BAD_REQUEST_400", "id list is required!", 40)

    # Support single integer input: { "id": 1 }
    if isinstance(settle_id_list, int):
        settle_id_list = [settle_id_list]

    # Reject invalid type
    if not isinstance(settle_id_list, list):
        return error_response("BAD_REQUEST_400", "id must be an integer or list of integers!", 40)

    if not settle_id_list:
        return error_response("BAD_REQUEST_400", "id list cannot be empty!", 40)

    # Validate each id
    for settle_id in settle_id_list:
        if not isinstance(settle_id, int):
            return error_response("BAD_REQUEST_400", "each id must be an integer!", 40)

    if settlement_type == "flexcube":
        for settle_id in settle_id_list:
            # get settle cbs object by cbs settle id
            settle_cbs_obj: SettleCbs = SettleCbsDao.get_settle_cbs_by_id(settle_cbs_id=settle_id)

            # check if settle cbs object exist
            if not settle_cbs_obj:
                return error_response(
                    "BAD_REQUEST_400",
                    f"flexcube settlement id {settle_id} not found!",
                    40
                )

            serialize_settle_cbs_obj = SettleCbsSchema().dump(settle_cbs_obj)

            # get status object by id (cbs settle status id)
            status_obj: Status = StatusDao.get_status_by_id(
                status_id=serialize_settle_cbs_obj['settlement_status_id']
            )

            data_obj = {
                "id": settle_id,
                "settlementStatus": status_obj.status_name,
            }
            data.append(data_obj)

        response = copy.deepcopy(get_const("SUCCESS_200"))
        response["detail"]["data"] = data
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    if settlement_type == "iroha":
        for settle_id in settle_id_list:
            # get settle iroha object by iroha settle id
            settle_iroha_obj: SettleIroha = SettleIrohaDao.get_settle_iroha_by_id(settle_iroha_id=settle_id)

            # check if settle iroha object exist
            if not settle_iroha_obj:
                return error_response(
                    "BAD_REQUEST_400",
                    f"iroha settlement id {settle_id} not found!",
                    40
                )

            serialize_settle_iroha_obj = SettleIrohaSchema().dump(settle_iroha_obj)

            # get status object by id (iroha settle status id)
            status_obj: Status = StatusDao.get_status_by_id(
                status_id=serialize_settle_iroha_obj['settlement_status_id']
            )

            data_obj = {
                "id": settle_id,
                "settlementStatus": status_obj.status_name,
            }
            data.append(data_obj)

        response = copy.deepcopy(get_const("SUCCESS_200"))
        response["detail"]["data"] = data
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    if settlement_type == "bklv":
        for settle_id in settle_id_list:
            # get settle bklv object by bklv settle id
            settle_bklv_obj: SettleBklv = SettleBklvDao.get_settle_bklv_by_id(settle_bklv_id=settle_id)

            # check if settle bklv object exist
            if not settle_bklv_obj:
                return error_response(
                    "BAD_REQUEST_400",
                    f"bklv settlement id {settle_id} not found!",
                    40
                )

            serialize_settle_bklv_obj = SettleBklvSchema().dump(settle_bklv_obj)

            # get status object by id (bklv settle status id)
            status_obj: Status = StatusDao.get_status_by_id(
                status_id=serialize_settle_bklv_obj['settlement_status_id']
            )

            data_obj = {
                "id": settle_id,
                "settlementStatus": status_obj.status_name,
            }
            data.append(data_obj)

        response = copy.deepcopy(get_const("SUCCESS_200"))
        response["detail"]["data"] = data
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    # Invalid settlement type 
    response = copy.deepcopy(get_const("BAD_REQUEST_400"))
    response["detail"]["error_message"] = "Invalid settlement type!"
    response["detail"]["error_code"] = 8
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify
