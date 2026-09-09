import unittest

import requests


class ApiFlexcube(unittest.TestCase):
    API_URL = "http://localhost:8000/api/v1/sis/"
    TOKEN_KEY = None

    def setUp(self):
        from test_user import ApiUser

        ApiUser.test_correct_user_login(self)
        self.TOKEN_KEY = ApiUser.ACCESS_TOKEN

    def test_wrong_create_flexcube(self):
        r = requests.post(ApiFlexcube.API_URL + 'create-flexcube',
                          json={
                              "username": "fcbs",
                              "password": "fcbs@1234",
                              "environment_id": 1,
                              "flexcube_url": "https://",
                              "source": None,
                              "ubscomp": None,
                              "userid": 1,
                              "branch": 1,
                              "moduleid": 1,
                              "service": None,
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 401)

    def test_correct_create_flexcube(self):
        r = requests.post(ApiFlexcube.API_URL + 'create-flexcube',
                          headers={
                              "Authorization": "Bearer " + self.TOKEN_KEY
                          },
                          json={
                              "username": "fcbs",
                              "password": "fcbs@1234",
                              "environment_id": 1,
                              "flexcube_url": "https://",
                              "source": None,
                              "ubscomp": None,
                              "userid": 1,
                              "branch": 1,
                              "moduleid": 1,
                              "service": None,
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 200)

    def test_wrong_edit_flexcube(self):
        r = requests.post(ApiFlexcube.API_URL + 'edit-flexcube',
                          json={
                              "username": "fcbs",
                              "password": "fcbs@1234",
                              "environment_id": 1,
                              "flexcube_url": "https://",
                              "source": None,
                              "ubscomp": None,
                              "userid": 1,
                              "branch": 1,
                              "moduleid": 1,
                              "service": None,
                              "updated_by": 1
                          })
        self.assertEqual(r.status_code, 401)

    def test_correct_edit_flexcube(self):
        r = requests.post(ApiFlexcube.API_URL + 'edit-flexcube?id=1',
                          headers={
                              "Authorization": "Bearer " + self.TOKEN_KEY
                          },
                          json={
                              "username": "fcbs",
                              "password": "fcbs@1234",
                              "environment_id": 1,
                              "flexcube_url": "https://",
                              "source": None,
                              "ubscomp": None,
                              "userid": 1,
                              "branch": 1,
                              "moduleid": 1,
                              "service": None,
                              "updated_by": 1
                          })
        self.assertEqual(r.status_code, 200)

    def test_correct_list_flexcube(self):
        r = requests.get(ApiFlexcube.API_URL + 'list-flexcube',
                         headers={
                             "Authorization": "Bearer " + self.TOKEN_KEY
                         })
        self.assertEqual(r.status_code, 200)

    def test_correct_flexcube_detail_by_id(self):
        r = requests.get(ApiFlexcube.API_URL + 'flexcube-detail-by-id?id=1',
                         headers={
                             "Authorization": "Bearer " + self.TOKEN_KEY
                         })
        self.assertEqual(r.status_code, 200)
