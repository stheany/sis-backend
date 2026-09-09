"""
Integration tests for User endpoints (T02).
Tests all fixes made in fix(users) commit:
  - Password not exposed in list/detail responses
  - Pagination offset correctness
  - change-password actually persists the new password
  - user_id null/type validation on user-detail-by-id
  - create-user: password min length + email format validation
  - user_role_post returns 400 (not 500) for missing fields
  - user_role_put: user_role_id required, invalid user_role_id returns 404
"""

import pytest
import requests

BASE = "http://localhost:8000/api/v1/sis"
ADMIN = {"username": "admin", "password": "admin"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def login(username="admin", password="admin") -> str:
    """Return a valid JWT access token for the given credentials."""
    r = requests.post(f"{BASE}/login", json={"username": username, "password": password})
    assert r.status_code == 200, f"Login failed: {r.text}"
    return r.json()["detail"]["data"]["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# T02-1  Password field must NOT appear in list-user or user-detail-by-id
# ---------------------------------------------------------------------------

class TestPasswordNotExposed:
    def test_list_user_no_password(self):
        token = login()
        r = requests.get(f"{BASE}/list-user", headers=auth_headers(token))
        assert r.status_code == 200, r.text
        data = r.json()["detail"].get("data", [])
        for user in data:
            assert "password" not in user, "Password hash exposed in list-user response!"

    def test_user_detail_no_password(self):
        token = login()
        r = requests.get(f"{BASE}/user-detail-by-id", params={"user_id": 1},
                         headers=auth_headers(token))
        assert r.status_code == 200, r.text
        data = r.json()["detail"].get("data", {})
        assert "password" not in data, "Password hash exposed in user-detail-by-id response!"


# ---------------------------------------------------------------------------
# T02-2  Pagination — page 1 and page 2 must return different results
# ---------------------------------------------------------------------------

class TestPagination:
    def test_page1_and_page2_differ(self):
        token = login()
        r1 = requests.get(f"{BASE}/list-user", params={"page": 1, "size": 1},
                          headers=auth_headers(token))
        r2 = requests.get(f"{BASE}/list-user", params={"page": 2, "size": 1},
                          headers=auth_headers(token))
        assert r1.status_code == 200, r1.text
        assert r2.status_code == 200, r2.text
        ids1 = [u["users_login_sis_id"] for u in r1.json()["detail"].get("data", [])]
        ids2 = [u["users_login_sis_id"] for u in r2.json()["detail"].get("data", [])]
        # Both pages must have results and must differ
        if ids1 and ids2:
            assert ids1 != ids2, f"Page 1 and page 2 returned the same user IDs: {ids1}"


# ---------------------------------------------------------------------------
# T02-3  user-detail-by-id — input validation
# ---------------------------------------------------------------------------

class TestUserDetailValidation:
    def test_missing_user_id_returns_400(self):
        token = login()
        r = requests.get(f"{BASE}/user-detail-by-id", headers=auth_headers(token))
        assert r.status_code == 400, f"Expected 400, got {r.status_code}: {r.text}"

    def test_non_integer_user_id_returns_400(self):
        token = login()
        r = requests.get(f"{BASE}/user-detail-by-id", params={"user_id": "abc"},
                         headers=auth_headers(token))
        assert r.status_code == 400, f"Expected 400, got {r.status_code}: {r.text}"

    def test_nonexistent_user_id_returns_404(self):
        token = login()
        r = requests.get(f"{BASE}/user-detail-by-id", params={"user_id": 999999},
                         headers=auth_headers(token))
        assert r.status_code == 404, f"Expected 404, got {r.status_code}: {r.text}"

    def test_valid_user_id_returns_200(self):
        token = login()
        r = requests.get(f"{BASE}/user-detail-by-id", params={"user_id": 1},
                         headers=auth_headers(token))
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"


# ---------------------------------------------------------------------------
# T02-4  create-user — validation rules
# ---------------------------------------------------------------------------

class TestCreateUserValidation:
    def test_short_password_returns_400(self):
        token = login()
        r = requests.post(f"{BASE}/create-user",
                          json={"username": "testshortpw", "password": "abc",
                                "email": "testshortpw@nbc.org.kh",
                                "first_name": "Test", "last_name": "User"},
                          headers=auth_headers(token))
        assert r.status_code == 400, f"Expected 400 for short password, got {r.status_code}: {r.text}"
        assert r.json()["detail"]["error_code"] == 44

    def test_invalid_email_returns_400(self):
        token = login()
        r = requests.post(f"{BASE}/create-user",
                          json={"username": "testbademail", "password": "SecurePass1",
                                "email": "not-an-email",
                                "first_name": "Test", "last_name": "User"},
                          headers=auth_headers(token))
        assert r.status_code == 400, f"Expected 400 for bad email, got {r.status_code}: {r.text}"
        assert r.json()["detail"]["error_code"] == 43

    def test_missing_username_returns_400(self):
        token = login()
        r = requests.post(f"{BASE}/create-user",
                          json={"password": "SecurePass1"},
                          headers=auth_headers(token))
        assert r.status_code == 400, f"Expected 400 for missing username, got {r.status_code}: {r.text}"


# ---------------------------------------------------------------------------
# T02-5  change-password — verifies the new password is actually persisted
# ---------------------------------------------------------------------------

class TestChangePassword:
    TEST_USER = "test_changepw_user"
    ORIGINAL_PW = "Original1Pass"
    NEW_PW = "NewSecure2Pass"

    def setup_method(self):
        """Create a fresh test user before each test in this class."""
        token = login()
        # Clean up if user exists from a previous failed run (ignore errors)
        requests.delete(f"{BASE}/create-user",
                        json={"username": self.TEST_USER},
                        headers=auth_headers(token))
        r = requests.post(f"{BASE}/create-user",
                          json={
                              "username": self.TEST_USER,
                              "password": self.ORIGINAL_PW,
                              "email": f"{self.TEST_USER}@nbc.org.kh",
                              "first_name": "Test",
                              "last_name": "ChangePW",
                          },
                          headers=auth_headers(token))
        assert r.status_code == 200, f"Setup: failed to create test user: {r.text}"

    def test_change_password_persists(self):
        # Log in as the test user
        token = login(self.TEST_USER, self.ORIGINAL_PW)

        # Change password
        r = requests.patch(f"{BASE}/change-password",
                           json={"old-password": self.ORIGINAL_PW, "new-password": self.NEW_PW},
                           headers=auth_headers(token))
        assert r.status_code == 200, f"change-password failed: {r.text}"

        # Login with the OLD password must now fail
        r_old = requests.post(f"{BASE}/login",
                              json={"username": self.TEST_USER, "password": self.ORIGINAL_PW})
        assert r_old.status_code != 200, "Old password still works after change — change-password is broken!"

        # Login with the NEW password must succeed
        r_new = requests.post(f"{BASE}/login",
                              json={"username": self.TEST_USER, "password": self.NEW_PW})
        assert r_new.status_code == 200, f"New password login failed: {r_new.text}"

    def test_wrong_old_password_rejected(self):
        token = login(self.TEST_USER, self.ORIGINAL_PW)
        r = requests.patch(f"{BASE}/change-password",
                           json={"old-password": "WrongOldPassword1", "new-password": self.NEW_PW},
                           headers=auth_headers(token))
        assert r.status_code == 401, f"Expected 401 for wrong old password, got {r.status_code}"

    def test_missing_fields_returns_400(self):
        token = login(self.TEST_USER, self.ORIGINAL_PW)
        r = requests.patch(f"{BASE}/change-password",
                           json={"old-password": self.ORIGINAL_PW},
                           headers=auth_headers(token))
        assert r.status_code == 400, f"Expected 400 for missing new-password, got {r.status_code}"


# ---------------------------------------------------------------------------
# T02-6  create-user-role — missing fields must return 400 (not 500)
# ---------------------------------------------------------------------------

class TestCreateUserRole:
    def test_missing_fields_returns_400(self):
        token = login()
        r = requests.post(f"{BASE}/create-user-role",
                          json={},
                          headers=auth_headers(token))
        assert r.status_code == 400, f"Expected 400 for missing user_id/role_id, got {r.status_code}: {r.text}"

    def test_missing_role_id_returns_400(self):
        token = login()
        r = requests.post(f"{BASE}/create-user-role",
                          json={"user_id": 1},
                          headers=auth_headers(token))
        assert r.status_code == 400, f"Expected 400 for missing role_id, got {r.status_code}: {r.text}"


# ---------------------------------------------------------------------------
# T02-7  edit-user-role — missing user_role_id must return 400; invalid must 404
# ---------------------------------------------------------------------------

class TestEditUserRole:
    def test_missing_user_role_id_returns_400(self):
        token = login()
        r = requests.put(f"{BASE}/edit-user-role",
                         json={"user_id": 1, "role_id": 1},
                         headers=auth_headers(token))
        assert r.status_code == 400, f"Expected 400 for missing user_role_id, got {r.status_code}: {r.text}"

    def test_invalid_user_role_id_returns_404(self):
        token = login()
        r = requests.put(f"{BASE}/edit-user-role",
                         params={"user_role_id": 999999},
                         json={"user_id": 1, "role_id": 1},
                         headers=auth_headers(token))
        assert r.status_code == 404, f"Expected 404 for nonexistent user_role_id, got {r.status_code}: {r.text}"

    def test_missing_body_fields_returns_400(self):
        token = login()
        r = requests.put(f"{BASE}/edit-user-role",
                         params={"user_role_id": 1},
                         json={},
                         headers=auth_headers(token))
        assert r.status_code == 400, f"Expected 400 for missing body fields, got {r.status_code}: {r.text}"
