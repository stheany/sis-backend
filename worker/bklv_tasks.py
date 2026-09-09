"""
Celery task for sending BKLV makeFullFundTransfer SOAP requests.
Builds the SOAP envelope, sends it to BKLV, parses the response,
updates the database, and optionally callbacks the source bank system.
"""
import os
import re
from datetime import datetime
from xml.etree.ElementTree import fromstring, ParseError

import cx_Oracle
import requests
from celery.utils.log import get_task_logger
from worker import celery_app
from worker.system_service import update_system_status

logger = get_task_logger(__name__)

SETTLE_STATUS_PENDING = (1, 'PENDING')
SETTLE_STATUS_SUCCESS = (2, 'SUCCESS')
SETTLE_STATUS_FAIL = (3, 'FAIL')
SETTLE_STATUS_ERROR = (4, 'ERROR')

DSN = f"{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_SERVICE_NAME')}"


def _build_soap_envelope(username, password, iso_message, ext_ref, leg=None):
    """
    Build the SOAP envelope for makeFullFundTransfer.
    The iso_message is wrapped in CDATA to preserve the XML content.

    leg is set ('DEBIT' or 'CREDIT') only when this call is going to one
    specific bank's own dedicated BKLV gateway (see bank_transfer_endpoint
    in bklv_client.py) — it tells that bank's gateway explicitly which half
    of the transfer to apply, since a per-bank gateway shouldn't try to
    guess from the message alone. Left unset for the shared fallback
    gateway, which applies both halves itself from one call, same as
    before per-bank endpoints existed.
    """
    leg_element = f'<web:leg>{leg}</web:leg>' if leg else ''
    envelope = (
        '<soapenv:Envelope'
        ' xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"'
        ' xmlns:web="http://webservice.nbc.org.kh/">'
        '<soapenv:Header/>'
        '<soapenv:Body>'
        '<web:makeFullFundTransfer>'
        '<web:cm_user_name>{username}</web:cm_user_name>'
        '<web:cm_password>{password}</web:cm_password>'
        '<web:iso_message><![CDATA[{iso_message}]]></web:iso_message>'
        '<web:ext_ref>{ext_ref}</web:ext_ref>'
        '{leg_element}'
        '</web:makeFullFundTransfer>'
        '</soapenv:Body>'
        '</soapenv:Envelope>'
    ).format(
        username=username,
        password=password,
        iso_message=iso_message,
        ext_ref=ext_ref,
        leg_element=leg_element
    )
    return envelope


def _post_makefullfundtransfer(url, iso_message, ext_ref, leg=None):
    """
    POSTs one makeFullFundTransfer call to a specific BKLV gateway URL and
    parses its response. Returns (status_tuple, request_body, response_text).
    Lets requests exceptions (Timeout, ConnectionError, ...) propagate to
    the caller, same as the inline POST send_to_bklv used to do directly.
    """
    bklv_username = os.environ.get('BKLV_USERNAME', '')
    bklv_password = os.environ.get('BKLV_PASSWORD', '')
    bklv_verify_ssl = os.environ.get('BKLV_VERIFY_SSL', 'true').lower() in ('1', 'true', 'yes', 'on')
    bklv_timeout = int(os.environ.get('BKLV_SOAP_TIMEOUT', '60'))

    request_body = _build_soap_envelope(
        username=bklv_username, password=bklv_password,
        iso_message=iso_message, ext_ref=ext_ref, leg=leg,
    )
    response = requests.post(
        url,
        data=request_body.encode('utf-8'),
        headers={'Content-Type': 'text/xml; charset=utf-8'},
        verify=bklv_verify_ssl,
        timeout=bklv_timeout,
    )
    response_text = response.content.decode('utf-8')
    logger.info('BKLV Response (%s leg, url=%s): %s', leg or 'single-call', url, response_text)
    status = _parse_bklv_response(response_text)
    return status, request_body, response_text


