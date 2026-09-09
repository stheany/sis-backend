"""
Action data access object from SIS Oracle database. Contains SQL queries related to action.
"""
from datetime import datetime
from typing import List

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.userRole import UserRole


class UserRoleDao:
    @staticmethod
    def get_user_role() -> List[UserRole]:
        """
        Get a list of the user role from the database.
        :return: A list containing UserRole model objects.
        """

        return UserRole.query.all()

    @staticmethod
    def get_user_role_by_id(user_role_id: int) -> UserRole:
        """
        Get a single UserRole from the database based on UserRole id.
        :param user_role_id: UserRole ID which uniquely identifies the UserRole.
        :return: The result of the database query.
        """
        return UserRole.query.get(user_role_id)

    @staticmethod
    def get_user_role_by_users_login_sis_id(users_login_sis_id: int) -> UserRole:
        """
        Get a single UserRole from the database based on UserRole users_login_sis_id.
        :param users_login_sis_id: UserRole users_login_sis_id which uniquely identifies the UserRole.
        :return: The result of the database query.
        """
        return UserRole.query.filter_by(users_login_sis_id=users_login_sis_id).first()

    @staticmethod
    def get_user_role_by_user_and_role(users_login_sis_id: int, role_id: int) -> UserRole:
        """
        Check whether a user already has the given role assigned.
        :param users_login_sis_id: The user's ID.
        :param role_id: The role's ID.
        :return: The existing UserRole row, or None if no mapping exists.
        """
        return UserRole.query.filter_by(
            users_login_sis_id=users_login_sis_id,
            role_id=role_id
        ).first()

    @staticmethod
    def add_user_role(user_role: UserRole) -> bool:
        """
        Add an UserRole to database
        :param user_role: UserRole object representing UserRole for the application.
        :return: True if the UserRole is inserted into the database, False otherwise.
        """
        db.session.add(user_role)
        return BasicDao.safe_commit()

    @staticmethod
    def update_user_role(user_role_id: int, user_role: UserRole) -> bool:
        """
        Update an UserRole in the database.
        :param user_role_id: UserRole ID which uniquely identifies the UserRole.
        :param user_role: UserRole object representing an UserRole for the application.
        :return: True if the UserRole is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE user_role SET
                role_id=:role_id,
                users_login_sis_id=:users_login_sis_id,
                updated_at=:current_date,
                updated_by=:updated_by
            WHERE user_role_id=:user_role_id
            """),
            {
                "role_id": user_role.role_id,
                "users_login_sis_id": user_role.users_login_sis_id,
                "current_date": datetime.now(),
                "updated_by": user_role.updated_by,
                "user_role_id": user_role.user_role_id,
            },
        )
        return BasicDao.safe_commit()
