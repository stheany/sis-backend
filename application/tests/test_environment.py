import unittest

import requests


class ApiEnvironment(unittest.TestCase):
    API_URL = "http://localhost:8000/api/v1/sis/"
    TOKEN_KEY = None

    def setUp(self):
        from test_user import ApiUser

        ApiUser.test_correct_user_login(self)
        self.TOKEN_KEY = ApiUser.ACCESS_TOKEN

    def test_wrong_create_environment(self):
        r = requests.post(ApiEnvironment.API_URL + 'create-environment',
                          json={
                              "name": "SIT",
                              "description": "Thos environment is use for testing on SIT",
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 401)

    def test_correct_create_environment(self):
        r = requests.post(ApiEnvironment.API_URL + 'create-environment',
                          headers={
                              "Authorization": "Bearer " + self.TOKEN_KEY
                          },
                          json={
                              "name": "SIT",
                              "description": "Thos environment is use for testing on SIT",
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 200)

    def test_wrong_edit_environment(self):
        r = requests.post(ApiEnvironment.API_URL + 'edit-environment',
                          json={
                              "name": "SIT",
                              "description": "Thos environment is use for testing on SIT",
                              "updated_by": 1
                          })
        self.assertEqual(r.status_code, 401)

    def test_correct_edit_environment(self):
        r = requests.post(ApiEnvironment.API_URL + 'edit-environment?id=1',
                          headers={
                              "Authorization": "Bearer " + self.TOKEN_KEY
                          },
                          json={
                              "name": "SIT",
                              "description": "Thos environment is use for testing on SIT",
                              "updated_by": 1
                          })
        self.assertEqual(r.status_code, 200)

    def test_correct_list_environment(self):
        r = requests.get(ApiEnvironment.API_URL + 'list-environment',
                         headers={
                             "Authorization": "Bearer " + self.TOKEN_KEY
                         })
        self.assertEqual(r.status_code, 200)

    def test_correct_environment_detail_by_id(self):
        r = requests.get(ApiEnvironment.API_URL + 'environment-detail-by-id?id=1',
                         headers={
                             "Authorization": "Bearer " + self.TOKEN_KEY
                         })
        self.assertEqual(r.status_code, 200)
