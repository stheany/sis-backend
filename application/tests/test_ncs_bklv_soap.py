import json
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from xml.etree.ElementTree import fromstring

from flask import Flask

from application.routes.ncsBklvSoapRoute import ncs_bklv_soap_route
from application.services import ncsBklvSoapService as service
from application.utils.ncsBklvSoapXml import build_pain001_message


def _envelope(operation: str, **fields) -> str:
    body = ''.join(f'<ws:{key}>{value}</ws:{key}>' for key, value in fields.items())
    return (
        '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" '
        'xmlns:ws="http://sis.nbc.org.kh/ws/ncs-bklv">'
        f'<soap:Body><ws:{operation}>{body}</ws:{operation}></soap:Body>'
        '</soap:Envelope>'
    )


def _local(tag: str) -> str:
    return tag.split('}', 1)[-1] if '}' in tag else tag


def _find(root, local_name):
    for elem in root.iter():
        if _local(elem.tag) == local_name:
            return elem
    return None


def _find_in_result(response_xml: str, result_local_name: str, inner_local_name: str):
    """
    getCBSAccountBalanceNCSResult / getFile_Status_DetailResult carry their
    payload as an *escaped XML string* inside the result element's text, not
    as real child elements (matching the Flexcube-adapter PDF's shape) — so
    finding a field inside them means reading that text back out and parsing
    it a second time as its own document.
    """
    result_elem = _find(fromstring(response_xml), result_local_name)
    inner_root = fromstring(result_elem.text)
    return _find(inner_root, inner_local_name)


class NcsBklvSoapAuthTests(unittest.TestCase):
    """
    getFile_Status_Detail is used here as a stand-in "authenticated operation"
    — any op except getFCDate would do, since getFCDate is the one operation
    that takes no parameters at all (see GetFcDateTests below).
    """

    def test_missing_credentials_returns_soap_fault(self):
        xml = _envelope('getFile_Status_Detail', pTranNo='1', pFileName='x.txt')
        response = service.handle_ncs_bklv_soap_request(xml)
        self.assertIsNotNone(_find(fromstring(response), 'Fault'))

    def test_invalid_credentials_returns_soap_fault(self):
        xml = _envelope(
            'getFile_Status_Detail',
            pAuthCode='AUTH', pUserName='ncs', pUserPwd='wrong',
            pTranNo='1', pFileName='x.txt',
        )
        with patch.object(service.SystemLoginSisDao, 'get_system_login_sis_by_username', return_value=None):
            response = service.handle_ncs_bklv_soap_request(xml)
        self.assertIsNotNone(_find(fromstring(response), 'Fault'))

    def test_missing_auth_code_is_accepted_when_credentials_are_valid(self):
        """pAuthCode isn't required or checked — see ncsBklvSoapService._authenticate."""
        xml = _envelope(
            'getFile_Status_Detail',
            pUserName='ncs', pUserPwd='pw',
            pTranNo='1', pFileName='x.txt',
        )
        login_obj = SimpleNamespace(system_id=1, password='hashed')
        batch_obj = SimpleNamespace(
            settle_ncs_bklv_batch_id=1, file_name='x.txt',
            batch_status_id=service.STATUS_PENDING, created_at=datetime(2026, 8, 17, 9, 0, 0),
        )
        with patch.object(service.SystemLoginSisDao, 'get_system_login_sis_by_username', return_value=login_obj), \
             patch.object(service, 'verify_password', return_value=True), \
             patch.object(service.SettleNcsBklvBatchDao, 'get_by_id', return_value=batch_obj), \
             patch.object(service.SettleBklvDao, 'get_by_batch_id', return_value=[]):
            response = service.handle_ncs_bklv_soap_request(xml)
        self.assertIsNone(_find(fromstring(response), 'Fault'))