def _record_settlement_result(con, cur, settle_bklv_id, system_url, request_body, response_text, status, bklv_reference, sent_time):
    """
    Shared DB-update + source-system-callback tail, used by both
    send_to_bklv (single-endpoint) and send_to_bklv_with_balance_check
    (single- or dual-endpoint) once a final status is known.
    """
    sql_stmt = (
        'UPDATE SETTLE_BKLV SET '
        'BKLV_REQUEST_CONTENT = :request_body, '
        'BKLV_RESPONSE_CONTENT = :response_body, '
        'BKLV_RESPONSE_STATUS_ID = :response_status, '
        'BKLV_RESPONSE_AT = :response_at, '
        'SETTLEMENT_STATUS_ID = :response_status, '
        'BKLV_REFERENCE = :bklv_reference, '
        'UPDATED_AT = :settlement_update_at, '
        'SENT_AT = :submit_at '
        'WHERE SETTLE_BKLV_ID = :settle_bklv_id'
    )
    cur.execute(sql_stmt, {
        'request_body': request_body.strip() if request_body else None,
        'response_body': response_text,
        'response_status': status[0],
        'response_at': datetime.now(),
        'bklv_reference': bklv_reference,
        'submit_at': sent_time,
        'settlement_update_at': datetime.now(),
        'settle_bklv_id': settle_bklv_id
    })
    con.commit()
    logger.info('BKLV settlement %s updated with status: %s', settle_bklv_id, status[1])

    if system_url:
        try:
            if update_system_status(system_url=system_url, settle_cbs_id=settle_bklv_id, status=status):
                logger.info("Callback to external system success")
            else:
                logger.warning("Callback to external system failed")
        except Exception as cb_err:
            logger.warning("Callback error: %s", str(cb_err))


@celery_app.task()
def send_to_bklv(system_url, settle_bklv_id, ext_ref, iso_message):
    """
    Celery task: send makeFullFundTransfer SOAP request to BKLV.
    1. Build SOAP envelope
    2. Send HTTP POST to BKLV
    3. Parse response for status
    4. Update SETTLE_BKLV record in Oracle DB
    5. Callback source bank system with status
    """
    logger.info('Got Request - Send to BKLV (settle_bklv_id=%s, ext_ref=%s)',
                settle_bklv_id, ext_ref)

    bklv_url = os.environ.get('BKLV_SOAP_URL', '')
    bklv_username = os.environ.get('BKLV_USERNAME', '')
    bklv_password = os.environ.get('BKLV_PASSWORD', '')
    bklv_verify_ssl = os.environ.get('BKLV_VERIFY_SSL', 'true').lower() in ('1', 'true', 'yes', 'on')
    bklv_timeout = int(os.environ.get('BKLV_SOAP_TIMEOUT', '60'))

    if not bklv_url:
        logger.error('BKLV_SOAP_URL is not configured!')
        _update_settle_bklv_error(settle_bklv_id, 'BKLV_SOAP_URL is not configured')
        return

    con = None
    cur = None

    try:
        # Establish Oracle connection
        con = cx_Oracle.connect(
            user=os.environ.get('DB_USERNAME'),
            password=os.environ.get('DB_PASSWORD'),
            dsn=DSN,
            encoding="UTF-8"
        )
    except cx_Oracle.DatabaseError as er:
        logger.error("Oracle DB connection error: %s", str(er))
        return

    try:
        cur = con.cursor()

        # Build SOAP request
        request_body = _build_soap_envelope(
            username=bklv_username,
            password=bklv_password,
            iso_message=iso_message,
            ext_ref=ext_ref
        )

        sent_time = datetime.now()

        # Send to BKLV
        response = requests.post(
            bklv_url,
            data=request_body.encode('utf-8'),
            headers={'Content-Type': 'text/xml; charset=utf-8'},
            verify=bklv_verify_ssl,
            timeout=bklv_timeout
        )

        response_text = response.content.decode('utf-8')
        logger.info('BKLV Response: %s', response_text)

        # Parse BKLV response for status
        status = _parse_bklv_response(response_text)
        bklv_reference = _extract_bklv_reference(response_text)

        # Update SETTLE_BKLV record
        sql_stmt = (
            'UPDATE SETTLE_BKLV SET '
            'BKLV_REQUEST_CONTENT = :request_body, '
            'BKLV_RESPONSE_CONTENT = :response_body, '
            'BKLV_RESPONSE_STATUS_ID = :response_status, '
            'BKLV_RESPONSE_AT = :response_at, '
            'SETTLEMENT_STATUS_ID = :response_status, '
            'BKLV_REFERENCE = :bklv_reference, '
            'UPDATED_AT = :settlement_update_at, '
            'SENT_AT = :submit_at '
            'WHERE SETTLE_BKLV_ID = :settle_bklv_id'
        )

        cur.execute(sql_stmt, {
            'request_body': request_body.strip(),
            'response_body': response_text,
            'response_status': status[0],
            'response_at': datetime.now(),
            'bklv_reference': bklv_reference,
            'submit_at': sent_time,
            'settlement_update_at': datetime.now(),
            'settle_bklv_id': settle_bklv_id
        })

        con.commit()
        logger.info('BKLV settlement %s updated with status: %s', settle_bklv_id, status[1])

        # Callback to source bank system
        if system_url:
            try:
                if update_system_status(
                    system_url=system_url,
                    settle_cbs_id=settle_bklv_id,
                    status=status
                ):
                    logger.info("Callback to external system success")
                else:
                    logger.warning("Callback to external system failed")
            except Exception as cb_err:
                logger.warning("Callback error: %s", str(cb_err))

    except requests.exceptions.Timeout:
        logger.error("BKLV SOAP request timed out for settle_bklv_id=%s", settle_bklv_id)
        _update_settle_bklv_status(cur, con, settle_bklv_id, SETTLE_STATUS_ERROR)
    except requests.exceptions.ConnectionError:
        logger.error("BKLV connection error for settle_bklv_id=%s", settle_bklv_id)
        _update_settle_bklv_status(cur, con, settle_bklv_id, SETTLE_STATUS_ERROR)
    except cx_Oracle.DatabaseError as er:
        logger.error("Oracle DB error: %s", str(er))
    except Exception as er:
        logger.error("Unexpected error: %s", str(er))
        if cur and con:
            _update_settle_bklv_status(cur, con, settle_bklv_id, SETTLE_STATUS_ERROR)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


