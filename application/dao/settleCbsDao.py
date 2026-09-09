"""
SettleCbs data access object from SIS Oracle database. Contains SQL queries related to SettleCbs.
"""
from typing import List

from application import db
from application.dao.basicDao import BasicDao
from application.models.settleCbs import SettleCbs


class SettleCbsDao:
    @staticmethod
    def get_settle_cbs_by_id(settle_cbs_id: int) -> SettleCbs:
        """
            Get a single SettleCbs from the database based on SettleCbs id.
            :param settle_cbs_id: SettleCbs ID which uniquely identifies the SettleCbs.
            :return: The result of the database query
            """
        return SettleCbs.query.get(settle_cbs_id)

    @staticmethod
    def get_settle_cbs() -> List[SettleCbs]:
        """
            Get a list of SettleCbs from the database.
            :return: The result of the database query.
            """
        return SettleCbs.query.all()

    @staticmethod
    def add_settle_cbs(settle_cbs: SettleCbs) -> bool:
        """
            Add a SettleCbs to database
            :param settle_cbs: SettleCbs object representing a SettleCbs for the application.
            :return: True if the SettleCbs is inserted into the database, False otherwise.
        """
        db.session.add(settle_cbs)
        return BasicDao.safe_commit()
