"""
Status ORM model for the 'STATUS' table in SIS Oracle database.
"""
from application import db


class Status(db.Model):
    def __init__(self, status: dict):
        """
        Initialize a Status by passing in a dictionary
        :param status: A dictionary with fields matching the Status fields
        """
        self.status_id = status.get("status_id")
        self.status_name = status.get("status_name")
        self.description = status.get("description")

    __tablename__ = "status"

    status_id = db.Column(db.Integer(), primary_key=True)
    status_name = db.Column(db.String(250))
    description = db.Column(db.String(500))
