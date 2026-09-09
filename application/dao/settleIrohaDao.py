"""
SettleIroha data access object from SIS Oracle database. Contains SQL queries related to SettleIroha.
"""
from typing import List

from application import db
from application.dao.basicDao import BasicDao
from application.models.settleIroha import SettleIroha


class SettleIrohaDao:
    @staticmethod
    def get_settle_iroha_by_id(settle_iroha_id: int) -> SettleIroha:
        """
            Get a single SettleIroha from the database based on SettleIroha id.
            :param settle_iroha_id: SettleIroha ID which uniquely identifies the SettleIroha.
            :return: The result of the database query.
            """
        return SettleIroha.query.get(settle_iroha_id)

    @staticmethod
    def get_settle_iroha() -> List[SettleIroha]:
        """
            Get a list of SettleIroha from the database.
            :return: The result of the database query.
            """
        return SettleIroha.query.all()

    @staticmethod
    def add_settle_iroha(settle_iroha: SettleIroha) -> bool:
        """
            Add a SettleIroha to database
            :param settle_iroha: SettleIroha object representing a SettleIroha for the application.
            :return: True if the SettleIroha is inserted into the database, False otherwise.
        """
        db.session.add(settle_iroha)
        return BasicDao.safe_commit()
