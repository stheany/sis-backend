# worker/pm_book_tasks.py  (patched)

import os
import re
from decimal import Decimal
from datetime import datetime
from xml.sax.saxutils import escape as _xml_escape

import settings
import cx_Oracle
import requests
from bs4 import BeautifulSoup as BS
from celery.utils.log import get_task_logger
from worker import celery_app
from application.constants.status import Status

logger = get_task_logger(__name__)

DB_DSN      = settings.DB_DSN
DB_USERNAME = settings.DB_USERNAME
DB_PASSWORD = settings.DB_PASSWORD

FLEXCUBE_DEFAULT_URL = settings.FLEXCUBE_URL
FLEXCUBE_TIMEOUT_S   = settings.FLEXCUBE_HTTP_TIMEOUT
FLEXCUBE_VERIFY_SSL  = settings.FLEXCUBE_VERIFY_SSL
SOAP_DEBUG           = settings.SOAP_DEBUG

def _redact(s: str) -> str:
    # mask long digit sequences (simple, extend if needed)
    return re.sub(r"(\d{6})\d{2,}(\d{2})", r"\1***\2", s or "")

def _soap_pm_book_xml(header: dict, body: dict) -> str:
    source     = header.get("source", "FCAT")
    ubscomp    = header.get("ubscomp", "FCUBS")
    msgid      = header["msgid"]
    userid     = header.get("userid", "OBSFLEXIN")
    branch     = header["branch"]
    entity     = header["entity"]
    module_id  = header.get("module_id", "PM")
    service    = header.get("service", "PMBookService")
    operation  = header.get("operation", "CreateBook")
    function_id= header.get("function_id", "PBDOTONL")
    action     = header.get("action", "NEW")

    b = body
    charge_block = ""
    if b.get("charge_component") is not None and b.get("charge_amount") is not None:
        charge_block = f"""
          <pmb:Brn-Out-Txn-Chg>
            <pmb:COMPONENT_NAME>{_xml_escape(str(b['charge_component']))}</pmb:COMPONENT_NAME>
            <pmb:AMOUNT>{_xml_escape(str(b['charge_amount']))}</pmb:AMOUNT>
          </pmb:Brn-Out-Txn-Chg>
        """

    xml = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:pmb="http://pmts.ofss.com/ws/PMBookService">
  <soapenv:Header/>
  <soapenv:Body>
    <pmb:CREATEBOOK_FSFS_REQ>
      <pmb:FCUBS_HEADER>
        <pmb:SOURCE>{_xml_escape(str(source))}</pmb:SOURCE>
        <pmb:UBSCOMP>{_xml_escape(str(ubscomp))}</pmb:UBSCOMP>
        <pmb:MSGID>{_xml_escape(str(msgid))}</pmb:MSGID>
        <pmb:USERID>{_xml_escape(str(userid))}</pmb:USERID>
        <pmb:BRANCH>{_xml_escape(str(branch))}</pmb:BRANCH>
        <pmb:ENTITY>{_xml_escape(str(entity))}</pmb:ENTITY>
        <pmb:MODULEID>{_xml_escape(str(module_id))}</pmb:MODULEID>
        <pmb:SERVICE>{_xml_escape(str(service))}</pmb:SERVICE>
        <pmb:OPERATION>{_xml_escape(str(operation))}</pmb:OPERATION>
        <pmb:FUNCTIONID>{_xml_escape(str(function_id))}</pmb:FUNCTIONID>
        <pmb:ACTION>{_xml_escape(str(action))}</pmb:ACTION>
      </pmb:FCUBS_HEADER>
      <pmb:FCUBS_BODY>
        <pmb:Brn-Out-Txn-Full>
          <pmb:TXN_VALUE_DATE>{_xml_escape(str(b['txn_value_date']))}</pmb:TXN_VALUE_DATE>
          <pmb:NETWORK_CODE>{_xml_escape(str(b['network_code']))}</pmb:NETWORK_CODE>
          <pmb:SOURCE_REF_NO>{_xml_escape(str(b['source_ref_no']))}</pmb:SOURCE_REF_NO>
          <pmb:SOURCE_CODE>{_xml_escape(str(b['source_code']))}</pmb:SOURCE_CODE>
          <pmb:TXN_BRANCH>{_xml_escape(str(b['txn_branch']))}</pmb:TXN_BRANCH>
          <pmb:HOST_CODE>{_xml_escape(str(b['host_code']))}</pmb:HOST_CODE>
          <pmb:DR_AC_NO>{_xml_escape(str(b['dr_ac_no']))}</pmb:DR_AC_NO>
          <pmb:CR_AC_NO>{_xml_escape(str(b['cr_ac_no']))}</pmb:CR_AC_NO>
          <pmb:CR_AC_CCY>{_xml_escape(str(b['cr_ac_ccy']))}</pmb:CR_AC_CCY>
          <pmb:CR_AMT>{_xml_escape(str(b['cr_amt']))}</pmb:CR_AMT>
          <pmb:INSTRUCTION_DATE>{_xml_escape(str(b['instruction_date']))}</pmb:INSTRUCTION_DATE>
          <pmb:REMARKS>{_xml_escape(str(b.get('remarks','')))}</pmb:REMARKS>
          {charge_block}
        </pmb:Brn-Out-Txn-Full>
      </pmb:FCUBS_BODY>
    </pmb:CREATEBOOK_FSFS_REQ>
  </soapenv:Body>
