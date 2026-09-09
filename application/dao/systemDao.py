"""
System data access object from SIS Oracle database. Contains SQL queries related to system.
"""
from datetime import datetime
from typing import List

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.system import System
from application.utils.query_sanitizer import safe_order_by

_SYSTEM_ALLOWED_COLUMNS = {
    "SYSTEM_ID": System.system_id,
    "SYSTEM_NAME": System.system_name,
    "SHORT_NAME": System.short_name,
    "URL": System.url,
    "IP_ADDRESS": System.ip_address,
    "STATUS": System.status,
    "CREATED_AT": System.created_at,
    "UPDATED_AT": System.updated_at,
    "BIC_CODE": System.bic_code,
    "SETTLEMENT_ACCOUNT_NUMBER": System.settlement_account_number
}


class SystemDao:
    @staticmethod
    def get_systems(page: int, size: int, order_by: System, order_method: str) -> List[System]:
        """
        Get a list of the systems from the database by query parameters.
        :return: A list containing System model objects.
        """
        systems = System.query
        systems = safe_order_by(systems, _SYSTEM_ALLOWED_COLUMNS, order_by, order_method)

        if page and size:
            systems = systems.offset((page - 1) * size).limit(size)
        elif size:
            systems = systems.limit(size)

        return systems.all()

    @staticmethod
    def get_system_by_id(system_id: int) -> System:
        """
        Get a single system from the database based on system id.
        :param system_id: System ID which uniquely identifies the system.
        :return: The result of the database query
        """
        return System.query.filter_by(system_id=system_id).first()

    @staticmethod
    def add_system(system: System) -> bool:
        """
        Add a system to database
        :param system: System object representing a system for the application.
        :return: True if the system is inserted into the database, False otherwise.
        """
        db.session.add(system)
        return BasicDao.safe_commit()

    @staticmethod
    def update_system(system_id: int, system: System) -> bool:
        """
        Update system in the database.
        :param system_id: System ID which uniquely identifies the system.
        :param system: System object representing system for the application.
        :return: True if the system is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE system SET
                system_name=:system_name,
                short_name=:short_name,
                bic_code=:bic_code,
                settlement_account_number=:settlement_account_number,
                url=:url,
                ip_address=:ip_address,
                updated_by=:updated_by,
                updated_at=:updated_at,
                status=:status
            WHERE system_id=:system_id
            """),
            {
                "system_name": system.system_name,
                "short_name": system.short_name,
                "bic_code": system.bic_code,
                "settlement_account_number": system.settlement_account_number,
                "url": system.url,
                "ip_address": system.ip_address,
                "updated_by": system.updated_by,
                "updated_at": datetime.now(),
                "status": system.status,
                "system_id": system.system_id
            },
        )
        return BasicDao.safe_commit()

    @staticmethod
    def get_system_by_id(system_id: int) -> System:
        """
        Get a single system from the database based on system id.
        :param system_id: System ID which uniquely identifies the system.
        :return: The result of the database query
        """
        return System.query.filter_by(system_id=system_id).first()

    @staticmethod
    def get_system_by_name(system_name: str) -> System:
        """
        Get a single system from the database based on system_name.
        Case-sensitive exact match, same lookup semantics as
        bklvTransferService._get_active_system_by_name().
        :param system_name: The system_name to search for.
        :return: The result of the database query, or None.
        """
        return System.query.filter_by(system_name=system_name).first()

    @staticmethod
    def get_system_by_url(url: str) -> System:
        """
        Get a single system from the database based on url.
        :param url: The callback url to search for.
        :return: The result of the database query, or None.
        """
        return System.query.filter_by(url=url).first()

    @staticmethod
    def get_system_by_ip_address(ip_address: str) -> System:
        """
        Get a single system from the database based on ip_address.
        :param ip_address: The IP address to search for.
        :return: The result of the database query, or None.
        """
        return System.query.filter_by(ip_address=ip_address).first()

    @staticmethod
    def get_system_by_bic_code(bic_code: str) -> System:
        """
        Get a single system from the database based on bic_code.
        :param bic_code: The BIC code to search for.
        :return: The result of the database query, or None.
        """
        return System.query.filter_by(bic_code=bic_code).first()

    @staticmethod
    def get_systems_with_settlement_account() -> List[System]:
        """
        Get all systems that have a settlement_account_number registered, for
        getCBSAccountBalanceNCS's account-registry response. Caller filters for
        active status (see ncsBklvSoapService._is_active_system), same convention
        as bklvTransferService._get_active_system_by_name.
        :return: A list of System model objects.
        """
        return System.query.filter(System.settlement_account_number.isnot(None)).all()