class GetFcDateTests(unittest.TestCase):
    def test_returns_current_business_date_with_no_parameters(self):
        """
        Matches the PDF exactly: getFCDate's sample request is a bare
        <ws:getFCDate/> with no credentials at all — it's the one call NCS
        makes before anything else is configured (startup health check), so
        it must succeed with zero parameters and no DAO/auth mocking.
        """
        xml = _envelope('getFCDate')
        response = service.handle_ncs_bklv_soap_request(xml)

        self.assertIsNone(_find(fromstring(response), 'Fault'))
        result = _find(fromstring(response), 'getFCDateResult')
        self.assertEqual(result.text, datetime.now().strftime('%m-%d-%Y'))


class GetCbsAccountBalanceTests(unittest.TestCase):
    def _run(self, systems, get_account_balance_side_effect):
        xml = _envelope('getCBSAccountBalanceNCS', pAuthCode='AUTH', pUser='ncs', pPassword='pw')
        login_obj = SimpleNamespace(system_id=1, password='hashed')
        with patch.object(service.SystemLoginSisDao, 'get_system_login_sis_by_username', return_value=login_obj), \
             patch.object(service, 'verify_password', return_value=True), \
             patch.object(service.SystemDao, 'get_systems_with_settlement_account', return_value=systems), \
             patch.object(service, 'get_account_balance', side_effect=get_account_balance_side_effect):
            response = service.handle_ncs_bklv_soap_request(xml)
        result_elem = _find(fromstring(response), 'getCBSAccountBalanceNCSResult')
        return fromstring(result_elem.text)

    def test_returns_only_active_registered_accounts(self):
        systems = [
            SimpleNamespace(system_name='ABA Bank', short_name='ABA', settlement_account_number='001',
                             status='1', bic_code='ABAAKHPPXXX'),
            SimpleNamespace(system_name='Old Bank', short_name='OLD', settlement_account_number='002',
                             status='0', bic_code='OLDXKHPPXXX'),
        ]
        inner_root = self._run(systems, get_account_balance_side_effect=lambda bic: {'balance': 12345.67, 'currency': 'USD'})
        account_numbers = [elem.text for elem in inner_root.iter() if _local(elem.tag) == 'ACCOUNT_NUMBER']
        self.assertEqual(account_numbers, ['001'])

    def test_uses_real_bklv_balance_when_available(self):
        systems = [
            SimpleNamespace(system_name='ABA Bank', short_name='ABA', settlement_account_number='001',
                             status='1', bic_code='ABAAKHPPXXX'),
        ]
        inner_root = self._run(systems, get_account_balance_side_effect=lambda bic: {'balance': 55000.5, 'currency': 'USD'})
        balances = [elem.text for elem in inner_root.iter() if _local(elem.tag) == 'BALANCE']
        self.assertEqual(balances, ['55000.50'])

    def test_uses_real_bklv_currency_when_available(self):
        systems = [
            SimpleNamespace(system_name='ABA Bank', short_name='ABA', settlement_account_number='001',
                             status='1', bic_code='ABAAKHPPXXX'),
        ]
        inner_root = self._run(systems, get_account_balance_side_effect=lambda bic: {'balance': 100.0, 'currency': 'USD'})
        currencies = [elem.text for elem in inner_root.iter() if _local(elem.tag) == 'CCY']
        self.assertEqual(currencies, ['USD'])

    def test_falls_back_to_zero_when_bklv_call_fails(self):
        """Non-blocking per the PDF: a failed sync just waits for next time, doesn't fault the whole response."""
        systems = [
            SimpleNamespace(system_name='ABA Bank', short_name='ABA', settlement_account_number='001',
                             status='1', bic_code='ABAAKHPPXXX'),
        ]

        def _raise(bic):
            raise service.BklvClientError("boom")

        inner_root = self._run(systems, get_account_balance_side_effect=_raise)
        balances = [elem.text for elem in inner_root.iter() if _local(elem.tag) == 'BALANCE']
        currencies = [elem.text for elem in inner_root.iter() if _local(elem.tag) == 'CCY']
        self.assertEqual(balances, ['0.00'])
        self.assertEqual(currencies, [None])

    def test_falls_back_to_zero_when_bic_code_missing(self):
        systems = [
            SimpleNamespace(system_name='ABA Bank', short_name='ABA', settlement_account_number='001',
                             status='1', bic_code=None),
        ]
        inner_root = self._run(systems, get_account_balance_side_effect=lambda bic: {'balance': 999.0, 'currency': 'USD'})
        balances = [elem.text for elem in inner_root.iter() if _local(elem.tag) == 'BALANCE']
        self.assertEqual(balances, ['0.00'])


