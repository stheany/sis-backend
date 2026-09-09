"""
Iroha data access object from SIS Oracle database. Contains SQL queries related to environment.
"""
from datetime import datetime
from typing import List

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.iroha import Iroha
from application.utils.query_sanitizer import safe_order_by

_IROHA_ALLOWED_COLUMNS = {
    "IROHA_ID": Iroha.iroha_id,
    "ENVIRONMENT_ID": Iroha.environment_id,
    "IP": Iroha.ip,
    "PORT": Iroha.port,
    "ACCOUNT_ID": Iroha.account_id,
    "CREATED_AT": Iroha.created_at,
    "UPDATED_AT": Iroha.updated_at,
}


class IrohaDao:
    @staticmethod
    def get_irohas(page: int, size: int, order_by: Iroha, order_method: str) -> List[Iroha]:
        """
        Get a list of the iroha from the database by query parameters.
        :return: A list containing Iroha model objects.
        """
        irohas = Iroha.query
        irohas = safe_order_by(irohas, _IROHA_ALLOWED_COLUMNS, order_by, order_method)

        if page:
            irohas = irohas.offset((page - 1) * size)

        if size:
            irohas = irohas.limit(size)

        return irohas.all()

    @staticmethod
    def get_iroha_by_id(iroha_id: int) -> Iroha:
        """
            Get a single iroha from the database based on iroha id.
            :param iroha_id: Iroha ID which uniquely identifies the Iroha.
            :return: The result of the database query
            """
        return Iroha.query.get(iroha_id)

    @staticmethod
    def add_iroha(iroha: Iroha) -> bool:
        """
            Add a Iroha to database
            :param iroha: Iroha object representing an Iroha for the application.
            :return: True if the iroha is inserted into the database, False otherwise.
        """
        db.session.add(iroha)
        return BasicDao.safe_commit()

    @staticmethod
    def update_iroha(iroha_id: int, iroha: Iroha) -> bool:
        """
            Update Iroha in the database.
            :param iroha_id: Iroha ID which uniquely identifies the Iroha.
            :param iroha: Iroha object representing an Iroha for the application.
            :return: True if the iroha is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE iroha SET
                environment_id=:environment_id,
                updated_at=:updated_at,
                updated_by=:updated_by,
                ip=:ip,
                port=:port,
                account_id=:account_id
            WHERE iroha_id=:iroha_id
            """),
            {
                "environment_id": iroha.environment_id,
                "updated_at": datetime.now(),
                "updated_by": iroha.updated_by,
                "ip": iroha.ip,
                "port": iroha.port,
                "account_id": iroha.account_id,
                "iroha_id": iroha_id,
            },
        )
        return BasicDao.safe_commit()
