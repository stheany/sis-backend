# services/settlementPmBookService.py
"""
Service layer for PM Book settlement.
- Validates incoming JSON (Marshmallow)
- Persists master/detail rows
- Enqueues Celery task to call Flexcube (SOAP)
- Returns standardized response payloads
"""
import copy
import logging
from datetime import datetime
from flask import request, jsonify, Response
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError

from settings import FLEXCUBE_URL
from application import db, celery
from application.constants.status import Status
from application.models.settlePmBook import SettlePmBook
from application.models.settlementPmBookDetail import SettlementPmBookDetail
from application.schemas.pmBookRequestSchema import PMBookCreateRequest
from application.schemas.pmBookResponseSchema import PMBookCreateResponse
from application.utils.responseMessage import get_const

logger = logging.getLogger(__name__)

def settle_pm_book_post() -> Response:
    """
    Create a PM Book settlement (single-leg).
    Request JSON must follow PMBookCreateRequest.
    """
    try:
        payload = request.get_json() or {}
        data = PMBookCreateRequest().load(payload)  # raises 400 via Marshmallow if invalid
        logger.info("PM Book create request validated: reference_id=%s", data.get("reference_id"))

        system_id = get_jwt_identity()
        logger.info("Authenticated system_id=%s", system_id)

        # --- Master row
        spb = SettlePmBook({
            "system_id": system_id,
            "settlement_status_id": Status.PENDING.value,
            "reference_id": data["reference_id"],
            "created_at": datetime.now(),
            # Convenience echo fields
            "dr_ac_no": data["dr_ac_no"],
            "cr_ac_no": data["cr_ac_no"],
            "transaction_amount": data["cr_amt"],
            "transaction_currency": data["cr_ac_ccy"],
            "txn_value_date": data["txn_value_date"],
        })
        db.session.add(spb)
        db.session.flush()  # obtain PK
        logger.info("Created SettlePmBook: id=%s", spb.settle_pm_book_id)

        # --- Detail row
        detail = SettlementPmBookDetail({
            "settle_pm_book_id": spb.settle_pm_book_id,
            "dr_ac_no": data["dr_ac_no"],
            "cr_ac_no": data["cr_ac_no"],
            "currency_code": data["cr_ac_ccy"],
            "amount": data["cr_amt"],
            "txn_value_date": data["txn_value_date"],
            "instruction_date": data["instruction_date"],
            "source_code": data["source_code"],
            "network_code": data["network_code"],
            "txn_branch": data["branch"],
            "host_code": data["host_code"],
            "remarks": data.get("remarks"),
            "charge_component": data.get("charge_component"),
            "charge_amount": data.get("charge_amount"),
            "flexcube_id": 1,  # TODO: lookup if per-system
        })
        db.session.add(detail)
        db.session.commit()
        logger.info("Created SettlementPmBookDetail: id=%s", detail.settlement_pm_book_detail_id)

        # --- enqueue Celery task
        celery.send_task(
            "worker.pm_book_tasks.send_to_flexcube_pm_book",
            kwargs={
                "settle_pm_book_id": spb.settle_pm_book_id,
                "request_json": data,
                "flexcube_url": FLEXCUBE_URL,
            },
        )
        logger.info("Queued PMBook worker task for settle_pm_book_id=%s", spb.settle_pm_book_id)

        # --- response
        ok = copy.deepcopy(get_const("SUCCESS_200"))
        ok["detail"]["data"] = PMBookCreateResponse().dump({
            "id": spb.settle_pm_book_id,
            "settlement_status": Status.PENDING.name,
            "created_at": spb.created_at,
            "msgstat": None,
            "txn_ref_no": None,
            "user_ref_no": None,
            "flexcube_message": None,
        })
        r = jsonify(ok); r.status_code = 200
        return r

    except IntegrityError:
        db.session.rollback()
        logger.warning("Duplicate reference_id for PM Book create request")
        err = copy.deepcopy(get_const("CONFLICT_409"))
        err["detail"]["error_message"] = "Duplicate reference_id."
        err["detail"]["error_code"] = 40901
        r = jsonify(err); r.status_code = err["http_code"]
        return r

    except Exception as e:
        db.session.rollback()
        logger.exception("PM Book create error")
        err = copy.deepcopy(get_const("SERVER_ERROR_500"))
        err["detail"]["error_message"] = "An internal error occurred."
        err["detail"]["error_code"] = 9002
        r = jsonify(err); r.status_code = err["http_code"]
        return r

    finally:
        db.session.close()