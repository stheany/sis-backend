import os
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import requests
from flask import Flask

from application.services import bklvTransferService as service
from worker import bklv_tasks


class BklvTransferScenarioTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.created_at = datetime(2026, 3, 30, 10, 15, 0)
        self.payload = {
            "ext_ref": "ABA-ACLEDA-USD-500-001",
            "source_bank": "ABA Bank",
            "destination_bank": "Acleda Bank",
            "debit_account": "001234567890",
            "amount": 500.0,
            "currency": "USD",
            "iso_message": (
                "<Document xmlns=\"urn:iso:std:iso:20022:tech:xsd:pain.001.001.05\">"
                "<CstmrCdtTrfInitn>"
                "<GrpHdr><MsgId>ABA-ACLEDA-USD-500-001</MsgId></GrpHdr>"
                "<PmtInf><CdtTrfTxInf><Amt><InstdAmt Ccy=\"USD\">500</InstdAmt></Amt>"
                "</CdtTrfTxInf></PmtInf>"
                "</CstmrCdtTrfInitn>"
                "</Document>"
            ),
        }
        
        

    def test_bklv_transfer_returns_pending_for_registered_banks(self):
        settle_bklv_obj = SimpleNamespace(
            settle_bklv_id=101,
            created_at=self.created_at,
        )
        mock_session = MagicMock()

        with self.app.test_request_context(json=self.payload):
            with patch.object(service.SettleBklvDao, "get_settle_bklv_by_ext_ref", return_value=None), \
                 patch.object(service, "_get_active_system_by_name", side_effect=[SimpleNamespace(), SimpleNamespace()]), \
                 patch.object(service, "get_jwt_identity", return_value=1), \
                 patch.object(service, "SettleBklv", return_value=settle_bklv_obj), \
                 patch.object(service.db, "session", mock_session), \
                 patch.object(service.SystemDao, "get_system_by_id", return_value=SimpleNamespace(url="https://aba.example.local")), \
                 patch.object(service, "send_task_bklv") as mock_send_task:
                response = service.bklv_transfer_post()

        response_body = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body["detail"]["data"]["id"], 101)
        self.assertEqual(response_body["detail"]["data"]["ext_ref"], self.payload["ext_ref"])
        self.assertEqual(response_body["detail"]["data"]["settlement_status"], "PENDING")
        mock_session.add.assert_called_once_with(settle_bklv_obj)
        mock_session.flush.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        mock_send_task.assert_called_once_with(
            system_url="https://aba.example.local",
            settle_bklv_id=101,
            ext_ref=self.payload["ext_ref"],
            iso_message=self.payload["iso_message"],
        )

    def test_bklv_transfer_rejects_unregistered_destination_bank(self):
        with self.app.test_request_context(json=self.payload):
            with patch.object(service.SettleBklvDao, "get_settle_bklv_by_ext_ref", return_value=None), \
                 patch.object(service, "_get_active_system_by_name", side_effect=[SimpleNamespace(), None]):
                response = service.bklv_transfer_post()

        response_body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body["detail"]["error_code"], 42)
        self.assertIn("Destination bank 'Acleda Bank'", response_body["detail"]["error_message"])


    # ------------------------------------------------------------------
    # Payload validation
    # ------------------------------------------------------------------

    def test_no_request_body_returns_400(self):
        """Empty body must be rejected before schema validation."""
        with self.app.test_request_context(data=b"", content_type="application/json"):
            response = service.bklv_transfer_post()
        self.assertEqual(response.status_code, 400)

    def test_missing_required_fields_return_400(self):
        """Every required field must be present; omitting any one fails with 400."""
        required_fields = [
            "ext_ref", "source_bank", "destination_bank",
            "debit_account", "amount", "currency", "iso_message",
        ]
        for field in required_fields:
            with self.subTest(missing_field=field):
                payload = {k: v for k, v in self.payload.items() if k != field}
                with self.app.test_request_context(json=payload):
                    response = service.bklv_transfer_post()
                body = response.get_json()
                self.assertEqual(response.status_code, 400, msg=f"Expected 400 for missing '{field}'")
                self.assertIn(field, body["detail"]["error_message"])

    def test_invalid_currency_returns_400(self):
        """Currency values outside USD/KHR must be rejected."""
        payload = {**self.payload, "currency": "EUR"}
        with self.app.test_request_context(json=payload):
            response = service.bklv_transfer_post()
        self.assertEqual(response.status_code, 400)
        self.assertIn("currency", response.get_json()["detail"]["error_message"])

    def test_zero_amount_returns_400(self):
        """Amount must be greater than zero."""
        payload = {**self.payload, "amount": 0}
        with self.app.test_request_context(json=payload):
            response = service.bklv_transfer_post()
        self.assertEqual(response.status_code, 400)
        self.assertIn("amount", response.get_json()["detail"]["error_message"])

    def test_negative_amount_returns_400(self):
        """Negative amounts must be rejected."""
        payload = {**self.payload, "amount": -100}
        with self.app.test_request_context(json=payload):
            response = service.bklv_transfer_post()
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------
    # Business rule: bank registration
    # ------------------------------------------------------------------

    def test_source_bank_not_registered_returns_400(self):
        """Source bank (ABA) must be registered and active in SYSTEM table."""
        with self.app.test_request_context(json=self.payload):
            with patch.object(service.SettleBklvDao, "get_settle_bklv_by_ext_ref", return_value=None), \
                 patch.object(service, "_get_active_system_by_name", return_value=None):
                response = service.bklv_transfer_post()
        body = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(body["detail"]["error_code"], 41)
        self.assertIn("ABA Bank", body["detail"]["error_message"])
        self.assertIn("not registered or not active", body["detail"]["error_message"])

    def test_destination_bank_not_registered_returns_400(self):
        """Destination bank (Acleda) must be registered and active in SYSTEM table."""
        with self.app.test_request_context(json=self.payload):
            with patch.object(service.SettleBklvDao, "get_settle_bklv_by_ext_ref", return_value=None), \
                 patch.object(service, "_get_active_system_by_name", side_effect=[SimpleNamespace(), None]):
                response = service.bklv_transfer_post()
        body = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(body["detail"]["error_code"], 42)
        self.assertIn("Acleda Bank", body["detail"]["error_message"])

    # ------------------------------------------------------------------
    # Idempotency (ext_ref deduplication)
    # ------------------------------------------------------------------

    def test_idempotency_returns_existing_pending_record(self):
        """A duplicate ext_ref with PENDING status returns the original record."""
        existing = SimpleNamespace(
            settle_bklv_id=77,
            ext_ref=self.payload["ext_ref"],
            settlement_status_id=1,  # PENDING
            created_at=self.created_at,
        )
        with self.app.test_request_context(json=self.payload):
            with patch.object(service.SettleBklvDao, "get_settle_bklv_by_ext_ref", return_value=existing):
                response = service.bklv_transfer_post()
        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["detail"]["data"]["id"], 77)
        self.assertIn("Duplicate", body["detail"]["data"]["message"])

    def test_idempotency_returns_existing_success_record(self):
        """A duplicate ext_ref with SUCCESS status also returns the original record."""
        existing = SimpleNamespace(
            settle_bklv_id=88,
            ext_ref=self.payload["ext_ref"],
            settlement_status_id=2,  # SUCCESS
            created_at=self.created_at,
        )
        with self.app.test_request_context(json=self.payload):
            with patch.object(service.SettleBklvDao, "get_settle_bklv_by_ext_ref", return_value=existing):
                response = service.bklv_transfer_post()
        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["detail"]["data"]["id"], 88)
        self.assertEqual(body["detail"]["data"]["settlement_status"], "SUCCESS")

    def test_idempotency_allows_retry_on_failed_record(self):
        """A duplicate ext_ref with FAIL status allows a fresh retry."""
        existing_failed = SimpleNamespace(
            settle_bklv_id=77,
            ext_ref=self.payload["ext_ref"],
            settlement_status_id=3,  # FAIL
            created_at=self.created_at,
        )
        new_obj = SimpleNamespace(settle_bklv_id=102, created_at=self.created_at)
        mock_session = MagicMock()
        with self.app.test_request_context(json=self.payload):
            with patch.object(service.SettleBklvDao, "get_settle_bklv_by_ext_ref", return_value=existing_failed), \
                 patch.object(service, "_get_active_system_by_name", side_effect=[SimpleNamespace(), SimpleNamespace()]), \
                 patch.object(service, "get_jwt_identity", return_value=1), \
                 patch.object(service, "SettleBklv", return_value=new_obj), \
                 patch.object(service.db, "session", mock_session), \
                 patch.object(service.SystemDao, "get_system_by_id", return_value=SimpleNamespace(url=None)), \
                 patch.object(service, "send_task_bklv"):
                response = service.bklv_transfer_post()
        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["detail"]["data"]["id"], 102)
        self.assertEqual(body["detail"]["data"]["settlement_status"], "PENDING")

    # ------------------------------------------------------------------
    # Transaction record creation
    # ------------------------------------------------------------------

    def test_settlement_record_created_with_pending_status(self):
        """SettleBklv record must be persisted (add + flush + commit) with PENDING status."""
        settle_bklv_obj = SimpleNamespace(
            settle_bklv_id=101,
            created_at=self.created_at,
        )
        mock_session = MagicMock()
        with self.app.test_request_context(json=self.payload):
            with patch.object(service.SettleBklvDao, "get_settle_bklv_by_ext_ref", return_value=None), \
                 patch.object(service, "_get_active_system_by_name", side_effect=[SimpleNamespace(), SimpleNamespace()]), \
                 patch.object(service, "get_jwt_identity", return_value=1), \
                 patch.object(service, "SettleBklv", return_value=settle_bklv_obj), \
                 patch.object(service.db, "session", mock_session), \
                 patch.object(service.SystemDao, "get_system_by_id", return_value=SimpleNamespace(url=None)), \
                 patch.object(service, "send_task_bklv"):
                response = service.bklv_transfer_post()
        mock_session.add.assert_called_once_with(settle_bklv_obj)
        mock_session.flush.assert_called_once()
        mock_session.commit.assert_called_once()
        self.assertEqual(response.get_json()["detail"]["data"]["settlement_status"], "PENDING")

    def test_db_commit_failure_returns_500_and_rollback(self):
        """A DB error during commit must return 500 and rollback the session."""
        settle_bklv_obj = SimpleNamespace(settle_bklv_id=101, created_at=self.created_at)
        mock_session = MagicMock()
        mock_session.commit.side_effect = Exception("Oracle commit error")
        with self.app.test_request_context(json=self.payload):
            with patch.object(service.SettleBklvDao, "get_settle_bklv_by_ext_ref", return_value=None), \
                 patch.object(service, "_get_active_system_by_name", side_effect=[SimpleNamespace(), SimpleNamespace()]), \
                 patch.object(service, "get_jwt_identity", return_value=1), \
                 patch.object(service, "SettleBklv", return_value=settle_bklv_obj), \
                 patch.object(service.db, "session", mock_session):
                response = service.bklv_transfer_post()
        self.assertEqual(response.status_code, 500)
        mock_session.rollback.assert_called_once()

    # ------------------------------------------------------------------
    # Celery task dispatch
    # ------------------------------------------------------------------

    def test_celery_task_dispatched_with_correct_args(self):
        """After creating the record, a Celery task must be dispatched to BKLV."""
        settle_bklv_obj = SimpleNamespace(settle_bklv_id=101, created_at=self.created_at)
        mock_session = MagicMock()
        with self.app.test_request_context(json=self.payload):
            with patch.object(service.SettleBklvDao, "get_settle_bklv_by_ext_ref", return_value=None), \
                 patch.object(service, "_get_active_system_by_name", side_effect=[SimpleNamespace(), SimpleNamespace()]), \
                 patch.object(service, "get_jwt_identity", return_value=1), \
                 patch.object(service, "SettleBklv", return_value=settle_bklv_obj), \
                 patch.object(service.db, "session", mock_session), \
                 patch.object(service.SystemDao, "get_system_by_id",
                               return_value=SimpleNamespace(url="https://aba.example.local")), \
                 patch.object(service, "send_task_bklv") as mock_send_task:
                service.bklv_transfer_post()
        mock_send_task.assert_called_once_with(
            system_url="https://aba.example.local",
            settle_bklv_id=101,
            ext_ref=self.payload["ext_ref"],
            iso_message=self.payload["iso_message"],
        )


