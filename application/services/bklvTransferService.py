"""
BKLV Transfer service handles the business logic for Bakong Large Value fund transfers.
Validates the request, checks bank registration, creates a settlement record,
and dispatches a Celery task to send the SOAP request to BKLV.
"""
import copy
import logging
from datetime import datetime
from xml.etree.ElementTree import fromstring, ParseError

from flask import request, jsonify, Response
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from application import celery, db
from application.dao.settleBklvDao import SettleBklvDao
from application.dao.systemDao import SystemDao
from application.models.settleBklv import SettleBklv
from application.models.system import System
from application.schemas.bklvTransferRequestSchema import BklvTransferRequestSchema
from application.utils.responseMessage import get_const, error_response

SETTLE_STATUS_PENDING = (1, 'PENDING')
SETTLE_STATUS_SUCCESS = (2, 'SUCCESS')
SETTLE_STATUS_FAIL = (3, 'FAIL')
SETTLE_STATUS_ERROR = (4, 'ERROR')

PAIN001_NS = {'p': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.05'}

# Optional top-level fields to their corresponding location inside iso_message.
_CROSS_CHECK_XPATHS = {
    'debtor_name': './/p:Dbtr/p:Nm',
    'creditor_name': './/p:Cdtr/p:Nm',
    'receiver_account_id': './/p:CdtrAcct/p:Id/p:Othr/p:Id',
    'execution_date': './/p:ReqdExctnDt',
}

def _cross_check_iso_fields(iso_message: str, claimed: dict) -> list:
    """
    Non-blocking: if the caller supplied any of the optional cross-check
    fields (debtor_name, creditor_name, receiver_account_id, execution_date),
    compare them against what's actually inside iso_message and return a
    list of human-readable mismatch warnings. Never raises, never rejects
    the request — iso_message stays the source of truth (see Blueprint §5,
    step 2, Option A).
    """
    warnings = []
    if not any(claimed.get(field) for field in _CROSS_CHECK_XPATHS):
        return warnings

    try:
        root = fromstring(iso_message)
    except ParseError:
        return ["could not parse iso_message for cross-check"]

    for field, xpath in _CROSS_CHECK_XPATHS.items():
        claimed_val = claimed.get(field)
        if not claimed_val:
            continue
        actual_val = root.findtext(xpath, namespaces=PAIN001_NS)
        if actual_val is not None and claimed_val != actual_val:
            warnings.append(f"{field}: claimed={claimed_val!r} actual={actual_val!r}")
    return warnings

def bklv_transfer_post() -> Response:
    """
    Process a BKLV fund transfer request.
    Flow:
        1. Validate request payload (Marshmallow schema)
        2. Idempotency check by ext_ref
        3. Validate source/destination bank registration (active in SYSTEM table)
        4. Create SettleBklv record with PENDING status
        5. Dispatch Celery task to send SOAP request to BKLV
        6. Return response with settlement ID and PENDING status
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}

    if not body:
        return error_response("BAD_REQUEST_400", "No request body!", 40)

    # --- 1. Validate request payload ---
    schema = BklvTransferRequestSchema()
    try:
        validated_data = schema.load(body)
    except ValidationError as err:
        # Collect all validation error messages
        error_messages = []
        for field_name, messages in err.messages.items():
            for msg in messages:
                error_messages.append(f"{field_name}: {msg}")
        return error_response(
            "BAD_REQUEST_400",
            "; ".join(error_messages),
            40
        )

    ext_ref = validated_data["ext_ref"]
    source_bank = validated_data["source_bank"]
    destination_bank = validated_data["destination_bank"]
    debit_account = validated_data["debit_account"]
    amount = validated_data["amount"]
    currency = validated_data["currency"]
    iso_message = validated_data["iso_message"]

    # --- 1b. Cross-check optional fields against iso_message (non-blocking) ---
    mismatch_warnings = _cross_check_iso_fields(iso_message, validated_data)
    if mismatch_warnings:
        logging.getLogger(__name__).warning(
            "BKLV cross-check mismatch for ext_ref=%s: %s", ext_ref, "; ".join(mismatch_warnings)
        )

    # --- 2. Idempotency check ---
    existing_record = SettleBklvDao.get_settle_bklv_by_ext_ref(ext_ref=ext_ref)
    if existing_record:
        # If the existing record is not in a terminal failure state, return it
        if existing_record.settlement_status_id not in (
            SETTLE_STATUS_FAIL[0], SETTLE_STATUS_ERROR[0]
        ):
            response = copy.deepcopy(get_const('SUCCESS_200'))
            response['detail']['data'] = {
                "id": existing_record.settle_bklv_id,
                "ext_ref": existing_record.ext_ref,
                "settlement_status": _status_name(existing_record.settlement_status_id),
                "created_at": existing_record.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                "message": "Duplicate request — returning existing record."
            }
            response_jsonify = jsonify(response)
            response_jsonify.status_code = response["http_code"]
            return response_jsonify
        # If previously failed, reset the existing record for retry
        # (don't create a new one — unique constraint on ext_ref would block it)

    # --- 3. Validate bank registration ---
    source_system = _get_active_system_by_name(source_bank)
    if source_system is None:
        return error_response(
            "BAD_REQUEST_400",
            f"Source bank '{source_bank}' is not registered or not active!",
            41
        )

    dest_system = _get_active_system_by_name(destination_bank)
    if dest_system is None:
        return error_response(
            "BAD_REQUEST_400",
            f"Destination bank '{destination_bank}' is not registered or not active!",
            42
        )

    # --- 4. Get system identity from JWT ---
    system_id = get_jwt_identity()

    # --- 5. Create or reset SettleBklv record ---
    try:
        if existing_record and existing_record.settlement_status_id in (
            SETTLE_STATUS_FAIL[0], SETTLE_STATUS_ERROR[0]
        ):
            # Retry: reset existing failed record back to PENDING
            existing_record.system_id = system_id
            existing_record.source_bank = source_bank
            existing_record.destination_bank = destination_bank
            existing_record.debit_account = debit_account
            existing_record.amount = amount
            existing_record.currency = currency
            existing_record.iso_message = iso_message
            existing_record.settlement_status_id = SETTLE_STATUS_PENDING[0]
            existing_record.bklv_request_content = None
            existing_record.bklv_response_content = None
            existing_record.bklv_response_status_id = None
            existing_record.bklv_reference = None
            existing_record.updated_at = datetime.now()
            db.session.flush()

            settle_bklv_id = existing_record.settle_bklv_id
            created_at = existing_record.created_at
        else:
            # New record
            settle_bklv_obj = SettleBklv({
                'system_id': system_id,
                'ext_ref': ext_ref,
                'source_bank': source_bank,
                'destination_bank': destination_bank,
                'debit_account': debit_account,
                'amount': amount,
                'currency': currency,
                'iso_message': iso_message,
                'settlement_status_id': SETTLE_STATUS_PENDING[0],
                'created_at': datetime.now()
            })
            db.session.add(settle_bklv_obj)
            db.session.flush()

            settle_bklv_id = settle_bklv_obj.settle_bklv_id
            created_at = settle_bklv_obj.created_at

        db.session.commit()
    except Exception:
        db.session.rollback()
        logging.getLogger(__name__).exception("BKLV settlement create failed")
        response = copy.deepcopy(get_const('SERVER_ERROR_500'))
        response['detail']['error_message'] = "An internal error occurred."
        response['detail']['error_code'] = 7
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response['http_code']
        return response_jsonify
    finally:
        db.session.close()

    # --- 6. Dispatch Celery task ---
    try:
        system_obj = SystemDao.get_system_by_id(system_id=system_id)
        system_url = system_obj.url if system_obj else None
        send_task_bklv(
            system_url=system_url,
            settle_bklv_id=settle_bklv_id,
            ext_ref=ext_ref,
            iso_message=iso_message
        )
    except Exception:
        logging.getLogger(__name__).exception("Failed to dispatch BKLV task")

    # --- 7. Return response ---
    response = copy.deepcopy(get_const('SUCCESS_200'))
    response['detail']['data'] = {
        "id": settle_bklv_id,
        "ext_ref": ext_ref,
        "settlement_status": SETTLE_STATUS_PENDING[1],
        "created_at": created_at.strftime("%d-%m-%Y %H:%M:%S")
    }
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify


def send_task_bklv(system_url, settle_bklv_id, ext_ref, iso_message):
    """
    Forward BKLV task to Celery worker in the background.
    :param system_url: Callback URL for the source bank system
    :param settle_bklv_id: BKLV Settle ID
    :param ext_ref: External reference
    :param iso_message: ISO 20022 XML message
    :return: A celery task object
    """
    result = celery.send_task('worker.bklv_tasks.send_to_bklv', kwargs={
        'system_url': system_url,
        'settle_bklv_id': settle_bklv_id,
        'ext_ref': ext_ref,
        'iso_message': iso_message
    })
    return result


def _get_active_system_by_name(system_name: str) -> System:
    """
    Look up a system by system_name and verify it is active.
    :param system_name: The system_name to search for.
    :return: System object if found and active, None otherwise.
    """
    system_obj = System.query.filter_by(system_name=system_name).first()
    if not system_obj:
        return None

    # Support numeric/boolean status flags where 1=True=active and 0=False=inactive,
    # while keeping compatibility with string values like "active".
    status_value = system_obj.status
    status_text = str(status_value).strip().lower() if status_value is not None else ""

    is_active = status_text in {"1", "active", "true"}
    if is_active:
        return system_obj
    return None


def _status_name(status_id: int) -> str:
    """Map status ID to human-readable name."""
    status_map = {
        SETTLE_STATUS_PENDING[0]: SETTLE_STATUS_PENDING[1],
        SETTLE_STATUS_SUCCESS[0]: SETTLE_STATUS_SUCCESS[1],
        SETTLE_STATUS_FAIL[0]: SETTLE_STATUS_FAIL[1],
        SETTLE_STATUS_ERROR[0]: SETTLE_STATUS_ERROR[1],
    }
    return status_map.get(status_id, "UNKNOWN")
