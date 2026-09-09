import unittest

import requests


class ApiAuth(unittest.TestCase):
    API_URL = "http://localhost:8000/api/v1/"
    TOKEN_KEY = None

    def test_wrong_system_login(self):
        r = requests.post(ApiAuth.API_URL + 'sis/auth',
                          json={
                              "username": "sesscurity@nbc.com",
                              "password": "srs",
                          })
        self.assertEqual(r.status_code, 401)

    def test_correct_system_login(self):
        r = requests.post(ApiAuth.API_URL + 'sis/auth',
                          json={
                              "username": "security@nbc.com",
                              "password": "admin",
                          })
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone((r.json())['data']['token'])
        ApiAuth.TOKEN_KEY = r.json()['data']['token']

    def test_wrong_system_logout(self):
        r = requests.post(ApiAuth.API_URL + 'sis/logout', headers={
            "Authorization": None
        })
        self.assertEqual(r.status_code, 401)

    def test_correct_system_logout(self):
        ApiAuth.test_correct_system_login(self)

        r = requests.post(ApiAuth.API_URL + 'sis/logout', headers={
            "Authorization": "Bearer " + ApiAuth.TOKEN_KEY
        })
        self.assertEqual(r.status_code, 200)
