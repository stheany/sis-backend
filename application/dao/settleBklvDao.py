"""
SettleBklv data access object from SIS Oracle database.
Contains SQL queries related to BKLV fund transfer settlements.
"""
from typing import List

from application import db
from application.dao.basicDao import BasicDao
from application.models.settleBklv import SettleBklv


class SettleBklvDao:
    @staticmethod
    def get_settle_bklv_by_id(settle_bklv_id: int) -> SettleBklv:
        """
        Get a single SettleBklv from the database based on SettleBklv id.
        :param settle_bklv_id: SettleBklv ID which uniquely identifies the SettleBklv.
        :return: The result of the database query.
        """
        return SettleBklv.query.get(settle_bklv_id)

    @staticmethod
    def get_settle_bklv_by_ext_ref(ext_ref: str) -> SettleBklv:
        """
        Get a single SettleBklv from the database based on external reference.
        Used for idempotency checks.
        :param ext_ref: External reference ID.
        :return: The result of the database query.
        """
        return SettleBklv.query.filter_by(ext_ref=ext_ref).first()

    @staticmethod
    def get_settle_bklv() -> List[SettleBklv]:
        """
        Get a list of SettleBklv from the database.
        :return: The result of the database query.
        """
        return SettleBklv.query.all()

    @staticmethod
    def add_settle_bklv(settle_bklv: SettleBklv) -> bool:
        """
        Add a SettleBklv to database
        :param settle_bklv: SettleBklv object representing a BKLV settlement.
        :return: True if the SettleBklv is inserted into the database, False otherwise.
        """
        db.session.add(settle_bklv)
        return BasicDao.safe_commit()

    @staticmethod
    def get_by_batch_id(batch_id: int) -> List[SettleBklv]:
        """
        Get all SettleBklv lines belonging to a NCS netfile batch, ordered by
        line_no, for getFile_Status_Detail's status rollup.
        :param batch_id: SettleNcsBklvBatch id.
        :return: The result of the database query.
        """
        return SettleBklv.query.filter_by(batch_id=batch_id).order_by(SettleBklv.line_no).all()