class BklvWorkerSoapTests(unittest.TestCase):
    def test_build_soap_envelope_uses_make_full_fund_transfer(self):
        request_xml = bklv_tasks._build_soap_envelope(
            username="aba-user",
            password="aba-pass",
            iso_message="<Document><Amount Ccy=\"USD\">500</Amount></Document>",
            ext_ref="ABA-ACLEDA-USD-500-001",
        )

        self.assertIn("<web:makeFullFundTransfer>", request_xml)
        self.assertIn("<web:cm_user_name>aba-user</web:cm_user_name>", request_xml)
        self.assertIn("<web:cm_password>aba-pass</web:cm_password>", request_xml)
        self.assertIn("<web:ext_ref>ABA-ACLEDA-USD-500-001</web:ext_ref>", request_xml)
        self.assertIn("<![CDATA[<Document><Amount Ccy=\"USD\">500</Amount></Document>]]>", request_xml)

    def test_build_soap_envelope_wraps_iso_message_in_cdata(self):
        """ISO 20022 XML must be wrapped in CDATA so special chars are preserved."""
        envelope = bklv_tasks._build_soap_envelope("u", "p", "<Msg>test & data</Msg>", "ref-001")
        self.assertIn("<![CDATA[<Msg>test & data</Msg>]]>", envelope)

    def test_build_soap_envelope_includes_nbc_namespace(self):
        """SOAP envelope must target the NBC webservice namespace."""
        envelope = bklv_tasks._build_soap_envelope("u", "p", "<Msg/>", "ref-001")
        self.assertIn('xmlns:web="http://webservice.nbc.org.kh/"', envelope)

    def test_build_soap_envelope_has_valid_soap_structure(self):
        """Envelope must contain required SOAP header and body elements."""
        envelope = bklv_tasks._build_soap_envelope("u", "p", "<Msg/>", "ref-001")
        self.assertIn("<soapenv:Envelope", envelope)
        self.assertIn("<soapenv:Header/>", envelope)
        self.assertIn("<soapenv:Body>", envelope)


