"""
User routes SIS API. Used for represent the API related to user request to SIS
"""

from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required

from application.services.userRoleService import user_role_post, user_role_put
from application.services.usersAuthService import change_password, reset_password_user, login, logout, token_refresh
from application.services.usersLoginSisService import user_login_sis_post, users_login_sis_get, \
    users_login_sis_by_id_get
from application.utils.rbac import rbac

user_route = Blueprint("user", __name__, url_prefix="/api/v1/sis")


@user_route.route('/create-user', methods=["POST"])
@jwt_required()
@rbac.check_allowed_access
def create_user() -> Response:
    """
    Endpoints for creating new user that login sis.
    :return: JSON representation of system and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-user"""
        return user_login_sis_post()


@user_route.route('/create-user-role', methods=['POST'])
@jwt_required()
@rbac.check_allowed_access
def create_user_role() -> Response:
    """
    Endpoints for creating new user role.
    :return: JSON representation of system and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-user-role"""
        return user_role_post()


@user_route.route('/edit-user-role', methods=["PUT"])
@jwt_required()
@rbac.check_allowed_access
def edit_user_role() -> Response:
    """
    Endpoints for updating the existing user role.
    :return: JSON representation of system and relevant metadata.
    """
    if request.method == "PUT":
        """[PUT] /api/v1/sis/edit-user-role"""
        return user_role_put()


@user_route.route('/list-user', methods=["GET"])
@jwt_required()
@rbac.check_allowed_access
def list_user() -> Response:
    """
    Endpoints for listing all user login to sis.
    :return: JSON representation of system and relevant metadata.
    """
    if request.method == "GET":
        """[PUT] /api/v1/sis/list-user"""
        return users_login_sis_get()


@user_route.route('/user-detail-by-id', methods=["GET"])
@jwt_required()
@rbac.check_allowed_access
def user_detail_by_id() -> Response:
    """
    Endpoints for retrieving the existing user by user id.
    :return: JSON representation of user login to sis and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/user-detail-by-id"""
        return users_login_sis_by_id_get()


@user_route.route('/change-password', methods=["PATCH"])
@jwt_required()
def change_password_user() -> Response:
    """
    Endpoints for updating user that login to sis's password.
    :return: JSON representation of user login to sis and relevant metadata.
    """
    if request.method == "PATCH":
        """[PATCH] /api/v1/sis/change-password"""
        return change_password()


@user_route.route('/reset-password-by-email', methods=["POST"])
def reset_password() -> Response:
    """
    Endpoints for reseting the user password based on email
    :return: JSON representation of user login to sis and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/reset-password-by-email"""
        return reset_password_user()


@user_route.route('/login', methods=["POST"])
def user_login() -> Response:
    """
    Endpoints for user login to sis.
    :return: JSON representation of user login to sis and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/login"""
        return login()


@user_route.route('/user-logout', methods=["POST"])
@jwt_required()
def user_logout() -> Response:
    """
    Endpoints for user logout from sis.
    :return: JSON representation of user login to sis and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/user-logout"""
        return logout()


@user_route.route('/user-refresh-token', methods=["POST"])
@jwt_required(refresh=True)
def user_refresh_token() -> Response:
    """
    Endpoints for user to refresh the token
    :return: JSON representation of user login to sis and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/user-refresh-token"""
        return token_refresh()
