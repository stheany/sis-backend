"""
User Authentication service is used for authentication between user that login to SIS
"""
import copy
import logging
from datetime import datetime

from flask import request, Response, jsonify, session
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, get_jwt_identity

from application.dao.permissionDao import PermissionDao
from application.dao.tokenBlocklistDao import TokenBlocklistDao
from application.dao.userRoleDao import UserRoleDao
from application.dao.usersLoginSisDao import UsersLoginSisDao
from application.models.permission import Permission
from application.models.tokenBlocklist import TokenBlocklist
from application.models.userRole import UserRole
from application.models.usersLoginSis import UsersLoginSis
from application.schemas.permissionSchema import PermissionSchema
from application.schemas.usersLoginSisSchema import UsersLoginSisSchema
from application.utils.responseMessage import get_const
from application.utils.password_utils import hash_password, verify_password


def change_password() -> Response:
    """
    Used to change password of user that login to sis.
    :return: A response as json object for the POST API request.
    """
    current_user_id = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    old_password = body.get("old-password", None)
    new_password = body.get("new-password", None)

    if not old_password or not new_password:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "old-password and new-password are required."
        response["detail"]["error_code"] = 38
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    if old_password == new_password:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "New password must be different from the current password."
        response["detail"]["error_code"] = 45
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    if len(new_password) < 8:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "New password must be at least 8 characters."
        response["detail"]["error_code"] = 44
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    user_login_sis_obj: UsersLoginSis = UsersLoginSisDao.get_user_login_sis_by_id(
        users_login_sis_id=current_user_id)

    if user_login_sis_obj is None:
        response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
        response["detail"]["error_message"] = "User Login SIS Obj not found!"
        response["detail"]["error_code"] = 37
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify

    if not verify_password(old_password, user_login_sis_obj.password):
        response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]

        return response_jsonify

    # update password of user login to sis
    UsersLoginSisDao.update_user_login_sis_password(
        username=user_login_sis_obj.username,
        password=hash_password(new_password)
    )

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']

    return response_jsonify


def reset_password_user() -> Response:
    """
    Used to reset password of user that login to sis.
    Generates a new random password, saves it, and emails it to the user.
    :return: A response as json object for the POST API request.
    """
    import re
    import secrets
    import string
    from flask_mail import Message
    from application import mail

    email = request.get_json(silent=True) or {}
    email = email.get("email", None)

    if not email:
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "Email is required."
        response["detail"]["error_code"] = 42
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        response = copy.deepcopy(get_const("BAD_REQUEST_400"))
        response["detail"]["error_message"] = "Invalid email format."
        response["detail"]["error_code"] = 43
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    user_login_sis_obj: UsersLoginSis = UsersLoginSisDao.get_user_login_sis_by_email(
        email=email)

    if user_login_sis_obj is None:
        response = copy.deepcopy(get_const("NOT_FOUND_HANDLER_404"))
        response["detail"]["error_message"] = "User not found!"
        response["detail"]["error_code"] = 37
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify

    # Generate a secure random password
    alphabet = string.ascii_letters + string.digits
    new_password = ''.join(secrets.choice(alphabet) for _ in range(12))
    user_login_sis_obj.password = hash_password(new_password)
    UsersLoginSisDao.update_user_login_sis(
        user_login_sis_id=user_login_sis_obj.users_login_sis_id,
        user_login_sis=user_login_sis_obj)

    # Send email
    try:
        msg = Message(
            subject="NBC SIS — Password Reset",
            recipients=[email],
            body=(
                f"Hello {user_login_sis_obj.full_name or user_login_sis_obj.username},\n\n"
                f"Your password has been reset.\n\n"
                f"New password: {new_password}\n\n"
                f"Please login and change your password immediately.\n\n"
                f"NBC :: System Integration Service\n"
                f"https://www.nbc.gov.kh/"
            )
        )
        mail.send(msg)
        email_sent = True
    except Exception:
        logging.getLogger(__name__).exception("Failed to send reset password email")
        email_sent = False

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response['detail']['data'] = {
        'email_sent': email_sent,
        # Only return new_password in response if email failed (fallback)
        'new_password': new_password if not email_sent else None
    }
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']
    return response_jsonify


