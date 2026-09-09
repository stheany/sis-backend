import unittest

import requests


class ApiAction(unittest.TestCase):
    API_URL = "http://localhost:8000/api/v1/sis/"
    TOKEN_KEY = None

    def setUp(self):
        from test_user import ApiUser

        ApiUser.test_correct_user_login(self)
        self.TOKEN_KEY = ApiUser.ACCESS_TOKEN

    def test_wrong_create_action(self):
        r = requests.post(ApiAction.API_URL + 'create-action',
                          json={
                              "name": "View",
                              "description": "This action allow only view.",
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 401)

    def test_correct_create_action(self):
        r = requests.post(ApiAction.API_URL + 'create-action',
                          headers={
                              "Authorization": "Bearer " + self.TOKEN_KEY
                          },
                          json={
                              "name": "View",
                              "description": "This action allow only view.",
                              "created_by": 1
                          })
        self.assertEqual(r.status_code, 200)

    def test_wrong_edit_action(self):
        r = requests.post(ApiAction.API_URL + 'edit-action',
                          json={
                              "name": "Edit",
                              "description": "This action allow to edit some information",
                              "updated_by": 1
                          })
        self.assertEqual(r.status_code, 401)

    def test_correct_edit_action(self):
        r = requests.post(ApiAction.API_URL + 'edit-action?id=1',
                          headers={
                              "Authorization": "Bearer " + self.TOKEN_KEY
                          },
                          json={
                              "name": "Edit",
                              "description": "This action allow to edit some information",
                              "updated_by": 1
                          })
        self.assertEqual(r.status_code, 200)

    def test_correct_list_action(self):
        r = requests.get(ApiAction.API_URL + 'list-action',
                         headers={
                             "Authorization": "Bearer " + self.TOKEN_KEY
                         })
        self.assertEqual(r.status_code, 200)

    def test_correct_action_detail_by_id(self):
        r = requests.get(ApiAction.API_URL + 'action-detail-by-id?id=1',
                         headers={
                             "Authorization": "Bearer " + self.TOKEN_KEY
                         })
        self.assertEqual(r.status_code, 200)
