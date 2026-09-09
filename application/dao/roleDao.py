"""
Role data access object from SIS Oracle database. Contains SQL queries related to Role.
"""
from datetime import datetime
from typing import List

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.role import Role
from application.utils.query_sanitizer import safe_order_by

_ROLE_ALLOWED_COLUMNS = {
    "ROLE_ID": Role.role_id,
    "NAME": Role.name,
    "STATUS": Role.status,
    "DESCRIPTION": Role.description,
    "CREATED_AT": Role.created_at,
    "UPDATED_AT": Role.updated_at,
}


class RoleDao:
    @staticmethod
    def get_roles(page: int, size: int, order_by: Role, order_method: str) -> List[Role]:
        """
        Get a list of the role from the database by query parameters.
        :return: A list containing Role model objects.
        """
        roles = Role.query
        roles = safe_order_by(roles, _ROLE_ALLOWED_COLUMNS, order_by, order_method)

        if page and size:
            roles = roles.offset((page - 1) * size)

        if size:
            roles = roles.limit(size)

        return roles.all()

    @staticmethod
    def get_role_by_id(role_id: int) -> Role:
        """
            Get a single role from the database based on role id.
            :param role_id: Role ID which uniquely identifies the Role.
            :return: The result of the database query
            """
        return Role.query.get(role_id)

    @staticmethod
    def add_role(role: Role) -> bool:
        """
            Add a Role to database
            :param role: Role object representing a Role for the application.
            :return: True if the role is inserted into the database, False otherwise.
        """
        db.session.add(role)
        return BasicDao.safe_commit()

    @staticmethod
    def update_role(role_id: int, role: Role) -> bool:
        """
            Update Role in the database.
            :param role_id: Role ID which uniquely identifies the Role.
            :param role: Role object representing a Role for the application.
            :return: True if the role is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE role SET
                name=:name,
                description=:description,
                updated_by=:updated_by,
                updated_at=:current_date,
                status=:status
            WHERE role_id=:role_id
            """),
            {
                "name": role.name,
                "description": role.description,
                "updated_by": role.updated_by,
                "current_date": datetime.now(),
                "status": role.status,
                "role_id": role_id
            },
        )
        return BasicDao.safe_commit()
