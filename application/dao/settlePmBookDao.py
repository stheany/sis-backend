"""
SettlePmBook data access object for SIS Oracle database.
Contains SQL queries related to SettlePmBook.
"""
from typing import List, Optional

from application import db
from application.dao.basicDao import BasicDao
from application.models.settlePmBook import SettlePmBook


class SettlePmBookDao:
    @staticmethod
    def get_settle_pm_book_by_id(settle_pm_book_id: int) -> Optional[SettlePmBook]:
        """
        Get a single SettlePmBook from the database based on id.

        :param settle_pm_book_id: Primary key of SettlePmBook
        :return: SettlePmBook instance or None
        """
        return SettlePmBook.query.get(settle_pm_book_id)

    @staticmethod
    def get_settle_pm_books() -> List[SettlePmBook]:
        """
        Get a list of all SettlePmBook rows.

        :return: List of SettlePmBook
        """
        return SettlePmBook.query.all()

    @staticmethod
    def add_settle_pm_book(settle_pm_book: SettlePmBook) -> bool:
        """
        Add a SettlePmBook row.

        :param settle_pm_book: SettlePmBook instance to insert
        :return: True if commit succeeded, False otherwise
        """
        db.session.add(settle_pm_book)
        return BasicDao.safe_commit()

    @staticmethod
    def update_status(settle_pm_book_id: int,
                      settlement_status_id: int,
                      flexcube_response_status_id: int | None = None) -> bool:
        """
        Update settlement and optional flexcube response status.

        :param settle_pm_book_id: PK
        :param settlement_status_id: new settlement status id
        :param flexcube_response_status_id: optional flexcube status id
        """
        obj = SettlePmBook.query.get(settle_pm_book_id)
        if not obj:
            return False
        obj.settlement_status_id = settlement_status_id
        if flexcube_response_status_id is not None:
            obj.flexcube_response_status_id = flexcube_response_status_id
        return BasicDao.safe_commit()

    @staticmethod
    def find_by_reference(reference_id: str) -> Optional[SettlePmBook]:
        """
        Find a SettlePmBook by reference_id (unique).

        :param reference_id: external idempotency key
        """
        return SettlePmBook.query.filter_by(reference_id=reference_id).first()