class BklvResponseParsingTests(unittest.TestCase):
    """Unit tests for _parse_bklv_response — covers all response status branches."""

    def test_soap_fault_returns_fail(self):
        xml = "<soap:Fault><faultstring>Permission denied</faultstring></soap:Fault>"
        self.assertEqual(bklv_tasks._parse_bklv_response(xml), bklv_tasks.SETTLE_STATUS_FAIL)

    def test_soapenv_fault_returns_fail(self):
        xml = "<soapenv:Fault><faultstring>Invalid credentials</faultstring></soapenv:Fault>"
        self.assertEqual(bklv_tasks._parse_bklv_response(xml), bklv_tasks.SETTLE_STATUS_FAIL)

    def test_success_keyword_returns_success(self):
        xml = "<makeFullFundTransferResponse><return>success</return></makeFullFundTransferResponse>"
        self.assertEqual(bklv_tasks._parse_bklv_response(xml), bklv_tasks.SETTLE_STATUS_SUCCESS)

    def test_accepted_keyword_returns_success(self):
        xml = "<Status>Accepted</Status>"
        self.assertEqual(bklv_tasks._parse_bklv_response(xml), bklv_tasks.SETTLE_STATUS_SUCCESS)

    def test_fail_keyword_returns_fail(self):
        xml = "<makeFullFundTransferResponse><return>fail</return></makeFullFundTransferResponse>"
        self.assertEqual(bklv_tasks._parse_bklv_response(xml), bklv_tasks.SETTLE_STATUS_FAIL)

    def test_error_keyword_returns_fail(self):
        xml = "<Response><status>error</status><message>Insufficient funds</message></Response>"
        self.assertEqual(bklv_tasks._parse_bklv_response(xml), bklv_tasks.SETTLE_STATUS_FAIL)

    def test_reject_keyword_returns_fail(self):
        xml = "<Response><status>Rejected</status></Response>"
        self.assertEqual(bklv_tasks._parse_bklv_response(xml), bklv_tasks.SETTLE_STATUS_FAIL)

    def test_unknown_response_defaults_to_success(self):
        """When no known keyword is found and no SOAP fault, default to SUCCESS."""
        xml = "<makeFullFundTransferResponse><return>PROCESSING</return></makeFullFundTransferResponse>"
        self.assertEqual(bklv_tasks._parse_bklv_response(xml), bklv_tasks.SETTLE_STATUS_SUCCESS)


