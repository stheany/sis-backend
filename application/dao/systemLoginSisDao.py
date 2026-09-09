"""
SystemLoginSis data access object from SIS Oracle database. Contains SQL queries related to SystemLoginSis.
"""
from datetime import datetime
from typing import List

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.systemLoginSis import SystemLoginSis
from application.utils.query_sanitizer import safe_order_by

_SYSTEM_LOGIN_SIS_ALLOWED_COLUMNS = {
    "SYSTEM_LOGIN_SIS_ID": SystemLoginSis.system_login_sis_id,
    "SYSTEM_ID": SystemLoginSis.system_id,
    "USERNAME": SystemLoginSis.username,
    "STATUS": SystemLoginSis.status,
    "CREATED_AT": SystemLoginSis.created_at,
    "UPDATED_AT": SystemLoginSis.updated_at,
}


class SystemLoginSisDao:
    @staticmethod
    def get_system_login_sis(page: int, size: int, orderBy: SystemLoginSis, orderMethod: str) -> List[SystemLoginSis]:
        """
        Get a list of the SystemLoginSis from the database by query parameters.
        :return: A list containing SystemLoginSis model objects.
        """
        system_login_sis = SystemLoginSis.query
        system_login_sis = safe_order_by(system_login_sis, _SYSTEM_LOGIN_SIS_ALLOWED_COLUMNS, orderBy, orderMethod)

        if page and size:
            system_login_sis = system_login_sis.offset((page - 1) * size).limit(size)
        elif size:
            system_login_sis = system_login_sis.limit(size)

        return system_login_sis.all()

    @staticmethod
    def get_system_login_sis_by_id(system_login_sis_id: int) -> SystemLoginSis:
        """
        Get a single SystemLoginSis from the database based on SystemLoginSis id.
        :param system_login_sis_id: SystemLoginSis ID which uniquely identifies the SystemLoginSis.
        :return: The result of the database query
        """
        return SystemLoginSis.query.get(system_login_sis_id)

    @staticmethod
    def get_system_login_sis_by_username(username: str) -> SystemLoginSis:
        """
        Get a single SystemLoginSis from the database based on SystemLoginSis username.
        :param username: SystemLoginSis username which uniquely identifies the SystemLoginSis.
        :return: The result of the database query
        """
        return SystemLoginSis.query.filter_by(username=username).first()

    @staticmethod
    def add_system_login_sis(system_login_sis: SystemLoginSis) -> bool:
        """
        Add a SystemLoginSis to database
        :param system_login_sis: SystemLoginSis object representing a SystemLoginSis for the application.
        :return: True if the SystemLoginSis is inserted into the database, False otherwise.
        """
        db.session.add(system_login_sis)
        return BasicDao.safe_commit()

    @staticmethod
    def update_system_login_sis(system_login_sis_id: int, system_login_sis: SystemLoginSis) -> bool:
        """
        Update SystemLoginSis in the database.
        :param system_login_sis_id: SystemLoginSis ID which uniquely identifies the SystemLoginSis.
        :param system_login_sis: SystemLoginSis object representing SystemLoginSis for the application.
        :return: True if the SystemLoginSis is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE system_login_sis SET
                username=:username,
                password=:password,
                status=:status,
                system_id=:system_id,
                updated_by=:updated_by,
                updated_at=:updated_at
            WHERE system_login_sis_id=:system_login_sis_id
            """),
            {
                "username": system_login_sis.username,
                "password": system_login_sis.password,
                "status": system_login_sis.status,
                "system_id": system_login_sis.system_id,
                "updated_by": system_login_sis.updated_by,
                "updated_at": datetime.now(),
                "system_login_sis_id": system_login_sis_id
            },
        )
        return BasicDao.safe_commit()
