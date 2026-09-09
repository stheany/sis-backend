"""
Unit tests for the bic_code field added to SYSTEM.
Mocked, no live server/DB required — same style as test_bklv.py, chosen
because test_system.py's existing tests hit a real running server instead.
"""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from flask import Flask

from application.dao.systemDao import SystemDao
from application.models.system import System
from application.services import systemService as service


class SystemBicCodeModelTests(unittest.TestCase):
    def test_model_init_reads_bic_code(self):
        system_obj = System({"system_name": "ACLEDA", "bic_code": "ACLEDAPPXXX"})
        self.assertEqual(system_obj.bic_code, "ACLEDAPPXXX")

    def test_model_init_defaults_bic_code_to_none(self):
        system_obj = System({"system_name": "ACLEDA"})
        self.assertIsNone(system_obj.bic_code)


class SystemBicCodeServiceTests(unittest.TestCase):
    """
    Duplicate checks are on url / ip_address / bic_code — the real
    physical/network identifiers of a system — not system_name, which is
    just a display label and isn't checked at all.
    """

    def setUp(self):
        self.app = Flask(__name__)
        # Default: nothing collides, for tests that don't care about the check.
        self._no_collision = [
            patch.object(service.SystemDao, "get_system_by_url", return_value=None),
            patch.object(service.SystemDao, "get_system_by_ip_address", return_value=None),
            patch.object(service.SystemDao, "get_system_by_bic_code", return_value=None),
        ]
        for p in self._no_collision:
            p.start()
            self.addCleanup(p.stop)

    def test_create_system_passes_bic_code_through(self):
        payload = {
            "system_name": "ACLEDA",
            "short_name": "ACLEDA",
            "bic_code": "ACLEDAPPXXX",
            "url": "https://acleda.example.com/callback",
            "ip_address": "10.20.30.40",
            "created_by": 1,
        }
        with self.app.test_request_context(json=payload):
            with patch.object(service.SystemDao, "add_system", return_value=True) as mock_add:
                response = service.system_post()

        self.assertEqual(response.status_code, 200)
        created_system = mock_add.call_args[0][0]
        self.assertEqual(created_system.bic_code, "ACLEDAPPXXX")

    def test_create_system_without_bic_code_defaults_to_none(self):
        """bic_code is optional — omitting it must not break system creation."""
        payload = {"system_name": "NCS", "created_by": 1}
        with self.app.test_request_context(json=payload):
            with patch.object(service.SystemDao, "add_system", return_value=True) as mock_add:
                response = service.system_post()

        self.assertEqual(response.status_code, 200)
        created_system = mock_add.call_args[0][0]
        self.assertIsNone(created_system.bic_code)

    def test_create_system_does_not_check_name_for_duplicates(self):
        """system_name is a display label — two systems may legitimately share one."""
        payload = {"system_name": "ABA Bank", "created_by": 1}
        with self.app.test_request_context(json=payload):
            with patch.object(service.SystemDao, "add_system", return_value=True), \
                 patch.object(service.SystemDao, "get_system_by_name") as mock_by_name:
                response = service.system_post()

        self.assertEqual(response.status_code, 200)
        mock_by_name.assert_not_called()

    def test_create_system_rejects_duplicate_url(self):
        payload = {"system_name": "ABA Bank 2", "url": "http://host.docker.internal:9001/callback", "created_by": 1}
        existing = System({"system_name": "ABA Bank"})
        existing.system_id = 91
        with self.app.test_request_context(json=payload):
            with patch.object(service.SystemDao, "get_system_by_url", return_value=existing), \
                 patch.object(service.SystemDao, "add_system") as mock_add:
                response = service.system_post()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["detail"]["error_code"], 42)
        self.assertIn("url", response.get_json()["detail"]["error_message"])
        mock_add.assert_not_called()

    def test_create_system_rejects_duplicate_ip_address(self):
        payload = {"system_name": "ABA Bank 2", "ip_address": "10.20.30.40", "created_by": 1}
        existing = System({"system_name": "ABA Bank"})
        existing.system_id = 91
        with self.app.test_request_context(json=payload):
            with patch.object(service.SystemDao, "get_system_by_ip_address", return_value=existing), \
                 patch.object(service.SystemDao, "add_system") as mock_add:
                response = service.system_post()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["detail"]["error_code"], 43)
        mock_add.assert_not_called()

    def test_create_system_rejects_duplicate_bic_code(self):
        payload = {"system_name": "ABA Bank 2", "bic_code": "ABAAKHPPXXX", "created_by": 1}
        existing = System({"system_name": "ABA Bank"})
        existing.system_id = 91
        with self.app.test_request_context(json=payload):
            with patch.object(service.SystemDao, "get_system_by_bic_code", return_value=existing), \
                 patch.object(service.SystemDao, "add_system") as mock_add:
                response = service.system_post()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["detail"]["error_code"], 44)
        mock_add.assert_not_called()

    def test_create_system_skips_checks_for_fields_left_blank(self):
        """Two systems both omitting url/ip/bic_code isn't a collision — matches SQL UNIQUE + NULL semantics."""
        payload = {"system_name": "Minimal System", "created_by": 1}
        with self.app.test_request_context(json=payload):
            with patch.object(service.SystemDao, "get_system_by_url") as mock_url, \
                 patch.object(service.SystemDao, "get_system_by_ip_address") as mock_ip, \
                 patch.object(service.SystemDao, "get_system_by_bic_code") as mock_bic, \
                 patch.object(service.SystemDao, "add_system", return_value=True):
                response = service.system_post()

        self.assertEqual(response.status_code, 200)
        mock_url.assert_not_called()
        mock_ip.assert_not_called()
        mock_bic.assert_not_called()

    def test_edit_system_updates_bic_code(self):
        existing = System({"system_name": "ACLEDA", "bic_code": None})
        existing.system_id = 41
        payload = {
            "system_name": "ACLEDA",
            "short_name": "ACLEDA",
            "bic_code": "ACLEDAPPXXX",
            "url": "https://acleda.example.com/callback",
            "ip_address": "10.20.30.40",
            "updated_by": 1,
            "status": "1",
        }
        with self.app.test_request_context(json=payload, query_string={"system_id": "41"}):
            with patch.object(service.SystemDao, "get_system_by_id", return_value=existing), \
                 patch.object(service.SystemDao, "update_system", return_value=True) as mock_update:
                response = service.system_put()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(existing.bic_code, "ACLEDAPPXXX")
        updated_system_arg = mock_update.call_args.kwargs.get("system") or mock_update.call_args[0][1]
        self.assertEqual(updated_system_arg.bic_code, "ACLEDAPPXXX")

    def test_edit_system_allows_keeping_its_own_bic_code(self):
        """Editing a system without changing bic_code must not trip the duplicate check on itself."""
        existing = System({"system_name": "ACLEDA", "bic_code": "ACLEDAPPXXX"})
        existing.system_id = 41
        payload = {"system_name": "ACLEDA", "bic_code": "ACLEDAPPXXX", "updated_by": 1, "status": "1"}
        with self.app.test_request_context(json=payload, query_string={"system_id": "41"}):
            with patch.object(service.SystemDao, "get_system_by_id", return_value=existing), \
                 patch.object(service.SystemDao, "get_system_by_bic_code", return_value=existing), \
                 patch.object(service.SystemDao, "update_system", return_value=True):
                response = service.system_put()

        self.assertEqual(response.status_code, 200)

    def test_edit_system_rejects_bic_code_belonging_to_another_system(self):
        existing = System({"system_name": "ACLEDA", "bic_code": None})
        existing.system_id = 41
        other_system = System({"system_name": "ABA Bank", "bic_code": "ABAAKHPPXXX"})
        other_system.system_id = 91
        payload = {"system_name": "ACLEDA", "bic_code": "ABAAKHPPXXX", "updated_by": 1, "status": "1"}
        with self.app.test_request_context(json=payload, query_string={"system_id": "41"}):
            with patch.object(service.SystemDao, "get_system_by_id", return_value=existing), \
                 patch.object(service.SystemDao, "get_system_by_bic_code", return_value=other_system), \
                 patch.object(service.SystemDao, "update_system") as mock_update:
                response = service.system_put()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["detail"]["error_code"], 44)
        mock_update.assert_not_called()

    def test_edit_system_allows_renaming_freely(self):
        """system_name has no uniqueness check — renaming to any label, even another system's, is allowed."""
        existing = System({"system_name": "ACLEDA"})
        existing.system_id = 41
        payload = {"system_name": "ABA Bank", "updated_by": 1, "status": "1"}
        with self.app.test_request_context(json=payload, query_string={"system_id": "41"}):
            with patch.object(service.SystemDao, "get_system_by_id", return_value=existing), \
                 patch.object(service.SystemDao, "update_system", return_value=True):
                response = service.system_put()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(existing.system_name, "ABA Bank")


class SystemBicCodeDaoTests(unittest.TestCase):
    """Regression test: update_system's raw SQL must persist bic_code, not just the ORM attribute."""

    def test_update_system_sql_includes_bic_code(self):
        system_obj = System({"system_name": "ACLEDA", "bic_code": "ACLEDAPPXXX"})
        system_obj.system_id = 41

        mock_session = MagicMock()
        with patch.object(SystemDao, "__module__", SystemDao.__module__), \
             patch("application.dao.systemDao.db.session", mock_session), \
             patch("application.dao.systemDao.BasicDao.safe_commit", return_value=True):
            SystemDao.update_system(system_id=41, system=system_obj)

        executed_sql = str(mock_session.execute.call_args[0][0])
        executed_params = mock_session.execute.call_args[0][1]
        self.assertIn("bic_code", executed_sql)
        self.assertEqual(executed_params["bic_code"], "ACLEDAPPXXX")


if __name__ == "__main__":
    unittest.main()
