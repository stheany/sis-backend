"""
Status data access object from SIS Oracle database. Contains SQL queries related to status.
"""
from typing import List

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.status import Status
from application.utils.query_sanitizer import safe_order_by

_STATUS_ALLOWED_COLUMNS = {
    "STATUS_ID": Status.status_id,
    "STATUS_NAME": Status.status_name,
    "DESCRIPTION": Status.description,
}


class StatusDao:
    @staticmethod
    def get_status(page: int, size: int, orderBy: Status, orderMethod: str) -> List[Status]:
        """
        Get a list of the actions from the database by query parameters.
        :return: A list containing Action model objects.
        """
        status = Status.query
        status = safe_order_by(status, _STATUS_ALLOWED_COLUMNS, orderBy, orderMethod)

        if page:
            status = status.offset((page - 1) * size)

        if size:
            status = status.limit(size)

        return status.all()

    @staticmethod
    def get_status_by_id(status_id: int) -> Status:
        """
        Get a single status from the database based on status id.
        :param status_id: Status ID which uniquely identifies the status.
        :return: The result of the database query
        """
        return Status.query.get(status_id)

    @staticmethod
    def add_status(status: Status) -> bool:
        """
        Add an status to database
        :param status: Status object representing an status for the application.
        :return: True if the status is inserted into the database, False otherwise.
        """
        db.session.add(status)
        return BasicDao.safe_commit()

    @staticmethod
    def update_status(status_id: int, status: Status) -> bool:
        """
        Update status in the database.
        :param status_id: Status ID which uniquely identifies the status.
        :param status: Status object representing status for the application.
        :return: True if the status is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE status SET
                status_name=:status_name,
                description=:description
            WHERE status_id=:status_id
            """),
            {
                "status_name": status.status_name,
                "description": status.description,
                "status_id": status_id,
            },
        )
        return BasicDao.safe_commit()
