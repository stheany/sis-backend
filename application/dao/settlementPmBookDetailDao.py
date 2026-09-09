"""
SettlementPmBookDetail data access object for SIS Oracle database.
Contains SQL queries related to SettlementPmBookDetail.
"""
from typing import List

from application import db
from application.dao.basicDao import BasicDao
from application.models.settlementPmBookDetail import SettlementPmBookDetail


class SettlementPmBookDetailDao:
    @staticmethod
    def get_settlement_pm_book_detail_by_id(detail_id: int) -> SettlementPmBookDetail | None:
        """
        Get a single SettlementPmBookDetail by id.

        :param detail_id: Primary key of SettlementPmBookDetail
        :return: SettlementPmBookDetail or None
        """
        return SettlementPmBookDetail.query.get(detail_id)

    @staticmethod
    def get_by_settle_pm_book_id(settle_pm_book_id: int) -> List[SettlementPmBookDetail]:
        """
        List all details for a given SettlePmBook.

        :param settle_pm_book_id: FK to SettlePmBook
        :return: List of SettlementPmBookDetail
        """
        return SettlementPmBookDetail.query.filter_by(
            settle_pm_book_id=settle_pm_book_id
        ).all()

    @staticmethod
    def add_settlement_pm_book_detail(detail: SettlementPmBookDetail) -> bool:
        """
        Insert one detail row.

        :param detail: SettlementPmBookDetail instance
        """
        db.session.add(detail)
        return BasicDao.safe_commit()

    @staticmethod
    def add_batch(details: List[SettlementPmBookDetail]) -> bool:
        """
        Bulk-insert many detail rows (same transaction).

        :param details: list of SettlementPmBookDetail instances
        """
        db.session.add_all(details)
        return BasicDao.safe_commit()