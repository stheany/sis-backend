import copy
import logging
from datetime import datetime

from flask import request, jsonify, Response
from flask_jwt_extended import get_jwt_identity

from application import celery, db
from application.dao.flexcubeDao import FlexcubeDao
from application.dao.systemDao import SystemDao
from application.models.flexcube import Flexcube
from application.models.settleCbs import SettleCbs
from application.models.settlementCbsContentDetail import SettlementCbsContentDetail
from application.models.system import System
from application.schemas.flexcubeSchema import FlexcubeSchema
from application.utils.responseMessage import get_const

SETTLE_STATUS_PENDING = (1, 'PENDING')
SETTLE_STATUS_SUCCESS = (2, 'SUCCESS')
SETTLE_STATUS_FAIL = (3, 'FAIL')
SETTLE_STATUS_ERROR = (4, 'ERROR')


def settle_cbs_post() -> Response:
    """
    Create a new cbs settlement.
    :return: A response as json object for the POST API request.
    """ 
    response = copy.deepcopy(get_const("GONE_410"))
    response["detail"]["error_code"] = 410
    response["detail"]["error_message"] = "This endpoint is no longer available."
    
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]

    return response_jsonify

    # Logic for creating CBS settlement doesn't run, return above response
    # because the endpoint is disabled. 
    reference_id = request.json.get("reference_id", None)
    settlement_content_list = request.json.get("settlementContent", None)

    # get the system login to sis id, after login to sis
    system_id = get_jwt_identity()

    # create the settle cbs object
    settle_cbs_obj: SettleCbs = SettleCbs({
        'system_id': system_id,
        'settlement_cbs_content': '\n'.join([str(item) for item in settlement_content_list]),
        'settlement_status_id': SETTLE_STATUS_PENDING[0],
        'reference_id': reference_id,
        'created_at': datetime.now()
    })

    try:
        # add settle cbs obj to database session
        db.session.add(settle_cbs_obj)

        # flush before commit to db prevent crash transaction and still add data to db
        db.session.flush()

        # get settle cbs id
        settle_cbs_id = settle_cbs_obj.settle_cbs_id

        # get created at
        created_at = settle_cbs_obj.created_at

        # get each settlement content from list of settlement cbs content
        for item in settlement_content_list:
            # add settlement cbs content detail object to database session
            db.session.add(SettlementCbsContentDetail({
                'settle_cbs_id': settle_cbs_id,
                'currency_code': item['currencyCode'],
                'customer_account': item['customerAccount'],
                'cr_dr': item['cr_dr'],
                'amount': item['amount'],
                'transaction_code': item['transactionCode'],
                'entry_date': datetime.strptime(
                    item['entryDate'], '%Y-%m-%d %H:%M:%S.%f'),
                'value_date': datetime.strptime(
                    item['valueDate'], '%Y-%m-%d %H:%M:%S.%f'),
                'financial_year': item['financialYear'],
                'financial_period': item['financialPeriod'],
                'description': item['description'],
                'flexcube_id': 1
            }))

        # save cbs settle and settlement cbs content detail into database
        db.session.commit()

        # get the system object
        system_obj: System = SystemDao.get_system_by_id(system_id=system_id)

        # sending to flexcube in the background
        send_task_flexcube(system_obj.url,
                           settle_cbs_id,
                           settlement_content_list)

        response = copy.deepcopy(get_const('SUCCESS_200'))
        response['detail']['data'] = {
            "id": settle_cbs_id,
            "settlement_status": SETTLE_STATUS_PENDING[1],
            "created_at": created_at.strftime("%d-%m-%Y %H:%M:%S")
        }
        response_jsonify = jsonify(response)
        response_jsonify.status_code = 200
        return response_jsonify
    except Exception as err:
        db.session.rollback()
        logging.getLogger(__name__).exception("CBS settlement create failed")
        response = copy.deepcopy(get_const('SERVER_ERROR_500'))
        response['detail']['error_message'] = "An internal error occurred."
        response['detail']['error_code'] = 7
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response['http_code']
        return response_jsonify
    finally:
        db.session.close()


def cbs_settlement_by_id_get() -> Response:
    pass


def settle_cbs_status_get(settle_cbs_id: int) -> Response:
    """
    Retrieve the settle cbs status based on environment id from request
    :param settle_cbs_id: ID of settle cbs
    :return: A response as json object for the GET API request.
    """
    pass


def send_task_flexcube(system_url, settle_cbs_id, settlement_cbs_details):
    """
    Forward flexcube task in the background
    :param system_url: System url
    :param settle_cbs_id: CBS Settle ID
    :param settlement_cbs_details: CBS settlement content details
    :return: The celery task object
    """
    flexcube_obj: Flexcube = FlexcubeDao.get_flexcube_by_id(flexcube_id=1)
    serialized_data = FlexcubeSchema().dump(flexcube_obj)

    result = celery.send_task('worker.tasks.send_to_flexcube', kwargs={
        'system_url': system_url,
        'settle_cbs_id': settle_cbs_id,
        'flexcube': serialized_data,
        'settlement_cbs_details': settlement_cbs_details
    })

    return result