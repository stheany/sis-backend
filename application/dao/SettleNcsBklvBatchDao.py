"""
SettleNcsBklvBatch data access object from SIS Oracle database.
Contains SQL queries related to NCS-submitted BKLV netfile batches.
"""
from typing import List

from application import db
from application.dao.basicDao import BasicDao
from application.dao.settleNcsBklvBatch import SettleNcsBklvBatch


class SettleNcsBklvBatchDao:
    @staticmethod
    def get_by_id(settle_ncs_bklv_batch_id: int) -> SettleNcsBklvBatch:
        """
        Get a single SettleNcsBklvBatch from the database based on its id.
        :param settle_ncs_bklv_batch_id: SettleNcsBklvBatch ID which uniquely identifies the batch.
        :return: The result of the database query.
        """
        return SettleNcsBklvBatch.query.get(settle_ncs_bklv_batch_id)

    @staticmethod
    def get_by_file_name(file_name: str) -> SettleNcsBklvBatch:
        """
        Get a single SettleNcsBklvBatch from the database based on netfile name.
        :param file_name: The submitted netfile name (pFileName).
        :return: The result of the database query, or None.
        """
        return SettleNcsBklvBatch.query.filter_by(file_name=file_name).first()

    @staticmethod
    def get_all() -> List[SettleNcsBklvBatch]:
        """
        Get a list of all SettleNcsBklvBatch from the database.
        :return: The result of the database query.
        """
        return SettleNcsBklvBatch.query.all()

    @staticmethod
    def add(settle_ncs_bklv_batch: SettleNcsBklvBatch) -> bool:
        """
        Add a SettleNcsBklvBatch to database.
        :param settle_ncs_bklv_batch: SettleNcsBklvBatch object representing a netfile batch.
        :return: True if the SettleNcsBklvBatch is inserted into the database, False otherwise.
        """
        db.session.add(settle_ncs_bklv_batch)
        return BasicDao.safe_commit()