class BklvWorkerTaskTests(unittest.TestCase):
    """
    Integration-style unit tests for the send_to_bklv Celery task.
    Oracle DB and HTTP calls are fully mocked — no real connections required.

    Scenario: ABA Bank → SIS → BKLV (makeFullFundTransfer) → response parsed → DB updated
    """

    BASE_ISO = (
        '<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.05">'
        "<CstmrCdtTrfInitn>"
        "<GrpHdr><MsgId>ABA-ACLEDA-USD-500-001</MsgId></GrpHdr>"
        "<PmtInf><CdtTrfTxInf><Amt><InstdAmt Ccy=\"USD\">500</InstdAmt></Amt>"
        "</CdtTrfTxInf></PmtInf>"
        "</CstmrCdtTrfInitn></Document>"
    )
    BKLV_ENV = {
        "BKLV_SOAP_URL": "http://bklv.test.local/ws",
        "BKLV_USERNAME": "test-user",
        "BKLV_PASSWORD": "test-pass",
        "BKLV_VERIFY_SSL": "false",
        "BKLV_SOAP_TIMEOUT": "30",
    }

    def _make_mock_oracle(self):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_con.cursor.return_value = mock_cur
        return mock_con, mock_cur

    # ------------------------------------------------------------------
    # Step 6–8: SOAP dispatch → BKLV response → DB status update
    # ------------------------------------------------------------------

    @patch("worker.bklv_tasks.requests.post")
    @patch("worker.bklv_tasks.cx_Oracle.connect")
    def test_send_to_bklv_updates_db_with_success_on_success_response(self, mock_connect, mock_post):
        """BKLV returns 'success' → SETTLE_BKLV record updated with SUCCESS status."""
        mock_con, mock_cur = self._make_mock_oracle()
        mock_connect.return_value = mock_con
        mock_resp = MagicMock()
        mock_resp.content = b"<makeFullFundTransferResponse><return>success</return></makeFullFundTransferResponse>"
        mock_post.return_value = mock_resp

        with patch.dict(os.environ, self.BKLV_ENV), \
             patch("worker.bklv_tasks.update_system_status", return_value=True):
            bklv_tasks.send_to_bklv(
                system_url="http://aba.test.local/callback",
                settle_bklv_id=101,
                ext_ref="ABA-ACLEDA-USD-500-001",
                iso_message=self.BASE_ISO,
            )

        mock_cur.execute.assert_called_once()
        mock_con.commit.assert_called_once()
        execute_params = mock_cur.execute.call_args[0][1]
        self.assertEqual(execute_params["response_status"], 2)  # SUCCESS
        self.assertIn("ABA-ACLEDA-USD-500-001", mock_post.call_args[1].get("data", b"").decode())

    @patch("worker.bklv_tasks.requests.post")
    @patch("worker.bklv_tasks.cx_Oracle.connect")
    def test_send_to_bklv_updates_db_with_fail_on_soap_fault(self, mock_connect, mock_post):
        """BKLV returns a SOAP fault → SETTLE_BKLV record updated with FAIL status."""
        mock_con, mock_cur = self._make_mock_oracle()
        mock_connect.return_value = mock_con
        mock_resp = MagicMock()
        mock_resp.content = b"<soap:Fault><faultstring>Insufficient balance</faultstring></soap:Fault>"
        mock_post.return_value = mock_resp

        with patch.dict(os.environ, self.BKLV_ENV):
            bklv_tasks.send_to_bklv(
                system_url=None,
                settle_bklv_id=102,
                ext_ref="ABA-ACLEDA-USD-500-002",
                iso_message=self.BASE_ISO,
            )

        execute_params = mock_cur.execute.call_args[0][1]
        self.assertEqual(execute_params["response_status"], 3)  # FAIL

    @patch("worker.bklv_tasks.requests.post")
    @patch("worker.bklv_tasks.cx_Oracle.connect")
    def test_send_to_bklv_sets_error_status_on_timeout(self, mock_connect, mock_post):
        """BKLV SOAP request times out → SETTLE_BKLV updated with ERROR status."""
        mock_con, mock_cur = self._make_mock_oracle()
        mock_connect.return_value = mock_con
        mock_post.side_effect = requests.exceptions.Timeout()

        with patch.dict(os.environ, self.BKLV_ENV):
            bklv_tasks.send_to_bklv(
                system_url=None,
                settle_bklv_id=103,
                ext_ref="ABA-ACLEDA-USD-500-003",
                iso_message=self.BASE_ISO,
            )

        mock_cur.execute.assert_called_once()
        execute_params = mock_cur.execute.call_args[0][1]
        self.assertEqual(execute_params["status_id"], 4)  # ERROR

    @patch("worker.bklv_tasks.requests.post")
    @patch("worker.bklv_tasks.cx_Oracle.connect")
    def test_send_to_bklv_sets_error_status_on_connection_error(self, mock_connect, mock_post):
        """BKLV is unreachable → SETTLE_BKLV updated with ERROR status."""
        mock_con, mock_cur = self._make_mock_oracle()
        mock_connect.return_value = mock_con
        mock_post.side_effect = requests.exceptions.ConnectionError()

        with patch.dict(os.environ, self.BKLV_ENV):
            bklv_tasks.send_to_bklv(
                system_url=None,
                settle_bklv_id=104,
                ext_ref="ABA-ACLEDA-USD-500-004",
                iso_message=self.BASE_ISO,
            )

        execute_params = mock_cur.execute.call_args[0][1]
        self.assertEqual(execute_params["status_id"], 4)  # ERROR

    def test_send_to_bklv_aborts_early_when_bklv_url_not_configured(self):
        """Missing BKLV_SOAP_URL env var → task aborts and records ERROR without HTTP call."""
        with patch.dict(os.environ, {"BKLV_SOAP_URL": ""}), \
             patch("worker.bklv_tasks._update_settle_bklv_error") as mock_err_update, \
             patch("worker.bklv_tasks.cx_Oracle.connect") as mock_connect:
            bklv_tasks.send_to_bklv(
                system_url=None,
                settle_bklv_id=105,
                ext_ref="ABA-ACLEDA-USD-500-005",
                iso_message=self.BASE_ISO,
            )
        mock_err_update.assert_called_once_with(105, "BKLV_SOAP_URL is not configured")
        mock_connect.assert_not_called()

    @patch("worker.bklv_tasks.requests.post")
    @patch("worker.bklv_tasks.cx_Oracle.connect")
    def test_send_to_bklv_soap_request_includes_iso_message_and_credentials(self, mock_connect, mock_post):
        """Verify that the SOAP request body contains credentials, ext_ref, and the ISO message."""
        mock_con, mock_cur = self._make_mock_oracle()
        mock_connect.return_value = mock_con
        mock_resp = MagicMock()
        mock_resp.content = b"<return>success</return>"
        mock_post.return_value = mock_resp

        with patch.dict(os.environ, self.BKLV_ENV):
            bklv_tasks.send_to_bklv(
                system_url=None,
                settle_bklv_id=106,
                ext_ref="ABA-ACLEDA-USD-500-001",
                iso_message=self.BASE_ISO,
            )

        posted_body = mock_post.call_args[1]["data"].decode("utf-8")
        self.assertIn("<web:makeFullFundTransfer>", posted_body)
        self.assertIn("<web:cm_user_name>test-user</web:cm_user_name>", posted_body)
        self.assertIn("<web:cm_password>test-pass</web:cm_password>", posted_body)
        self.assertIn("ABA-ACLEDA-USD-500-001", posted_body)
        self.assertIn("InstdAmt", posted_body)  # ISO message content present

    @patch("worker.bklv_tasks.requests.post")
    @patch("worker.bklv_tasks.cx_Oracle.connect")
    def test_send_to_bklv_triggers_callback_to_source_bank(self, mock_connect, mock_post):
        """After DB update, SIS must call back the source bank (ABA) with the final status."""
        mock_con, mock_cur = self._make_mock_oracle()
        mock_connect.return_value = mock_con
        mock_resp = MagicMock()
        mock_resp.content = b"<return>success</return>"
        mock_post.return_value = mock_resp

        with patch.dict(os.environ, self.BKLV_ENV), \
             patch("worker.bklv_tasks.update_system_status", return_value=True) as mock_cb:
            bklv_tasks.send_to_bklv(
                system_url="http://aba.example.local/callback",
                settle_bklv_id=107,
                ext_ref="ABA-ACLEDA-USD-500-001",
                iso_message=self.BASE_ISO,
            )

        mock_cb.assert_called_once_with(
            system_url="http://aba.example.local/callback",
            settle_cbs_id=107,
            status=bklv_tasks.SETTLE_STATUS_SUCCESS,
        )