@celery_app.task()
def send_to_bklv_with_balance_check(system_url, settle_bklv_id, ext_ref, iso_message, debtor_bic, creditor_bic, amount):
    """
    NCS-BKLV SOAP rail only (see
    application/services/ncsBklvSoapService.py::_handle_upload_netfile) —
    checks the debit account's real BKLV balance before ever calling
    makeFullFundTransfer. This is additive: the REST /bklv/transfer rail
    (bklvTransferService.py) keeps dispatching straight to send_to_bklv,
    unchanged, with no balance check.

    debtor_bic/creditor_bic/amount are resolved synchronously by the caller
    (a local DB lookup, not a BKLV call) before this task is even queued —
    only the actual balance check and settlement calls, real network calls
    to BKLV, are deferred to the background here, matching "respond before
    BKLV is contacted".

    Each participant bank runs its own BKLV gateway (see bklv_client.py's
    BKLV_BANK_ENDPOINTS) rather than there being one shared BKLV hub: the
    debit leg is sent to the DEBTOR bank's own endpoint, the credit leg to
    the CREDITOR bank's own endpoint, as two separate calls. If neither bank
    has a dedicated endpoint configured, both resolve to the same shared
    fallback gateway, and a single call covers both legs — exactly the
    original one-call behavior, unchanged for banks without their own mock.
    """
    from bklv_client import BklvClientError, bank_transfer_endpoint, get_balance

    try:
        balance = get_balance(debtor_bic)
    except BklvClientError as err:
        logger.error("Balance check failed for settle_bklv_id=%s bic=%s: %s", settle_bklv_id, debtor_bic, err)
        _update_settle_bklv_message(settle_bklv_id, SETTLE_STATUS_ERROR, f"Balance check failed: {err}")
        return

    if balance < amount:
        logger.warning(
            "Insufficient balance for settle_bklv_id=%s bic=%s balance=%s amount=%s",
            settle_bklv_id, debtor_bic, balance, amount
        )
        _update_settle_bklv_message(
            settle_bklv_id, SETTLE_STATUS_FAIL,
            f"Insufficient balance: available {balance}, needed {amount}"
        )
        return

    fallback_url = os.environ.get('BKLV_SOAP_URL', '')
    debtor_url = bank_transfer_endpoint(debtor_bic) or fallback_url
    creditor_url = bank_transfer_endpoint(creditor_bic) or fallback_url

    if not debtor_url:
        logger.error('No BKLV endpoint configured for settle_bklv_id=%s (debtor_bic=%s)', settle_bklv_id, debtor_bic)
        _update_settle_bklv_error(settle_bklv_id, 'No BKLV endpoint configured')
        return

    con = None
    cur = None
    try:
        con = cx_Oracle.connect(
            user=os.environ.get('DB_USERNAME'),
            password=os.environ.get('DB_PASSWORD'),
            dsn=DSN,
            encoding="UTF-8"
        )
    except cx_Oracle.DatabaseError as er:
        logger.error("Oracle DB connection error: %s", str(er))
        return

    try:
        cur = con.cursor()
        sent_time = datetime.now()

        if debtor_url == creditor_url:
            # No dedicated endpoint for either bank (or both point at the
            # same one) — one call covers both legs, same as before
            # per-bank gateways existed.
            status, request_body, response_text = _post_makefullfundtransfer(debtor_url, iso_message, ext_ref)
            bklv_reference = _extract_bklv_reference(response_text)
        else:
            debit_status, debit_req, debit_resp = _post_makefullfundtransfer(
                debtor_url, iso_message, ext_ref, leg='DEBIT'
            )
            if debit_status != SETTLE_STATUS_SUCCESS:
                # Debit leg didn't settle — never attempt the credit leg.
                status = debit_status
                request_body, response_text = debit_req, debit_resp
                bklv_reference = _extract_bklv_reference(debit_resp)
            else:
                credit_status, credit_req, credit_resp = _post_makefullfundtransfer(
                    creditor_url, iso_message, ext_ref, leg='CREDIT'
                )
                request_body = debit_req + '\n---CREDIT LEG---\n' + credit_req
                response_text = debit_resp + '\n---CREDIT LEG---\n' + credit_resp
                bklv_reference = _extract_bklv_reference(debit_resp) or _extract_bklv_reference(credit_resp)
                if credit_status == SETTLE_STATUS_SUCCESS:
                    status = SETTLE_STATUS_SUCCESS
                else:
                    # Debit succeeded but credit didn't — funds may be in
                    # limbo (debited but never credited). Flag distinctly
                    # as ERROR rather than reporting a false SUCCESS or a
                    # misleading FAIL (the debit itself did NOT fail).
                    status = SETTLE_STATUS_ERROR
                    logger.error(
                        'Debit leg succeeded but credit leg did not for settle_bklv_id=%s — '
                        'funds may be in limbo (debited from %s, not yet credited to %s)',
                        settle_bklv_id, debtor_bic, creditor_bic
                    )

        _record_settlement_result(
            con, cur, settle_bklv_id, system_url,
            request_body, response_text, status, bklv_reference, sent_time
        )

    except requests.exceptions.Timeout:
        logger.error("BKLV SOAP request timed out for settle_bklv_id=%s", settle_bklv_id)
        _update_settle_bklv_status(cur, con, settle_bklv_id, SETTLE_STATUS_ERROR)
    except requests.exceptions.ConnectionError:
        logger.error("BKLV connection error for settle_bklv_id=%s", settle_bklv_id)
        _update_settle_bklv_status(cur, con, settle_bklv_id, SETTLE_STATUS_ERROR)
    except cx_Oracle.DatabaseError as er:
        logger.error("Oracle DB error: %s", str(er))
    except Exception as er:
        logger.error("Unexpected error: %s", str(er))
        if cur and con:
            _update_settle_bklv_status(cur, con, settle_bklv_id, SETTLE_STATUS_ERROR)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def _update_settle_bklv_message(settle_bklv_id, status, message):
    """
    Update SETTLE_BKLV to a terminal status with an explanatory message, for
    failures that happen before BKLV is ever contacted (e.g. the balance
    check in send_to_bklv_with_balance_check) — same shape as
    _update_settle_bklv_error, generalized to any status.
    """
    try:
        con = cx_Oracle.connect(
            user=os.environ.get('DB_USERNAME'),
            password=os.environ.get('DB_PASSWORD'),
            dsn=DSN,
            encoding="UTF-8"
        )
        cur = con.cursor()
        sql_stmt = (
            'UPDATE SETTLE_BKLV SET '
            'SETTLEMENT_STATUS_ID = :status_id, '
            'BKLV_RESPONSE_CONTENT = :message, '
            'UPDATED_AT = :updated_at '
            'WHERE SETTLE_BKLV_ID = :settle_bklv_id'
        )
        cur.execute(sql_stmt, {
            'status_id': status[0],
            'message': message,
            'updated_at': datetime.now(),
            'settle_bklv_id': settle_bklv_id
        })
        con.commit()
        cur.close()
        con.close()
    except Exception as er:
        logger.error("Failed to update settle_bklv message: %s", str(er))


