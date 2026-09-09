
from datetime import datetime
from xml.sax.saxutils import escape
from settings import NCS_BKLV_SOAP_NAMESPACE , SOAP_ENV_NS
from xml.etree.ElementTree import Element, ParseError, SubElement, fromstring, tostring

PAIN001_NS = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.05"

class SoapFault(Exception):
    """Raised by handlers to signal that a SOAP Fault response should be returned."""

    def __init__(self, fault_string: str, fault_code: str = "Client"):
        super().__init__(fault_string)
        self.fault_string = fault_string
        self.fault_code = fault_code


def _local_name(tag: str) -> str:
    """Strip a '{namespace}Tag' qualified name down to 'Tag'."""
    return tag.split('}', 1)[-1] if '}' in tag else tag


def parse_operation(raw_xml: str):
    """
    Parse an incoming SOAP envelope and return (operation_name, params), where
    params is a dict of the operation element's immediate children keyed by
    local (namespace-stripped) tag name, values as stripped text.
    Raises SoapFault on malformed XML or a missing/empty Body.
    """
    if not raw_xml or not raw_xml.strip():
        raise SoapFault("Request body is empty")

    try:
        root = fromstring(raw_xml)
    except ParseError as err:
        raise SoapFault(f"Malformed SOAP XML: {err}") from err

    body = None
    for child in root:
        if _local_name(child.tag) == 'Body':
            body = child
            break
    if body is None or len(body) == 0:
        raise SoapFault("SOAP Body is missing or empty")

    operation_element = body[0]
    operation_name = _local_name(operation_element.tag)
    params = {
        _local_name(child.tag): (child.text or '').strip()
        for child in operation_element
    }
    return operation_name, params


def build_response_envelope(operation_name: str, result_name: str, result_value: str) -> str:
    """
    Build a SOAP 1.2 response envelope with a single <opResponse><result>value.
    Used by getFCDate and upload_File_GI_FLATFILE.
    """
    return (
        f'<soap:Envelope xmlns:soap="{SOAP_ENV_NS}">'
        f'<soap:Body>'
        f'<ws:{operation_name}Response xmlns:ws="{NCS_BKLV_SOAP_NAMESPACE}">'
        f'<ws:{result_name}>{escape(str(result_value))}</ws:{result_name}>'
        f'</ws:{operation_name}Response>'
        f'</soap:Body>'
        f'</soap:Envelope>'
    )

def build_account_balance_response(accounts: list) -> str:
    """
    Build getCBSAccountBalanceNCSResponse. accounts is a list of dicts with
    keys: bank_name, branch_code, account_number, cust_no, short_name,
    customer_name, description, account_class, ccy.
    """
    data = Element('DATA')
    for acct in accounts:
        cur_acc = SubElement(data, 'CUR_ACC')
        SubElement(cur_acc, 'BANK_NAME').text = acct.get('bank_name') or ''
        SubElement(cur_acc, 'BRANCH_CODE').text = acct.get('branch_code') or ''
        SubElement(cur_acc, 'ACCOUNT_NUMBER').text = acct.get('account_number') or ''
        SubElement(cur_acc, 'CUST_NO').text = acct.get('cust_no') or ''
        SubElement(cur_acc, 'SHORT_NAME').text = acct.get('short_name') or ''
        SubElement(cur_acc, 'CUSTOMER_NAME').text = acct.get('customer_name') or ''
        SubElement(cur_acc, 'DESCRIPTION').text = acct.get('description') or ''
        SubElement(cur_acc, 'ACCOUNT_CLASS').text = acct.get('account_class') or ''
        SubElement(cur_acc, 'BALANCE').text = acct.get('balance') or '0.00'
        SubElement(cur_acc, 'CCY').text = acct.get('ccy') or ''
    inner_xml = tostring(data, encoding='unicode')
    return build_response_envelope('getCBSAccountBalanceNCS', 'getCBSAccountBalanceNCSResult', inner_xml)

def build_fault_envelope(fault: SoapFault) -> str:
    """Build a SOAP 1.2 Fault envelope."""
    return (
        f'<soap:Envelope xmlns:soap="{SOAP_ENV_NS}">'
        f'<soap:Body>'
        f'<soap:Fault>'
        f'<soap:Code><soap:Value>soap:{escape(fault.fault_code)}</soap:Value></soap:Code>'
        f'<soap:Reason><soap:Text xml:lang="en">{escape(fault.fault_string)}</soap:Text></soap:Reason>'
        f'</soap:Fault>'
        f'</soap:Body>'
        f'</soap:Envelope>'
    )

