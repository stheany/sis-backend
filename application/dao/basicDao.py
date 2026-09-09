"""
Basic Data Access Object with function reused by the other DAOs.
"""

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from application import db


class BasicDao:
    @staticmethod
    def safe_commit() -> bool:
        """
        Safely attempt to commit changes to database.  Rollback in case of a failure.
        :return: True if the commit was successful, False if a rollback occurred.
        """
        try:
            db.session.commit()
            current_app.logger.info("Database Safely Committed")
            return True
        except SQLAlchemyError as error:
            db.session.rollback()
            current_app.logger.error("Database Commit Failed!  Rolling back...")
            current_app.logger.error(error.args)
            return False
        finally:
            db.session.close()