def _parse_bklv_response(response_text):
    """
    Parse the BKLV SOAP response to determine success or failure.
    Prefers the ISO 20022 pain.002 TxSts code (ACSP/ACSC/RJCT/PDNG); falls
    back to keyword matching for SOAP faults or non-pain.002 responses,
    since abbreviated ISO codes (e.g. RJCT) don't reliably contain English
    words like "reject".
    Returns status tuple (id, name).
    """
    try:
        root = fromstring(response_text)
        for elem in root.iter():
            if elem.tag.split('}')[-1] == 'TxSts':  # strip XML namespace, if any
                tx_sts = (elem.text or '').strip().upper()
                if tx_sts in ('ACSP', 'ACSC'):
                    return SETTLE_STATUS_SUCCESS
                if tx_sts == 'RJCT':
                    return SETTLE_STATUS_FAIL
                if tx_sts == 'PDNG':
                    return SETTLE_STATUS_PENDING
                break
    except ParseError:
        pass

    response_lower = response_text.lower()

    # Check for SOAP fault — covers all namespace prefixes:
    #   <soap:Fault>, <soapenv:Fault>, <SOAP-ENV:Fault>
    if 'fault>' in response_lower or '<soap:fault' in response_lower:
        logger.warning('BKLV SOAP Fault detected in response')
        return SETTLE_STATUS_FAIL

    # Check for common success indicators in the response
    if 'success' in response_lower or 'accepted' in response_lower:
        return SETTLE_STATUS_SUCCESS

    # Check for failure indicators
    if 'fail' in response_lower or 'error' in response_lower or 'reject' in response_lower:
        return SETTLE_STATUS_FAIL

    # Default: treat as success if HTTP was ok and no fault detected
    return SETTLE_STATUS_SUCCESS


