import unittest

import requests


class ApiSystem(unittest.TestCase):
    API_URL = "http://localhost:8000/api/v1/sis/"
    TOKEN_KEY = None

    def setUp(self):
        from test_user import ApiUser

        ApiUser.test_correct_user_login(self)
        self.TOKEN_KEY = ApiUser.ACCESS_TOKEN

    def test_wrong_create_system(self):
        r = requests.post(ApiSystem.API_URL + 'create-system',
                          json={
                              "system_name": "FAST",
                              "url": "nbc.org.kh",
                              "ip_address": "12.123.11.123",
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 401)

    def test_correct_create_system(self):
        r = requests.post(ApiSystem.API_URL + 'create-system',
                          headers={
                              "Authorization": "Bearer " + self.TOKEN_KEY
                          },
                          json={
                              "system_name": "FAST",
                              "url": "nbc.org.kh",
                              "ip_address": "12.123.11.123",
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 200)

    def test_wrong_create_system_user(self):
        r = requests.post(ApiSystem.API_URL + 'create-system-user',
                          json={
                              "system_id": 1,
                              "username": "fast",
                              "password": "1234567",
                              "status": 1,
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 401)

    @unittest.skip
    def test_correct_create_system_user(self):
        r = requests.post(ApiSystem.API_URL + 'create-system-user',
                          headers={
                              "Authorization": "Bearer " + self.TOKEN_KEY
                          },
                          json={
                              "system_id": 1,
                              "username": "fast",
                              "password": "1234567",
                              "status": 1,
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 200)

    def test_wrong_edit_system_user(self):
        r = requests.post(ApiSystem.API_URL + 'edit-system-user',
                          json={
                              "system_id": 1,
                              "username": "fasts",
                              "password": "1234@fast",
                              "status": 1,
                              "updated_by": 1
                          })
        self.assertEqual(r.status_code, 401)

    def test_correct_edit_system_user(self):
        r = requests.post(ApiSystem.API_URL + 'edit-system-user?id=1',
                          headers={
                              "Authorization": "Bearer " + self.TOKEN_KEY
                          },
                          json={
                              "system_id": 1,
                              "username": "security@nbc.com",
                              "password": "admin",
                              "status": 1,
                              "updated_by": 1
                          })
        self.assertEqual(r.status_code, 200)

    def test_wrong_edit_system(self):
        r = requests.post(ApiSystem.API_URL + 'edit-system',
                          json={
                              "system_name": "FAST 2.0",
                              "url": "nbc.org.kh",
                              "ip_address": "12.123.11.123",
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 401)

    def test_correct_edit_system(self):
        r = requests.post(ApiSystem.API_URL + 'edit-system?id=1',
                          headers={
                              "Authorization": "Bearer " + self.TOKEN_KEY
                          },
                          json={
                              "system_name": "FAST 2.0",
                              "url": "nbc.org.kh",
                              "ip_address": "12.123.11.123",
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 200)

    def test_correct_list_system(self):
        r = requests.get(ApiSystem.API_URL + 'list-system',
                         headers={
                             "Authorization": "Bearer " + self.TOKEN_KEY
                         })
        self.assertEqual(r.status_code, 200)

    def test_correct_system_detail_by_id(self):
        r = requests.get(ApiSystem.API_URL + 'system-detail-by-id?id=1',
                         headers={
                             "Authorization": "Bearer " + self.TOKEN_KEY
                         })
        self.assertEqual(r.status_code, 200)
