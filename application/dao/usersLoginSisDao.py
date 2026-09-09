"""
UsersLoginSis data access object from SIS Oracle database. Contains SQL queries related to UsersLoginSis.
"""
from datetime import datetime
from typing import List

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.usersLoginSis import UsersLoginSis
from application.utils.query_sanitizer import safe_order_by

_USERS_LOGIN_SIS_ALLOWED_COLUMNS = {
    "USERS_LOGIN_SIS_ID": UsersLoginSis.users_login_sis_id,
    "USERNAME": UsersLoginSis.username,
    "FIRST_NAME": UsersLoginSis.first_name,
    "LAST_NAME": UsersLoginSis.last_name,
    "FULL_NAME": UsersLoginSis.full_name,
    "EMAIL": UsersLoginSis.email,
    "STATUS": UsersLoginSis.status,
    "CREATED_AT": UsersLoginSis.created_at,
    "UPDATED_AT": UsersLoginSis.updated_at,
}


class UsersLoginSisDao:
    @staticmethod
    def get_user_login_sis(page: int, size: int, order_by: UsersLoginSis, order_method: str) -> List[UsersLoginSis]:
        """
        Get a list of the UsersLoginSis from the database by query parameters.
        :return: A list containing UsersLoginSis model objects.
        """
        user_login_sis = UsersLoginSis.query
        user_login_sis = safe_order_by(user_login_sis, _USERS_LOGIN_SIS_ALLOWED_COLUMNS, order_by, order_method)

        if page and size:
            user_login_sis = user_login_sis.offset((page - 1) * size)

        if size:
            user_login_sis = user_login_sis.limit(size)

        return user_login_sis.all()

    @staticmethod
    def get_user_login_sis_by_id(users_login_sis_id: int) -> UsersLoginSis:
        """
        Get a single UsersLoginSis from the database based on UsersLoginSis id.
        :param user_login_sis_id: UsersLoginSis ID which uniquely identifies the UsersLoginSis.
        :return: The result of the database query
        """
        return UsersLoginSis.query.get(users_login_sis_id)

    @staticmethod
    def get_user_login_sis_by_username(username: str) -> UsersLoginSis:
        """
        Get a single UsersLoginSis from the database based on UsersLoginSis username.
        :param username: UsersLoginSis username which uniquely identifies the UsersLoginSis.
        :return: The result of the database query
        """
        return UsersLoginSis.query.filter_by(username=username).first()

    @staticmethod
    def get_user_login_sis_by_email(email: str) -> UsersLoginSis:
        """
        Get a single UsersLoginSis from the database based on UsersLoginSis email.
        :param email: UsersLoginSis email which uniquely identifies the UsersLoginSis.
        :return: The result of the database query
        """
        return UsersLoginSis.query.filter_by(email=email).first()

    @staticmethod
    def add_user_login_sis(user_login_sis: UsersLoginSis) -> bool:
        """
        Add a UsersLoginSis to database
        :param user_login_sis: UsersLoginSis object representing a UsersLoginSis for the application.
        :return: True if the UsersLoginSis is inserted into the database, False otherwise.
        """
        db.session.add(user_login_sis)
        return BasicDao.safe_commit()

    @staticmethod
    def update_user_login_sis(user_login_sis_id: int, user_login_sis: UsersLoginSis) -> bool:
        """
        Update UsersLoginSis in the database. This function does NOT update passwords.
        :param user_login_sis_id: UsersLoginSis ID which uniquely identifies the UsersLoginSis.
        :param user_login_sis: UsersLoginSis object representing UsersLoginSis for the application.
        :return: True if the UsersLoginSis is updated in the database, False otherwise.
        """
        """
        """
        db.session.execute(
            text("""
            UPDATE users_login_sis SET
                username=:username,
                first_name=:first_name,
                last_name=:last_name,
                full_name=:full_name,
                email=:email,
                description=:description,
                status=:status,
                updated_by=:updated_by,
                updated_at=:updated_at
            WHERE users_login_sis_id=:users_login_sis_id
            """),
            {
                "username": user_login_sis.username,
                "first_name": user_login_sis.first_name,
                "last_name": user_login_sis.last_name,
                "full_name": user_login_sis.full_name,
                "email": user_login_sis.email,
                "description": user_login_sis.description,
                "status": user_login_sis.status,
                "updated_by": user_login_sis.updated_by,
                "updated_at": datetime.now(),
                "users_login_sis_id": user_login_sis_id,
            },
        )
        return BasicDao.safe_commit()

    @staticmethod
    def update_user_login_sis_password(username: str, password: str) -> bool:
        """
        Update the password of an UsersLoginSis.
        :param username: Username which uniquely identifies the UsersLoginSis.
        :param password: New password for a UsersLoginSis.
        :return: True if the update was successful, False otherwise
        """
        db.session.execute(
            text("""
            UPDATE users_login_sis SET 
            password=:password 
            WHERE username=:username
            """),
            {
                "username": username,
                "password": password
            },
        )
        return BasicDao.safe_commit()
