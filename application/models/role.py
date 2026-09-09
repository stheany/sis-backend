"""
Role ORM model for the 'ROLE' table in SIS Oracle database.
"""
from application import db


class Role(db.Model):
    def __init__(self, role: dict):
        """
        Initialize a Role by passing in a dictionary
        :param role: A dictionary with fields matching the Role fields
        """
        self.role_id = role.get("role_id")
        self.name = role.get("name")
        self.description = role.get("description")
        self.status = role.get("status")
        self.created_at = role.get("created_at")
        self.created_by = role.get("created_by")
        self.updated_at = role.get("updated_at")
        self.updated_by = role.get("updated_by")

    __tablename__ = "role"

    # Data Columns
    role_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(500))
    description = db.Column(db.String(2500))
    status = db.Column(db.String(10))
    created_at = db.Column(db.DateTime())
    created_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    updated_at = db.Column(db.DateTime())
    updated_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
