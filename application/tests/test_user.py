import unittest

import requests


class ApiUser(unittest.TestCase):
    API_URL = "http://localhost:8000/api/v1/"
    ACCESS_TOKEN = None

    def setUp(self):
        from test_user import ApiUser

        ApiUser.test_correct_user_login(self)
        self.TOKEN_KEY = ApiUser.ACCESS_TOKEN

    def test_wrong_user_login(self):
        r = requests.post(ApiUser.API_URL + 'user-login',
                          json={
                              "username": "admin",
                              "password": "adminx"
                          })
        self.assertEqual(r.status_code, 401)

    def test_correct_user_login(self):
        r = requests.post(ApiUser.API_URL + 'user-login',
                          json={
                              "username": "admin",
                              "password": "admin"
                          })
        print(r)
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone((r.json())['data']['access_token'])
        ApiUser.ACCESS_TOKEN = r.json()['data']['access_token']

    def test_wrong_create_user(self):
        r = requests.post(ApiUser.API_URL + 'sis/create-user',
                          json={
                              "username": "Darxa",
                              "password": "ss",
                              "email": "darax@nbc.org.kh",
                              "first_name": "Dara",
                              "last_name": "Tyty",
                              "user_id": "1022",
                              "status": "1"
                          })
        self.assertEqual(r.status_code, 401)

    @unittest.skip
    def test_correct_create_user(self):
        r = requests.post(ApiUser.API_URL + 'sis/create-user',
                          headers={
                              "Authorization": "Bearer " + self.TOKEN_KEY,
                              "user_id": "1"
                          },
                          json={
                              "username": "Darxe2eeeeeea",
                              "password": "ss",
                              "email": "darax@nbc.org.kh",
                              "first_name": "Dara",
                              "last_name": "Tyty",
                              "nbc_user_id": "1022",
                              "status": "1"
                          })
        self.assertEqual(r.status_code, 200)

    def test_wrong_user_logout(self):
        r = requests.post(ApiUser.API_URL + 'user-logout', headers={
            "Authorization": None
        })
        self.assertEqual(r.status_code, 401)

    def test_correct_user_logout(self):
        ApiUser.test_correct_user_login(self)

        r = requests.post(ApiUser.API_URL + 'user-logout', headers={
            "Authorization": "Bearer " + ApiUser.ACCESS_TOKEN
        })
        self.assertEqual(r.status_code, 200)
