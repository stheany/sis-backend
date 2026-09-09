import unittest

import requests


class MenuAction(unittest.TestCase):
    API_URL = "http://localhost:8000/api/v1/sis/"
    ACCESS_TOKEN = None

    def setUp(self):
        from test_user import ApiUser

        ApiUser.test_correct_user_login(self)
        self.ACCESS_TOKEN = ApiUser.ACCESS_TOKEN

    # test create menu with no bearer token
    def test_create_menu_no_token(self):
        r = requests.post(MenuAction.API_URL + 'create-menu',
                          json={
                              "name": "New test password",
                              "description": "This feature allows users to new test password",
                              "created_by": 1
                          })
        print("<test_create_menu_no_token> Expected status response:", 401)
        print("<test_create_menu_no_token> Actual status response:", r.status_code)
        self.assertEqual(r.status_code, 401)

    # test correct create menu
    def test_correct_create_menu(self):
        r = requests.post(MenuAction.API_URL + 'create-menu',
                          headers={
                              "Authorization": "Bearer " + self.ACCESS_TOKEN
                          },
                          json={
                              "name": "New Change password",
                              "description": "This feature allows users to new change password",
                              "created_by": 1
                          })
        print("<test_correct_create_menu> Expected status response:", 200)
        print("<test_correct_create_menu> Actual status response:", r.status_code)
        self.assertEqual(r.status_code, 200)

    # test create menu with duplicate name
    def test_create_menu_duplicate_name(self):
        r = requests.post(MenuAction.API_URL + 'create-menu',
                          headers={
                              "Authorization": "Bearer " + self.ACCESS_TOKEN
                          },
                          json={
                              "name": "Change password",
                              "description": "This feature allows users to change password",
                              "created_by": 1
                          })
        print("<test_create_menu_duplicate_name> Expected status response:", 401)
        print("<test_create_menu_duplicate_name> Actual status response:", r.status_code)
        self.assertEqual(r.status_code, 401)

    # test create menu with unavailable created_by id
    def test_create_menu_wrong_created_by_id(self):
        r = requests.post(MenuAction.API_URL + 'create-menu',
                          headers={
                              "Authorization": "Bearer " + self.ACCESS_TOKEN
                          },
                          json={
                              "name": "New Test Menu",
                              "description": "This feature allows users new test menu",
                              "created_by": 2500
                          })
        print("<test_create_menu_wrong_created_by_id> Expected status response:", 401)
        print("<test_create_menu_wrong_created_by_id> Actual status response:", r.status_code)
        self.assertEqual(r.status_code, 401)

    # test edit menu with no bearer token
    def test_edit_menu_no_token(self):
        r = requests.post(MenuAction.API_URL + 'edit-menu',
                          json={
                              "menu_id": 1,
                              "name": "Edit new test password",
                              "description": "This feature allows users to new test password",
                              "updated_by": 1
                          })
        print("<test_edit_menu_no_token> Expected status response:", 401)
        print("<test_edit_menu_no_token> Actual status response:", r.status_code)
        self.assertEqual(r.status_code, 401)

    # test correct edit menu
    def test_correct_edit_menu(self):
        r = requests.post(MenuAction.API_URL + 'edit-menu',
                          headers={
                              "Authorization": "Bearer " + self.ACCESS_TOKEN
                          },
                          json={
                              "menu_id": 1,
                              "name": "Change password update 2",
                              "description": "This feature allows users to new change password",
                              "updated_by": 1
                          })
        print("<test_correct_create_menu> Expected status response:", 200)
        print("<test_correct_create_menu> Actual status response:", r.status_code)
        self.assertEqual(r.status_code, 200)

    # test edit menu unavailable menu id
    def test_edit_menu_wrong_menu_id(self):
        r = requests.post(MenuAction.API_URL + 'edit-menu',
                          headers={
                              "Authorization": "Bearer " + self.ACCESS_TOKEN
                          },
                          json={
                              "menu_id": 20,
                              "name": "New Change password 3 update",
                              "description": "This feature allows users to new change password",
                              "updated_by": 1
                          })
        print("<test_edit_menu_wrong_menu_id> Expected status response:", 404)
        print("<test_edit_menu_wrong_menu_id> Actual status response:", r.status_code)
        self.assertEqual(r.status_code, 404)

    # test edit menu no menu id
    def test_edit_menu_no_menu_id(self):
        r = requests.post(MenuAction.API_URL + 'edit-menu',
                          headers={
                              "Authorization": "Bearer " + self.ACCESS_TOKEN
                          },
                          json={
                              "name": "New Change password 3",
                              "description": "This feature allows users to new change password",
                              "updated_by": 1
                          })
        print("<test_edit_menu_no_menu_id> Expected status response:", 401)
        print("<test_edit_menu_no_menu_id> Actual status response:", r.status_code)
        self.assertEqual(r.status_code, 401)

    # test edit menu with duplicate name
    def test_edit_menu_duplicate_name(self):
        r = requests.post(MenuAction.API_URL + 'edit-menu',
                          headers={
                              "Authorization": "Bearer " + self.ACCESS_TOKEN
                          },
                          json={
                              "menu_id": 1,
                              "name": "Change password",
                              "description": "This feature allows users to change password",
                              "updated_by": 1
                          })
        print("<test_edit_menu_duplicate_name> Expected status response:", 401)
        print("<test_edit_menu_duplicate_name> Actual status response:", r.status_code)
        self.assertEqual(r.status_code, 401)

    # test edit menu with no updated_by id
    def test_edit_menu_no_updated_by_id(self):
        r = requests.post(MenuAction.API_URL + 'edit-menu',
                          headers={
                              "Authorization": "Bearer " + self.ACCESS_TOKEN
                          },
                          json={
                              "menu_id": 1,
                              "name": "New Test Menu",
                              "description": "This feature allows users new test menu",
                          })
        print("<test_edit_menu_no_updated_by_id> Expected status response:", 401)
        print("<test_edit_menu_no_updated_by_id> Actual status response:", r.status_code)
        self.assertEqual(r.status_code, 401)

    # test edit menu with unavailable updated_by id
    def test_edit_menu_wrong_updated_by_id(self):
        r = requests.post(MenuAction.API_URL + 'edit-menu',
                          headers={
                              "Authorization": "Bearer " + self.ACCESS_TOKEN
                          },
                          json={
                              "menu_id": 1,
                              "name": "New Test Menu",
                              "description": "This feature allows users new test menu",
                              "updated_by": 2500
                          })
        print("<test_edit_menu_wrong_updated_by_id> Expected status response:", 404)
        print("<test_edit_menu_wrong_updated_by_id> Actual status response:", r.status_code)
        self.assertEqual(r.status_code, 404)

    # test list menu
    # def test_list_menu_no_token(self):
    #     r = requests.get(MenuAction.API_URL + 'list-menu')
    #
    #     print("<test_list_menu_no_token> Expected status response:", 401)
    #     print("<test_list_menu_no_token> Actual status response:", r.status_code)
    #     self.assertEqual(r.status_code, 401)

    # test get menu by id