def login() -> Response:
    """
    Used for user login SIS
    :return: A response as json object for the POST API request.
    """
    body = request.get_json(silent=True) or {}
    username = body.get("username", None)
    password = body.get("password", None)

    if not username or not password:
        response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response['http_code']

        return response_jsonify

    user_login_sis_obj: UsersLoginSis = UsersLoginSisDao.get_user_login_sis_by_username(
        username=username)

    if user_login_sis_obj:
        if verify_password(password, user_login_sis_obj.password):
            access_token = create_access_token(
                identity=user_login_sis_obj.users_login_sis_id, fresh=True)
            refresh_token = create_refresh_token(
                user_login_sis_obj.users_login_sis_id)

            user_role_obj: UserRole = UserRoleDao. \
                get_user_role_by_users_login_sis_id(
                users_login_sis_id=user_login_sis_obj.users_login_sis_id)

            # store UserLoginSis object in "user_login_sis" key for flask session
            session["user_login_sis"] = UsersLoginSisSchema().dump(user_login_sis_obj)

            if user_role_obj:
                permissions_obj: Permission = PermissionDao.get_permissions_by_role_id(
                    role_id=user_role_obj.role_id)
                permissions_obj_serialized = PermissionSchema(many=True).dump(permissions_obj)
                actions = []
                menus = []
                for permission in permissions_obj_serialized:
                    actions.append(permission['action_id'])
                    menus.append(permission['menu_id'])
                permissions_obj = {"actions": actions, "menus": menus}
            if not user_role_obj or not permissions_obj:
                permissions_obj = {"actions": [], "menus": []}

            response = copy.deepcopy(get_const("SUCCESS_200"))
            response["detail"]["data"] = {'access_token': access_token,
                                          'refresh_token': refresh_token,
                                          'user_role_id': user_role_obj.user_role_id if user_role_obj else None,
                                          'user_id': user_login_sis_obj.users_login_sis_id,
                                          'permissions': permissions_obj,
                                          }
            response_jsonify = jsonify(response)
            response_jsonify.status_code = response["http_code"]

            return response_jsonify
        else:
            response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
            response['detail']['error_code'] = 14
            response['detail']['error_message'] = "Incorrect username or password!"
            response_jsonify = jsonify(response)
            response_jsonify.status_code = response['http_code']

            return response_jsonify
    else:
        response = copy.deepcopy(get_const("UNAUTHORIZED_401"))
        response['detail']['error_code'] = 14
        response['detail']['error_message'] = "Incorrect username or password!"
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response['http_code']

        return response_jsonify


def token_refresh() -> Response:
    """
    Used for get the refresh token for user login sis.
    :return: A response as json object for the POST API request.
    """
    current_user = get_jwt_identity()  # get current user from a refresh token
    access_token = create_access_token(identity=current_user, fresh=False)

    response = copy.deepcopy(get_const('SUCCESS_200'))
    response['detail']['data'] = {'access_token': access_token}
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response['http_code']

    return response_jsonify


def logout() -> Response:
    """
    Used for user UserLoginSis logout from SIS.
    :return: A response as json object for the POST API request.
    """
    try:
        token = get_jwt()
        token_blocklist_obj: TokenBlocklist = TokenBlocklist({
            "jti": token['jti'],
            "created_at": datetime.now(),
            "remark": "User id {user_id} logout".format(user_id=session["user_login_sis"].get('users_login_sis_id'))
        })
        TokenBlocklistDao.add_token_blocklist(token_blocklist=token_blocklist_obj)

        # when system logout from sis we remove "system_login_sis" key from flask session
        if "user_login_sis" in session.keys():
            session.pop("user_login_sis", None)

        response = copy.deepcopy(get_const('SUCCESS_200'))
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify
    except Exception as e:
        logging.getLogger(__name__).exception("Logout error")
        response = copy.deepcopy(get_const("SERVER_ERROR_500"))
        response["detail"]["error_message"] = "An internal error occurred."
        response_jsonify = jsonify(response)
        response_jsonify.status_code = response["http_code"]
        return response_jsonify