def build_pain001_message(line: dict, msg_id: str) -> str:
    """
    Build an ISO 20022 pain.001.001.05 message from one structured netfile
    line, for handoff to the existing worker.bklv_tasks.send_to_bklv task —
    same iso_message shape the REST /bklv/transfer callers already provide
    themselves. Field set and element order follow BKLV's real
    makeFullFundTransfer sample request (GrpHdr/NbOfTxs/CtrlSum/InitgPty,
    PmtInf/PmtInfId/PmtMtd, DbtrAcct/Ccy, DbtrAgt/CdtrAgt BICFI,
    CdtTrfTxInf/PmtId/EndToEndId, RmtInf/Ustrd) — not just the minimal
    fields the earlier cut-down version carried.
    """
    amount = str(line.get('amount') or '0')
    currency = line.get('currency_code') or ''
    debtor_bic = line.get('debtor_bic') or ''
    creditor_bic = line.get('creditor_bic') or ''

    doc = Element('Document', {'xmlns': PAIN001_NS})
    cstmr = SubElement(doc, 'CstmrCdtTrfInitn')

    grp_hdr = SubElement(cstmr, 'GrpHdr')
    SubElement(grp_hdr, 'MsgId').text = msg_id
    SubElement(grp_hdr, 'CreDtTm').text = datetime.now().isoformat()
    SubElement(grp_hdr, 'NbOfTxs').text = '1'
    SubElement(grp_hdr, 'CtrlSum').text = amount
    SubElement(SubElement(grp_hdr, 'InitgPty'), 'Nm').text = line.get('debtor_name') or ''

    pmt_inf = SubElement(cstmr, 'PmtInf')
    SubElement(pmt_inf, 'PmtInfId').text = f'{debtor_bic}/{creditor_bic}/{msg_id}'
    SubElement(pmt_inf, 'PmtMtd').text = 'TRF'
    SubElement(pmt_inf, 'ReqdExctnDt').text = line.get('execution_date') or ''

    SubElement(SubElement(pmt_inf, 'Dbtr'), 'Nm').text = line.get('debtor_name') or ''

    dbtr_acct = SubElement(pmt_inf, 'DbtrAcct')
    dbtr_acct_othr = SubElement(SubElement(dbtr_acct, 'Id'), 'Othr')
    SubElement(dbtr_acct_othr, 'Id').text = line.get('debit_account') or ''
    SubElement(dbtr_acct, 'Ccy').text = currency

    if debtor_bic:
        SubElement(SubElement(SubElement(pmt_inf, 'DbtrAgt'), 'FinInstnId'), 'BICFI').text = debtor_bic

    cdt_trf = SubElement(pmt_inf, 'CdtTrfTxInf')
    SubElement(SubElement(cdt_trf, 'PmtId'), 'EndToEndId').text = msg_id

    instd_amt = SubElement(SubElement(cdt_trf, 'Amt'), 'InstdAmt', {'Ccy': currency})
    instd_amt.text = amount

    if creditor_bic:
        SubElement(SubElement(SubElement(cdt_trf, 'CdtrAgt'), 'FinInstnId'), 'BICFI').text = creditor_bic

    SubElement(SubElement(cdt_trf, 'Cdtr'), 'Nm').text = line.get('creditor_name') or ''

    cdtr_acct_othr = SubElement(SubElement(SubElement(cdt_trf, 'CdtrAcct'), 'Id'), 'Othr')
    SubElement(cdtr_acct_othr, 'Id').text = line.get('credit_account') or ''

    SubElement(SubElement(cdt_trf, 'RmtInf'), 'Ustrd').text = (
        line.get('remittance_info') or 'NCS Transaction Settlement'
    )

    return tostring(doc, encoding='unicode')

def build_status_detail_response(tran_no, file_name, tran_dte, tran_status,
                                  response_status, response_message, response_dte) -> str:
    """
    Build getFile_Status_DetailResponse. The Result element carries the
    <NewDataSet><status>...</status></NewDataSet> document as escaped text,
    same shape as the Flexcube-adapter PDF.
    """
    dataset = Element('NewDataSet')
    status_el = SubElement(dataset, 'status')
    SubElement(status_el, 'tran_no').text = str(tran_no)
    SubElement(status_el, 'batch_id').text = str(tran_no)
    SubElement(status_el, 'file_name').text = file_name
    SubElement(status_el, 'tran_dte').text = tran_dte
    SubElement(status_el, 'tran_status').text = tran_status
    SubElement(status_el, 'response_status').text = response_status
    SubElement(status_el, 'response_message').text = response_message or None
    SubElement(status_el, 'response_dte').text = response_dte
    SubElement(status_el, 'response_message_detail')
    inner_xml = '<?xml version="1.0" encoding="UTF-8"?>' + tostring(dataset, encoding='unicode')
    return build_response_envelope('getFile_Status_Detail', 'getFile_Status_DetailResult', inner_xml)