class UploadNetfileTests(unittest.TestCase):
    def setUp(self):
        self.login_obj = SimpleNamespace(system_id=7, password='hashed')
        self.lines = [
            {
                'currency_code': 'USD', 'debit_account': 'DR1', 'credit_account': 'CR1',
                'amount': '100.00', 'debtor_name': 'ABA Bank', 'creditor_name': 'Acleda Bank',
                'debtor_bic': 'ABAAKHPPXXX', 'creditor_bic': 'ACLEDAPPXXX',
                'execution_date': '2026-08-17',
            },
            {
                'currency_code': 'USD', 'debit_account': 'DR2', 'credit_account': 'CR2',
                'amount': '50.00', 'debtor_name': 'ABA Bank', 'creditor_name': 'Wing Bank',
                'debtor_bic': 'ABAAKHPPXXX', 'creditor_bic': 'WINGKHPPXXX',
                'execution_date': '2026-08-17',
            },
        ]
        content = json.dumps(self.lines)
        self.xml = _envelope(
            'upload_File_GI_FLATFILE',
            pAuthCode='AUTH', pUserName='ncs', pUserPwd='pw',
            pFileName='NET-000TEST0001.txt', pContent=content.replace('<', '&lt;').replace('>', '&gt;'),
        )

    def test_creates_batch_and_dispatches_one_task_per_line(self):
        batch_obj = SimpleNamespace(settle_ncs_bklv_batch_id=55)
        settle_bklv_objs = [SimpleNamespace(settle_bklv_id=101), SimpleNamespace(settle_bklv_id=102)]

        with patch.object(service.SystemLoginSisDao, 'get_system_login_sis_by_username', return_value=self.login_obj), \
             patch.object(service, 'verify_password', return_value=True), \
             patch.object(service.SettleNcsBklvBatchDao, 'get_by_file_name', return_value=None), \
             patch.object(service, 'SettleNcsBklvBatch', return_value=batch_obj), \
             patch.object(service, 'SettleBklv', side_effect=settle_bklv_objs), \
             patch.object(service.db, 'session', MagicMock()), \
             patch.object(service, '_send_task_bklv_with_balance_check') as mock_send_task:
            response = service.handle_ncs_bklv_soap_request(self.xml)

        result = _find(fromstring(response), 'upload_File_GI_FLATFILEResult')
        self.assertEqual(result.text, '55')
        self.assertEqual(mock_send_task.call_count, 2)
        # Each line's own debtor_bic/amount are what get balance-checked —
        # not the plain send_to_bklv task, and not a shared/default value.
        self.assertEqual(mock_send_task.call_args_list[0].kwargs['debtor_bic'], 'ABAAKHPPXXX')
        self.assertEqual(mock_send_task.call_args_list[0].kwargs['amount'], 100.00)
        self.assertEqual(mock_send_task.call_args_list[1].kwargs['amount'], 50.00)

    def test_missing_debtor_bic_returns_soap_fault(self):
        """debtor_bic/creditor_bic are required — see _REQUIRED_LINE_FIELDS."""
        lines = [dict(self.lines[0])]
        del lines[0]['debtor_bic']
        xml = _envelope(
            'upload_File_GI_FLATFILE',
            pAuthCode='AUTH', pUserName='ncs', pUserPwd='pw',
            pFileName='NET-NO-BIC.txt', pContent=json.dumps(lines),
        )
        with patch.object(service.SystemLoginSisDao, 'get_system_login_sis_by_username', return_value=self.login_obj), \
             patch.object(service, 'verify_password', return_value=True), \
             patch.object(service.SettleNcsBklvBatchDao, 'get_by_file_name', return_value=None):
            response = service.handle_ncs_bklv_soap_request(xml)

        fault = _find(fromstring(response), 'Fault')
        self.assertIsNotNone(fault)
        self.assertIn('debtor_bic', response)

    def test_duplicate_file_name_returns_soap_fault(self):
        with patch.object(service.SystemLoginSisDao, 'get_system_login_sis_by_username', return_value=self.login_obj), \
             patch.object(service, 'verify_password', return_value=True), \
             patch.object(service.SettleNcsBklvBatchDao, 'get_by_file_name', return_value=SimpleNamespace()):
            response = service.handle_ncs_bklv_soap_request(self.xml)

        self.assertIsNotNone(_find(fromstring(response), 'Fault'))


