"""
TokenBlocklist ORM model for the 'TOKEN_BLOCK_LIST' table in SIS Oracle database.
"""
from application import db


class TokenBlocklist(db.Model):
    def __init__(self, token_block_list: dict):
        """
        Initialize a TokenBlocklist by passing in a dictionary
        :param token_block_list: A dictionary with fields matching the TokenBlocklist fields
        """
        self.id = token_block_list.get("id")
        self.jti = token_block_list.get("jti")
        self.created_at = token_block_list.get("created_at")
        self.remark = token_block_list.get("remark")

    __tablename__ = "token_blocklist"

    # Data Columns
    id = db.Column(db.Integer(), primary_key=True)
    jti = db.Column(db.String(200), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
    remark = db.Column(db.String(500))
