"""
TokenBlockList data access object from SIS Oracle database. Contains SQL queries related to TokenBlockList.
"""
from application import db
from application.dao.basicDao import BasicDao
from application.models.tokenBlocklist import TokenBlocklist


class TokenBlocklistDao:
    @staticmethod
    def get_token_blocklist_by_id(token_blocklist_id: int) -> TokenBlocklist:
        """
            Get a single TokenBlocklist from the database based on TokenBlocklist id.
            :param token_blocklist_id: TokenBlocklist ID which uniquely identifies the TokenBlocklist.
            :return: The result of the database query.
            """
        return TokenBlocklist.query.get(token_blocklist_id)

    @staticmethod
    def get_token_blocklist_by_jti(jti: str) -> TokenBlocklist:
        """
            Get a single TokenBlocklist from the database based on TokenBlocklist jti.
            :param jti: TokenBlocklist jti which uniquely identifies the TokenBlocklist.
            :return: The result of the database query.
            """
        return TokenBlocklist.query.filter_by(jti=jti).scalar()

    @staticmethod
    def add_token_blocklist(token_blocklist: TokenBlocklist) -> bool:
        """
            Add a TokenBlocklist to database
            :param token_blocklist: TokenBlocklist object representing a TokenBlocklist for the application.
            :return: True if the TokenBlocklist is inserted into the database, False otherwise.
        """
        db.session.add(token_blocklist)
        return BasicDao.safe_commit()