class GetFileStatusDetailTests(unittest.TestCase):
    def _run(self, statuses):
        xml = _envelope(
            'getFile_Status_Detail',
            pAuthCode='AUTH', pUserName='ncs', pUserPwd='pw',
            pTranNo='55', pFileName='NET-000TEST0001.txt',
        )
        login_obj = SimpleNamespace(system_id=7, password='hashed')
        batch_obj = SimpleNamespace(
            settle_ncs_bklv_batch_id=55, file_name='NET-000TEST0001.txt',
            batch_status_id=service.STATUS_PENDING, created_at=datetime(2026, 8, 17, 9, 0, 0),
            updated_at=None,
        )
        lines = [SimpleNamespace(settlement_status_id=s, ext_ref=f'ref-{i}') for i, s in enumerate(statuses)]

        with patch.object(service.SystemLoginSisDao, 'get_system_login_sis_by_username', return_value=login_obj), \
             patch.object(service, 'verify_password', return_value=True), \
             patch.object(service.SettleNcsBklvBatchDao, 'get_by_id', return_value=batch_obj), \
             patch.object(service.SettleBklvDao, 'get_by_batch_id', return_value=lines), \
             patch.object(service.db, 'session', MagicMock()):
            response = service.handle_ncs_bklv_soap_request(xml)

        return _find_in_result(response, 'getFile_Status_DetailResult', 'response_status').text

    def test_any_pending_line_reports_waiting(self):
        self.assertEqual(self._run([service.STATUS_SUCCESS, service.STATUS_PENDING]), 'Waiting')

    def test_any_failed_line_once_resolved_reports_error(self):
        self.assertEqual(self._run([service.STATUS_SUCCESS, service.STATUS_FAIL]), 'Error')

    def test_all_succeeded_reports_processed(self):
        self.assertEqual(self._run([service.STATUS_SUCCESS, service.STATUS_SUCCESS]), 'Processed')

    def test_unknown_tran_no_returns_soap_fault(self):
        xml = _envelope(
            'getFile_Status_Detail',
            pAuthCode='AUTH', pUserName='ncs', pUserPwd='pw',
            pTranNo='999', pFileName='NET-000TEST0001.txt',
        )
        login_obj = SimpleNamespace(system_id=7, password='hashed')
        with patch.object(service.SystemLoginSisDao, 'get_system_login_sis_by_username', return_value=login_obj), \
             patch.object(service, 'verify_password', return_value=True), \
             patch.object(service.SettleNcsBklvBatchDao, 'get_by_id', return_value=None):
            response = service.handle_ncs_bklv_soap_request(xml)

        self.assertIsNotNone(_find(fromstring(response), 'Fault'))


