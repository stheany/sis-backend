
from datetime import datetime
import json
import logging

from application.dao.SettleNcsBklvBatchDao import SettleNcsBklvBatchDao
from application.dao.settleBklvDao import SettleBklvDao
from application.dao.settleNcsBklvBatch import SettleNcsBklvBatch
from application import celery, db
from application.dao.systemDao import SystemDao
from application.dao.systemLoginSisDao import SystemLoginSisDao
from application.models.settleBklv import SettleBklv
from application.utils.password_utils import verify_password
from bklv_client import BklvClientError, get_account_balance
from application.utils.ncsBklvSoapXml import (
    SoapFault,
    build_account_balance_response,
    build_response_envelope,
    build_status_detail_response,
    parse_operation,
    build_fault_envelope,
    build_pain001_message
)

STATUS_PENDING = 1
STATUS_SUCCESS = 2
STATUS_FAIL = 3
STATUS_ERROR = 4

_REQUIRED_LINE_FIELDS = (
    'currency_code', 'debit_account', 'credit_account', 'amount',
    'debtor_bic', 'creditor_bic',
)

logger = logging.getLogger(__name__)

def handle_ncs_bklv_soap_request(raw_xml: str, expected_operation: str = None) -> str:
    """
    Handle an incoming SOAP request from ncs and return a SOAP response.
    """
    try:
        operation_name, params = parse_operation(raw_xml)
        if expected_operation and operation_name != expected_operation:
            raise SoapFault(
                f"URL is for operation '{expected_operation}' but the SOAP body's "
                f"root element is '{operation_name}'"
            )
        handler = _OPERATION_HANDLERS.get(operation_name)
        if handler is None:
            raise SoapFault(f"Unknown operation: {operation_name}")
        return handler(params)
    except SoapFault as fault:
        logger.warning("NCS-BKLV SOAP fault: %s", fault.fault_string)
        return build_fault_envelope(fault)
    except Exception:
        logger.exception("Unhandled error processing NCS-BKLV SOAP request")
        return build_fault_envelope(SoapFault("Internal server error", fault_code="Server"))

def _authenticate(params: dict, username_key: str = 'pUserName', password_key: str = 'pUserPwd'):
    """
    Authenticate the SOAP request using the provided username and password , 
    AuthCode is optional and not verified in SIS.
    """
    auth_code = params.get('pAuthCode')
    username = params.get(username_key)
    password = params.get(password_key)

    if auth_code:
        logger.info("NCS-BKLV SOAP call carried pAuthCode=%s (not verified)", auth_code)

    if not username or not password:
        raise SoapFault("Missing credentials")

    login_obj = SystemLoginSisDao.get_system_login_sis_by_username(username=username)
    if not login_obj or not verify_password(password, login_obj.password):
        raise SoapFault("Authentication failed")

    return login_obj

def _is_active_system(system) -> bool:
    """check system is active based on status field."""
    status_text = str(system.status).strip().lower() if system.status is not None else ""
    return status_text in {"1", "active", "true"}

def _handle_get_fc_date(params: dict) -> str:
    """
    Handle the <ws:getFCDate/> request and return a SOAP response 
    with a date in MM-DD-YYYY format, no authentication required.
    """
    business_date = datetime.now().strftime('%m-%d-%Y')
    return build_response_envelope('getFCDate', 'getFCDateResult', business_date)

def _handle_get_cbs_account_balance(params: dict) -> str:
    _authenticate(params, username_key='pUser', password_key='pPassword')

    accounts = []
    for system in SystemDao.get_systems_with_settlement_account():
        if not _is_active_system(system):
            continue
        detail = _live_account_detail_for(system)
        accounts.append({
            'bank_name': system.system_name,
            'branch_code': system.short_name or '',
            'account_number': system.settlement_account_number,
            'account_class': 'CURRENT',
            'balance': detail['balance'],
            'ccy': detail['ccy'],
        })
    return build_account_balance_response(accounts)

def _live_account_detail_for(system) -> dict:
    """
    Get the live account balance and currency for a system's settlement account.
    """
    if not system.bic_code:
        logger.warning("No bic_code for system_name=%s — cannot fetch a live BKLV balance", system.system_name)
        return {'balance': '0.00', 'ccy': ''}
    try:
        detail = get_account_balance(system.bic_code)
        return {'balance': f"{detail['balance']:.2f}", 'ccy': detail['currency'] or ''}
    except BklvClientError as err:
        logger.warning("Live balance fetch failed for bic=%s: %s", system.bic_code, err)
        return {'balance': '0.00', 'ccy': ''}

def _validate_line(line, index: int) -> dict:
    if not isinstance(line, dict):
        raise SoapFault(f"Line {index} is not an object")
    missing = [field for field in _REQUIRED_LINE_FIELDS if not line.get(field)]
    if missing:
        raise SoapFault(f"Line {index} is missing required field(s): {', '.join(missing)}")
    try:
        float(line['amount'])
    except (TypeError, ValueError):
        raise SoapFault(f"Line {index} has a non-numeric amount")
    return line

