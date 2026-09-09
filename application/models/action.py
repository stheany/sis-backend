"""
Action ORM model for the 'ACTION' table in SIS Oracle database.
"""
from application import db


class Action(db.Model):
    def __init__(self, action: dict):
        """
        Initialize a Action by passing in a dictionary.
        :param action: A dictionary with fields matching the Action fields
        """
        self.action_id = action.get("action_id")
        self.name = action.get("name")
        self.description = action.get("description")
        self.status = action.get("status")
        self.url = action.get("url")
        self.created_at = action.get("created_at")
        self.created_by = action.get("created_by")
        self.updated_at = action.get("updated_at")
        self.updated_by = action.get("updated_by")

    __tablename__ = "action"

    # Data Columns
    action_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(500))
    description = db.Column(db.String(2500))
    status = db.Column(db.Integer())
    url = db.Column(db.String(2500))
    created_at = db.Column(db.DateTime())
    created_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    updated_at = db.Column(db.DateTime())
    updated_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