def _extract_bklv_reference(response_text):
    """
    Extract BKLV reference/transaction ID from the response if available.
    """
    # Try to extract a reference from common response patterns
    match = re.search(r'<.*?[Rr]ef.*?>(.*?)</.*?>', response_text)
    if match:
        return match.group(1).strip()
    return None


def _update_settle_bklv_status(cur, con, settle_bklv_id, status):
    """
    Update the SETTLE_BKLV status in case of error.
    """
    try:
        sql_stmt = (
            'UPDATE SETTLE_BKLV SET '
            'SETTLEMENT_STATUS_ID = :status_id, '
            'UPDATED_AT = :updated_at '
            'WHERE SETTLE_BKLV_ID = :settle_bklv_id'
        )
        cur.execute(sql_stmt, {
            'status_id': status[0],
            'updated_at': datetime.now(),
            'settle_bklv_id': settle_bklv_id
        })
        con.commit()
    except Exception as er:
        logger.error("Failed to update error status: %s", str(er))


def _update_settle_bklv_error(settle_bklv_id, error_message):
    """
    Update SETTLE_BKLV to ERROR status when we cannot even connect to DB initially.
    Opens a dedicated connection for this.
    """
    try:
        con = cx_Oracle.connect(
            user=os.environ.get('DB_USERNAME'),
            password=os.environ.get('DB_PASSWORD'),
            dsn=DSN,
            encoding="UTF-8"
        )
        cur = con.cursor()
        sql_stmt = (
            'UPDATE SETTLE_BKLV SET '
            'SETTLEMENT_STATUS_ID = :status_id, '
            'BKLV_RESPONSE_CONTENT = :error_msg, '
            'UPDATED_AT = :updated_at '
            'WHERE SETTLE_BKLV_ID = :settle_bklv_id'
        )
        cur.execute(sql_stmt, {
            'status_id': SETTLE_STATUS_ERROR[0],
            'error_msg': error_message,
            'updated_at': datetime.now(),
            'settle_bklv_id': settle_bklv_id
        })
        con.commit()
        cur.close()
        con.close()
    except Exception as er:
        logger.error("Failed to update error status: %s", str(er))
