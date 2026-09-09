"""
SettlementCbsContentDetail data access object from SIS Oracle database. Contains SQL queries related to SettlementCbsContentDetail.
"""
from typing import List

from application import db
from application.dao.basicDao import BasicDao
from application.models.settlementCbsContentDetail import SettlementCbsContentDetail


class SettlementCbsContentDetailDao:
    @staticmethod
    def get_settlement_cbs_content_detail_by_id(settlement_cbs_content_detail_id: int) -> SettlementCbsContentDetail:
        """
            Get a single SettlementCbsContentDetail from the database based on SettlementCbsContentDetail id.
            :param settlement_cbs_content_detail_id:
                SettlementCbsContentDetail ID which uniquely identifies the SettlementCbsContentDetail.
            :return: The result of the database query.
            """
        return SettlementCbsContentDetail.query.get(settlement_cbs_content_detail_id)

    @staticmethod
    def get_settlement_cbs_content_detail() -> List[SettlementCbsContentDetail]:
        """
            Get a list of SettlementCbsContentDetail from the database.
            :return: The result of the database query.
            """
        return SettlementCbsContentDetail.query.all()

    @staticmethod
    def add_settlement_cbs_content_detail(settlement_cbs_content_detail: SettlementCbsContentDetail) -> bool:
        """
            Add a SettlementCbsContentDetail to database
            :param settlement_cbs_content_detail:
                SettlementCbsContentDetail object representing a SettlementCbsContentDetail for the application.
            :return: True if the SettlementCbsContentDetail is inserted into the database, False otherwise.
        """
        db.session.add(settlement_cbs_content_detail)
        return BasicDao.safe_commit()