class BuildPain001MessageTests(unittest.TestCase):
    """
    build_pain001_message must produce every field BKLV's real
    makeFullFundTransfer sample marks REQUIRED (Dbtr/Nm, DbtrAcct/Id+Ccy,
    PmtMtd, ReqdExctnDt, Amt/InstdAmt, Cdtr/Nm, CdtrAcct/Id, RmtInf/Ustrd),
    plus the optional BIC/PmtInfId/EndToEndId structure BKLV's sample also
    carries — not just the minimal subset the first cut of this builder had.
    """

    def setUp(self):
        self.line = {
            'currency_code': 'KHR', 'debit_account': '015039685739105',
            'credit_account': '000886653481654', 'amount': '800',
            'debtor_name': 'TEST', 'creditor_name': 'TEST',
            'execution_date': '2019-10-14',
            'debtor_bic': 'NBHQKHPP', 'creditor_bic': 'DEVBKHPP',
            'remittance_info': 'TRANSFER/AAAA0001',
        }
        self.xml = build_pain001_message(self.line, msg_id='AAAA0002')
        self.root = fromstring(self.xml)

    def _text(self, path_local_names):
        """Walk local (namespace-stripped) tag names down from the root."""
        node = self.root
        for name in path_local_names:
            node = next(child for child in node if _local(child.tag) == name)
        return node.text

    def test_required_fields_present(self):
        self.assertEqual(self._text(['CstmrCdtTrfInitn', 'GrpHdr', 'MsgId']), 'AAAA0002')
        self.assertEqual(self._text(['CstmrCdtTrfInitn', 'PmtInf', 'PmtMtd']), 'TRF')
        self.assertEqual(self._text(['CstmrCdtTrfInitn', 'PmtInf', 'ReqdExctnDt']), '2019-10-14')
        self.assertEqual(self._text(['CstmrCdtTrfInitn', 'PmtInf', 'Dbtr', 'Nm']), 'TEST')
        self.assertEqual(
            self._text(['CstmrCdtTrfInitn', 'PmtInf', 'DbtrAcct', 'Id', 'Othr', 'Id']),
            '015039685739105',
        )
        self.assertEqual(self._text(['CstmrCdtTrfInitn', 'PmtInf', 'DbtrAcct', 'Ccy']), 'KHR')
        self.assertEqual(
            self._text(['CstmrCdtTrfInitn', 'PmtInf', 'CdtTrfTxInf', 'Cdtr', 'Nm']), 'TEST',
        )
        self.assertEqual(
            self._text(['CstmrCdtTrfInitn', 'PmtInf', 'CdtTrfTxInf', 'CdtrAcct', 'Id', 'Othr', 'Id']),
            '000886653481654',
        )
        self.assertEqual(
            self._text(['CstmrCdtTrfInitn', 'PmtInf', 'CdtTrfTxInf', 'RmtInf', 'Ustrd']),
            'TRANSFER/AAAA0001',
        )

    def test_amount_and_currency_on_instd_amt(self):
        instd_amt = self.root.find(
            './/{urn:iso:std:iso:20022:tech:xsd:pain.001.001.05}InstdAmt'
        )
        self.assertEqual(instd_amt.text, '800')
        self.assertEqual(instd_amt.get('Ccy'), 'KHR')

    def test_bics_included_when_provided(self):
        self.assertEqual(
            self._text(['CstmrCdtTrfInitn', 'PmtInf', 'DbtrAgt', 'FinInstnId', 'BICFI']),
            'NBHQKHPP',
        )
        self.assertEqual(
            self._text(['CstmrCdtTrfInitn', 'PmtInf', 'CdtTrfTxInf', 'CdtrAgt', 'FinInstnId', 'BICFI']),
            'DEVBKHPP',
        )
        self.assertEqual(self._text(['CstmrCdtTrfInitn', 'PmtInf', 'PmtInfId']), 'NBHQKHPP/DEVBKHPP/AAAA0002')
        self.assertEqual(
            self._text(['CstmrCdtTrfInitn', 'PmtInf', 'CdtTrfTxInf', 'PmtId', 'EndToEndId']),
            'AAAA0002',
        )

    def test_bics_omitted_when_not_provided(self):
        """DbtrAgt/CdtrAgt aren't marked REQUIRED in BKLV's sample — must not fabricate a BIC."""
        line = dict(self.line)
        del line['debtor_bic']
        del line['creditor_bic']
        xml = build_pain001_message(line, msg_id='AAAA0003')
        root = fromstring(xml)
        self.assertIsNone(root.find('.//{urn:iso:std:iso:20022:tech:xsd:pain.001.001.05}DbtrAgt'))
        self.assertIsNone(root.find('.//{urn:iso:std:iso:20022:tech:xsd:pain.001.001.05}CdtrAgt'))

    def test_remittance_info_defaults_when_omitted(self):
        line = dict(self.line)
        del line['remittance_info']
        xml = build_pain001_message(line, msg_id='AAAA0004')
        root = fromstring(xml)
        ustrd = root.find('.//{urn:iso:std:iso:20022:tech:xsd:pain.001.001.05}Ustrd')
        self.assertEqual(ustrd.text, 'NCS Transaction Settlement')