def _handle_upload_netfile(params: dict) -> str:
    login_obj = _authenticate(params)

    file_name = params.get('pFileName')
    content = params.get('pContent')
    if not file_name:
        raise SoapFault("pFileName is required")
    if not content:
        raise SoapFault("pContent is required")

    if SettleNcsBklvBatchDao.get_by_file_name(file_name):
        raise SoapFault(f"Netfile '{file_name}' was already submitted")

    try:
        lines = json.loads(content)
    except (TypeError, ValueError) as err:
        raise SoapFault(f"pContent must be a JSON array of line objects: {err}") from err
    if not isinstance(lines, list) or not lines:
        raise SoapFault("pContent must be a non-empty JSON array of line objects")

    lines = [_validate_line(line, index) for index, line in enumerate(lines, start=1)]

    dispatch_queue = []
    try:
        batch_req = SettleNcsBklvBatch({
            'system_id': login_obj.system_id,
            'file_name': file_name,
            'currency_code': lines[0].get('currency_code'),
            'batch_status_id': STATUS_PENDING,
            'submitted_content': content,
            'created_at': datetime.now(),
        })
        db.session.add(batch_req)
        db.session.flush()
        batch_id = batch_req.settle_ncs_bklv_batch_id

        for index, line in enumerate(lines, start=1):
            ext_ref = f"{file_name}-{index}"
            iso_message = build_pain001_message(line, msg_id=ext_ref)

            settle_bklv_obj = SettleBklv({
                'system_id': login_obj.system_id,
                'ext_ref': ext_ref,
                'source_bank': line.get('debtor_name') or '',
                'destination_bank': line.get('creditor_name') or '',
                'debit_account': line.get('debit_account'),
                'amount': float(line['amount']),
                'currency': line.get('currency_code'),
                'iso_message': iso_message,
                'settlement_status_id': STATUS_PENDING,
                'created_at': datetime.now(),
                'batch_id': batch_id,
                'line_no': index,
            })
            db.session.add(settle_bklv_obj)
            db.session.flush()
            dispatch_queue.append((
                settle_bklv_obj.settle_bklv_id, ext_ref, iso_message,
                line['debtor_bic'], line['creditor_bic'], float(line['amount']),
            ))

        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Failed to create NCS-BKLV netfile batch")
        raise SoapFault("Failed to create netfile batch", fault_code="Server")
    finally:
        db.session.close()

    for settle_bklv_id, ext_ref, iso_message, debtor_bic, creditor_bic, amount in dispatch_queue:
        try:
            _send_task_bklv_with_balance_check(
                settle_bklv_id=settle_bklv_id,
                ext_ref=ext_ref,
                iso_message=iso_message,
                debtor_bic=debtor_bic,
                creditor_bic=creditor_bic,
                amount=amount,
            )
        except Exception:
            logger.exception("Failed to dispatch BKLV task for line ext_ref=%s", ext_ref)

    return build_response_envelope(
        'upload_File_GI_FLATFILE', 'upload_File_GI_FLATFILEResult', str(batch_id)
    )

def _send_task_bklv_with_balance_check(settle_bklv_id, ext_ref, iso_message, debtor_bic, creditor_bic, amount):
    """
    Dispatch to worker.bklv_tasks.send_to_bklv_with_balance_check — same
    send-by-task-name pattern as bklvTransferService.send_task_bklv, but a
    different task: this one checks the debit account's real BKLV balance
    first and never calls makeFullFundTransfer if it's insufficient, then
    settles via each bank's own dedicated BKLV gateway (debtor_bic/
    creditor_bic each resolve to their own endpoint — see
    bklv_client.py's BKLV_BANK_ENDPOINTS). Only used by the NCS-BKLV SOAP
    rail; the REST /bklv/transfer rail keeps using the plain send_to_bklv
    task, unchanged.
    """
    return celery.send_task('worker.bklv_tasks.send_to_bklv_with_balance_check', kwargs={
        'system_url': None,
        'settle_bklv_id': settle_bklv_id,
        'ext_ref': ext_ref,
        'iso_message': iso_message,
        'debtor_bic': debtor_bic,
        'creditor_bic': creditor_bic,
        'amount': amount,
    })

def _handle_get_file_status_detail(params: dict) -> str:
    _authenticate(params)

    tran_no_raw = params.get('pTranNo')
    file_name = params.get('pFileName')
    try:
        batch_id = int(tran_no_raw)
    except (TypeError, ValueError):
        raise SoapFault("pTranNo must be numeric")

    batch_req = SettleNcsBklvBatchDao.get_by_id(batch_id)
    if not batch_req or (file_name and batch_req.file_name != file_name):
        raise SoapFault(f"No netfile found for tran_no={tran_no_raw}")

    lines = SettleBklvDao.get_by_batch_id(batch_id)
    statuses = [line.settlement_status_id for line in lines]

    if not statuses or STATUS_PENDING in statuses:
        response_status, tran_status, response_message = 'Waiting', 'PENDING', None
    elif any(status_id in (STATUS_FAIL, STATUS_ERROR) for status_id in statuses):
        response_status, tran_status = 'Error', 'COMPLETED'
        failed_refs = [line.ext_ref for line in lines if line.settlement_status_id in (STATUS_FAIL, STATUS_ERROR)]
        response_message = f"{len(failed_refs)} of {len(lines)} line(s) failed: {', '.join(failed_refs)}"
    else:
        response_status, tran_status, response_message = 'Processed', 'COMPLETED', None

    if response_status != 'Waiting' and batch_req.batch_status_id == STATUS_PENDING:
        batch_req.batch_status_id = STATUS_SUCCESS if response_status == 'Processed' else STATUS_ERROR
        batch_req.updated_at = datetime.now()
        db.session.commit()

    return build_status_detail_response(
        tran_no=batch_id,
        file_name=batch_req.file_name,
        tran_dte=batch_req.created_at.strftime('%Y-%m-%dT%H:%M:%S+07:00'),
        tran_status=tran_status,
        response_status=response_status,
        response_message=response_message,
        response_dte=datetime.now().strftime('%Y-%m-%dT%H:%M:%S+07:00'),
    )

_OPERATION_HANDLERS = {
    'getFCDate': _handle_get_fc_date,
    'getCBSAccountBalanceNCS': _handle_get_cbs_account_balance,
    'upload_File_GI_FLATFILE': _handle_upload_netfile,
    'getFile_Status_Detail': _handle_get_file_status_detail,
}