"""
SettlementIrohaContentDetail data access object from SIS Oracle database. Contains SQL queries related to SettlementIrohaContentDetail.
"""
from typing import List

from application import db
from application.dao.basicDao import BasicDao
from application.models.settlementIrohaContentDetail import SettlementIrohaContentDetail


class SettlementIrohaContentDetailDao:
    @staticmethod
    def get_settlement_iroha_content_detail_by_id(
            settlement_iroha_content_detail_id: int) -> SettlementIrohaContentDetail:
        """
            Get a single SettlementIrohaContentDetail from the database based on SettlementIrohaContentDetail id.
            :param settlement_iroha_content_detail_id:
                SettlementIrohaContentDetail ID which uniquely identifies the SettlementIrohaContentDetail.
            :return: The result of the database query.
            """
        return SettlementIrohaContentDetail.query.get(settlement_iroha_content_detail_id)

    @staticmethod
    def get_settlement_iroha_content_detail() -> List[SettlementIrohaContentDetail]:
        """
            Get a list of SettlementIrohaContentDetail from the database.
            :return: The result of the database query.
            """
        return SettlementIrohaContentDetail.query.all()

    @staticmethod
    def add_settlement_iroha_content_detail(settlement_iroha_content_detail: SettlementIrohaContentDetail) -> bool:
        """
            Add a SettlementIrohaContentDetail to database
            :param settlement_iroha_content_detail:
                SettlementIrohaContentDetail object representing a SettlementIrohaContentDetail for the application.
            :return: True if the SettlementIrohaContentDetail is inserted into the database, False otherwise.
        """
        db.session.add(settlement_iroha_content_detail)
        return BasicDao.safe_commit()
