import copy
import logging
from datetime import datetime
import json

from flask import request, jsonify, Response
from flask_jwt_extended import get_jwt_identity

from application import celery, db
from application.dao.systemDao import SystemDao
from application.models.settleIroha import SettleIroha
from application.models.settlementIrohaContentDetail import SettlementIrohaContentDetail
from application.models.system import System
from application.utils.responseMessage import get_const, error_response

SETTLE_STATUS_PENDING = (1, 'PENDING')
SETTLE_STATUS_SUCCESS = (2, 'SUCCESS')
SETTLE_STATUS_FAIL = (3, 'FAIL')
SETTLE_STATUS_ERROR = (4, 'ERROR')
SETTLE_STATUS_COMMITTED = (5, 'COMMITTED')
SETTLE_STATUS_REJECTED = (6, 'REJECTED')
SETTLE_STATUS_STATELESS_VALIDATION_FAILED = (7, 'STATELESS_VALIDATION_FAILED')


# create iroha settlement
def settle_iroha_post() -> Response:
    body = request.get_json(silent=True) or {}

    if not body:
        return error_response("BAD_REQUEST_400", "No request body!", 40)

    reference_id = body.get("reference_id")
    settlement_iroha_content = body.get("settlementContent")

    if reference_id is None:
        return error_response("BAD_REQUEST_400", "reference_id is required!", 40)

    try:
        reference_id = int(reference_id)
    except (TypeError, ValueError):
        return error_response("BAD_REQUEST_400", "reference_id must be numeric!", 40)

    if not isinstance(settlement_iroha_content, dict):
        return error_response("BAD_REQUEST_400", "settlementContent must be an object!", 40)

    required_fields = [
        "currencyCode",
        "senderAccountId",
        "receiverAccountId",
        "amount",
        "description"
    ]

    for field in required_fields:
        if field not in settlement_iroha_content:
            return error_response("BAD_REQUEST_400", f"{field} is required in settlementContent!", 40)

    system_id = get_jwt_identity()

    settle_iroha_obj = SettleIroha({
        'system_id': system_id,
        'reference_id': reference_id,
        'settlement_iroha_content': json.dumps(settlement_iroha_content),
        'settlement_status_id': SETTLE_STATUS_PENDING[0],
        'created_at': datetime.now()
    })

    try:
        db.session.add(settle_iroha_obj)
        db.session.flush()

        settle_iroha_id = settle_iroha_obj.settle_iroha_id
        created_at = settle_iroha_obj.created_at

        db.session.add(SettlementIrohaContentDetail({
            'settle_iroha_id': settle_iroha_id,
            'currency_code': settlement_iroha_content['currencyCode'],
            'sender_account_id': settlement_iroha_content['senderAccountId'],
            'receiver_account_id': settlement_iroha_content['receiverAccountId'],
            'amount': settlement_iroha_content['amount'],
            'description': settlement_iroha_content['description'],
            'iroha_id': 1
        }))

        db.session.commit()

    except Exception:
        db.session.rollback()
        logging.getLogger(__name__).exception("Iroha settlement create failed")
        response = copy.deepcopy(get_const('SERVER_ERROR_500'))
        response['detail']['error_message'] = "An internal error occurred."
        response['detail']['error_code'] = 7
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response['http_code']
        return response_jsonify
    finally:
        db.session.close()

    try:
        system_obj = SystemDao.get_system_by_id(system_id=system_id)
        send_task_iroha(system_obj.url, settle_iroha_id, settlement_iroha_content)
    except Exception:
        logging.getLogger(__name__).exception("Failed to send task to iroha")

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response['detail']['data'] = {
        "id": settle_iroha_id,
        "settlement_status": SETTLE_STATUS_PENDING[1],
        "created_at": created_at.strftime("%d-%m-%Y %H:%M:%S")
    }
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify


def send_task_iroha(system_url, settle_iroha_id, settlement_iroha_detail):
    """
    Forward iroha task in the background
    :param system_url: System url
    :param settle_iroha_id: Iroha Settle ID
    :param settlement_iroha_detail:  Iroha settlement content details
    :return: A celery task object
    """
    result = celery.send_task('worker.tasks.send_to_iroha', kwargs={
        'settle_iroha_id': settle_iroha_id,
        'settlement_iroha_detail': settlement_iroha_detail
    })

    return result
