"""
Permission data access object from SIS Oracle database. Contains SQL queries related to Permission.
"""
from datetime import datetime

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.permission import Permission


class PermissionDao:
    @staticmethod
    def add_permission(permission: Permission) -> bool:
        """
            Add a Permission to database
            :param permission: Permission object representing a Permission for the application.
            :return: True if the permission is inserted into the database, False otherwise.
        """
        db.session.add(permission)
        return BasicDao.safe_commit()

    @staticmethod
    def get_permission_by_id(permission_id: int) -> Permission:
        """
            Get a single permission from the database based on permission id.
            :param permission_id: Permission ID which uniquely identifies the Permission.
            :return: The result of the database query
        """
        return Permission.query.get(permission_id)

    @staticmethod
    def get_permissions_by_role_id(role_id: int) -> list:
        """
            Get a list of permission from the database based on role id.
            :param role_id: Role ID which uniquely identifies the Permission.
            :return: The result of the database query
        """
        return Permission.query.filter_by(role_id=role_id).all()

    @staticmethod
    def update_permission(permission_id: int, permission: Permission) -> bool:
        """
            Update Permission in the database.
            :param permission_id: Permission ID which uniquely identifies the Permission.
            :param permission: Permission object representing a Permission for the application.
            :return: True if the permission is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE permission SET
                role_id=:role_id,
                menu_id=:menu_id,
                action_id=:action_id,
                updated_by=:updated_by,
                updated_at=:updated_at
            WHERE permission_id=:permission_id
            """),
            {
                "role_id": permission.role_id,
                "menu_id": permission.menu_id,
                "action_id": permission.action_id,
                "updated_by": permission.updated_by,
                "updated_at": datetime.now(),
                "permission_id": permission_id
            },
        )
        return BasicDao.safe_commit()