</soapenv:Envelope>"""
    # Only log (redacted) body at DEBUG to avoid dumping secrets in prod logs
    if SOAP_DEBUG:
        logger.debug("PMBook SOAP Request XML:\n%s", _redact(xml))
    return xml

def _parse_pm_book_response(xml_text: str) -> dict:
    out = {"msgstat": None, "txn_ref_no": None, "user_ref_no": None}
    try:
        m = re.search(r"<MSGSTAT>\s*(.*?)\s*</MSGSTAT>", xml_text, flags=re.I | re.S)
        if m: out["msgstat"] = m.group(1).strip()

        m = re.search(r"<TXN_REF_NO>\s*(.*?)\s*</TXN_REF_NO>", xml_text, flags=re.I | re.S)
        if m: out["txn_ref_no"] = m.group(1).strip()

        m = re.search(r"<USER_REF_NO>\s*(.*?)\s*</USER_REF_NO>", xml_text, flags=re.I | re.S)
        if m: out["user_ref_no"] = m.group(1).strip()

        if not out["msgstat"]:
            soup = BS(xml_text, features="xml")
            node = soup.find(lambda tag: tag.name and tag.name.upper() == "MSGSTAT")
            if node and node.text:
                out["msgstat"] = node.text.strip()
    except Exception as e:
        logger.warning("Response parse error: %s", e)
    return out

@celery_app.task(
    autoretry_for=(requests.RequestException, cx_Oracle.DatabaseError),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_to_flexcube_pm_book(
    settle_pm_book_id: int,
    request_json: dict,
    *,
    flexcube_url: str | None = None,
    header_overrides: dict | None = None,
    system_url: str | None = None,
):
    logger.info("PMBook task started id=%s", settle_pm_book_id)

    flexcube_url = flexcube_url or FLEXCUBE_DEFAULT_URL
    if not flexcube_url:
        logger.error("FLEXCUBE_URL is not set")
        return

    header = {
        "source": "FCAT",
        "ubscomp": "FCUBS",
        "msgid": request_json["msgid"],
        "userid": "OBSFLEXIN",
        "branch": request_json["branch"],
        "entity": request_json["entity"],
        "module_id": "PM",
        "service": "PMBookService",
        "operation": "CreateBook",
        "function_id": "PBDOTONL",
        "action": "NEW",
    }
    if header_overrides:
        header.update(header_overrides)

    body = {
        "txn_value_date": request_json["txn_value_date"],
        "network_code": request_json["network_code"],
        "source_ref_no": "OBS",
        "source_code": request_json["source_code"],
        "txn_branch": request_json["branch"],
        "host_code": request_json["host_code"],
        "dr_ac_no": request_json["dr_ac_no"],
        "cr_ac_no": request_json["cr_ac_no"],
        "cr_ac_ccy": request_json["cr_ac_ccy"],
        "cr_amt": request_json["cr_amt"],
        "instruction_date": request_json["instruction_date"],
        "remarks": request_json.get("remarks", ""),
        "charge_component": request_json.get("charge_component"),
        "charge_amount": request_json.get("charge_amount"),
    }

    request_xml = _soap_pm_book_xml(header, body)
    sent_at = datetime.now()

    try:
        # --- HTTP call
        resp = requests.post(
            flexcube_url,
            data=request_xml,
            headers={"Content-Type": "text/xml"},
            timeout=FLEXCUBE_TIMEOUT_S,
            verify=FLEXCUBE_VERIFY_SSL,
        )
        resp.raise_for_status()
        response_text = resp.text
        logger.info("PMBook SOAP HTTP %s", resp.status_code)
        if SOAP_DEBUG:
            logger.debug("PMBook SOAP Response XML:\n%s", _redact(response_text))

        # --- Parse & map status
        parsed = _parse_pm_book_response(response_text)
        msgstat = (parsed.get("msgstat") or "").upper()
        if msgstat == "SUCCESS":
            status = Status.SUCCESS
        elif msgstat == "FAILURE":
            status = Status.FAIL
        else:
            status = Status.ERROR

        # --- DB update
        con = cx_Oracle.connect(
            user=DB_USERNAME, 
            password=DB_PASSWORD,
            dsn=DB_DSN,
            encoding="UTF-8",
        )
        
        try:
            cur = con.cursor()
            sql = """
            UPDATE SETTLE_PM_BOOK
               SET FLEXCUBE_CONTENT = :request_body,
                   FLEXCUBE_MESSAGE = :response_body,
                   FLEXCUBE_RESPONSE_STATUS_ID = :resp_status_id,
                   FLEXCUBE_RESPONSE_AT = :resp_at,
                   SETTLEMENT_STATUS_ID = :resp_status_id,
                   UPDATED_AT = :updated_at,
                   SENT_AT = :sent_at,
                   MSGSTAT = :msgstat,
                   TXN_REF_NO = :txn_ref_no,
                   USER_REF_NO = :user_ref_no,
                   DR_AC_NO = :dr_ac_no,
                   CR_AC_NO = :cr_ac_no,
                   TRANSACTION_AMOUNT = :txn_amt,
                   TRANSACTION_CURRENCY = :txn_ccy
             WHERE SETTLE_PM_BOOK_ID = :id
            """
            cur.execute(
                sql,
                {
                    "request_body": request_xml,
                    "response_body": response_text,
                    "resp_status_id": int(status),
                    "resp_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "sent_at": sent_at,
                    "msgstat": parsed.get("msgstat"),
                    "txn_ref_no": parsed.get("txn_ref_no"),
                    "user_ref_no": parsed.get("user_ref_no"),
                    "dr_ac_no": body["dr_ac_no"],
                    "cr_ac_no": body["cr_ac_no"],
                    # DECIMAL → string for cx_Oracle binding
                    "txn_amt": str(body["cr_amt"]),
                    "txn_ccy": body["cr_ac_ccy"],
                    "id": settle_pm_book_id,
                },
            )
            con.commit()
            logger.info("PMBook DB updated id=%s status=%s (%d)", settle_pm_book_id, status.name, int(status))
        finally:
            try:
                cur.close()
            except Exception:
                pass
            try:
                con.close()
            except Exception:
                pass

    except requests.RequestException as http_err:
        logger.exception("HTTP error talking to Flexcube: %s", http_err)
        _mark_error_status(settle_pm_book_id)
        raise  # let Celery retry
    except cx_Oracle.DatabaseError as db_err:
        logger.exception("Oracle DB error: %s", db_err)
        _mark_error_status(settle_pm_book_id)
        raise  # let Celery retry
    except Exception as err:
        logger.exception("PMBook task error: %s", err)
        _mark_error_status(settle_pm_book_id)
        # Don't re-raise here (we've already updated status); remove raise to avoid infinite retries

    logger.info("PMBook task finished id=%s", settle_pm_book_id)

def _mark_error_status(settle_pm_book_id: int) -> None:
    """Best-effort DB mark as ERROR."""
    try:
        con = cx_Oracle.connect(
            user=DB_USERNAME,
            password=DB_PASSWORD,
            dsn=DB_DSN,
            encoding="UTF-8",
        )
        try:
            cur = con.cursor()
            cur.execute(
                """
                UPDATE SETTLE_PM_BOOK
                   SET FLEXCUBE_RESPONSE_STATUS_ID = :resp_status_id,
                       SETTLEMENT_STATUS_ID = :resp_status_id,
                       UPDATED_AT = :updated_at
                 WHERE SETTLE_PM_BOOK_ID = :id
                """,
                {
                    "resp_status_id": int(Status.ERROR),
                    "updated_at": datetime.now(),
                    "id": settle_pm_book_id,
                },
            )
            con.commit()
        finally:
            try: cur.close()
            except Exception: pass
            try: con.close()
            except Exception: pass
    except Exception:
        logger.warning("Failed to mark ERROR for id=%s", settle_pm_book_id)