class OperationUrlMismatchTests(unittest.TestCase):
    """
    Each route in ncsBklvSoapRoute.py now passes its own operation name as
    expected_operation — a body posted to the wrong per-operation URL faults
    instead of silently running whatever operation the body itself claims.
    """

    def test_matching_operation_is_unaffected(self):
        xml = _envelope('getFCDate')
        response = service.handle_ncs_bklv_soap_request(xml, expected_operation='getFCDate')
        self.assertIsNone(_find(fromstring(response), 'Fault'))

    def test_mismatched_operation_returns_soap_fault(self):
        xml = _envelope('getCBSAccountBalanceNCS', pAuthCode='AUTH', pUser='ncs', pPassword='pw')
        response = service.handle_ncs_bklv_soap_request(xml, expected_operation='getFCDate')
        fault = _find(fromstring(response), 'Fault')
        self.assertIsNotNone(fault)
        self.assertIn('getFCDate', response)
        self.assertIn('getCBSAccountBalanceNCS', response)

    def test_no_expected_operation_dispatches_off_body_alone(self):
        """Backward-compatible default: expected_operation is optional."""
        xml = _envelope('getFCDate')
        response = service.handle_ncs_bklv_soap_request(xml)
        self.assertIsNone(_find(fromstring(response), 'Fault'))


class NcsBklvSoapRouteTests(unittest.TestCase):
    """
    Exercises application/routes/ncsBklvSoapRoute.py itself (not just the
    service function directly) — registers the blueprint on a bare Flask
    app, no application/__init__.py, no DB.
    """

    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(ncs_bklv_soap_route)
        app.testing = True
        self.client = app.test_client()

    def test_all_four_operations_are_routed(self):
        rules = {r.rule for r in self.client.application.url_map.iter_rules()}
        for op in ('getFCDate', 'getCBSAccountBalanceNCS', 'upload_File_GI_FLATFILE', 'getFile_Status_Detail'):
            self.assertIn(f'/ws/{op}', rules)

    def test_get_fc_date_route_returns_success(self):
        response = self.client.post(
            '/ws/getFCDate',
            data=_envelope('getFCDate'),
            content_type='text/xml; charset=utf-8',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(_find(fromstring(response.get_data(as_text=True)), 'Fault'))

    def test_wrong_body_on_get_fc_date_route_returns_soap_fault(self):
        """A getCBSAccountBalanceNCS body posted to the getFCDate URL — client misconfiguration."""
        response = self.client.post(
            '/ws/getFCDate',
            data=_envelope('getCBSAccountBalanceNCS', pAuthCode='AUTH', pUser='ncs', pPassword='pw'),
            content_type='text/xml; charset=utf-8',
        )
        self.assertEqual(response.status_code, 200)  # SOAP faults are still HTTP 200
        self.assertIsNotNone(_find(fromstring(response.get_data(as_text=True)), 'Fault'))


if __name__ == '__main__':
    unittest.main()
