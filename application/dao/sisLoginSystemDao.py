"""
SisLoginSystem data access object from SIS Oracle database. Contains SQL queries related to SisLoginSystem.
"""
from datetime import datetime
from typing import List

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.sisLoginSystem import SisLoginSystem


class SisLoginSystemDao:
    @staticmethod
    def get_sis_login_system() -> List[SisLoginSystem]:
        """
        Get a list of the SisLoginSystem from the database by query parameters.
        :return: A list containing SisLoginSystem model objects.
        """

        return SisLoginSystem.query.all()

    @staticmethod
    def get_sis_login_system_by_id(sis_login_system_id: int) -> SisLoginSystem:
        """
        Get a single SisLoginSystem from the database based on SisLoginSystem id.
        :param sis_login_system_id: SisLoginSystem ID which uniquely identifies the SisLoginSystem.
        :return: The result of the database query
        """
        return SisLoginSystem.query.get(sis_login_system_id)

    @staticmethod
    def add_sis_login_system(sis_login_system: SisLoginSystem) -> bool:
        """
        Add an SisLoginSystem to database
        :param sis_login_system: SisLoginSystem object representing a SisLoginSystem for the application.
        :return: True if the SisLoginSystem is inserted into the database, False otherwise.
        """
        db.session.add(sis_login_system)
        return BasicDao.safe_commit()

    @staticmethod
    def update_sis_login_system(sis_login_system_id: int, sis_login_system: SisLoginSystem) -> bool:
        """
        Update an SisLoginSystem in the database.
        :param sis_login_system_id: SisLoginSystem ID which uniquely identifies the SisLoginSystem.
        :param sis_login_system: SisLoginSystem object representing an SisLoginSystem for the application.
        :return: True if the SisLoginSystem is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE sis_login_system SET
                system_id=:system_id,
                username=:username,
                status=:status,
                updated_at=:current_date,
                updated_by=:updated_by
            WHERE sis_login_system_id=:sis_login_system_id
            """),
            {
                "system_id": sis_login_system.system_id,
                "username": sis_login_system.username,
                "status": sis_login_system.status,
                "current_date": datetime.now(),
                "updated_by": sis_login_system.updated_by,
                "sis_login_system_id": sis_login_system_id,
            },
        )
        return BasicDao.safe_commit()
