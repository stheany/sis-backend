"""
SisLoginSystem ORM model for the 'SIS_LOGIN_SYSTEM' table in SIS Oracle database.
"""
from application import db


class SisLoginSystem(db.Model):
    def __init__(self, sis_login_system: dict):
        """
        Initialize a SisLoginSystem by passing in a dictionary
        :param sis_login_system: A dictionary with fields matching the SisLoginSystem fields
        """
        self.sis_login_system_id = sis_login_system.get("sis_login_system_id")
        self.system_id = sis_login_system.get("system_id")
        self.username = sis_login_system.get("username")
        self.password = sis_login_system.get("password")
        self.status = sis_login_system.get("status")
        self.created_at = sis_login_system.get("created_at")
        self.created_by = sis_login_system.get("created_by")
        self.updated_at = sis_login_system.get("updated_at")
        self.updated_by = sis_login_system.get("updated_by")
        self.blocked_at = sis_login_system.get("blocked_at")
        self.blocked_by = sis_login_system.get("blocked_by")

    __tablename__ = "sis_login_system"

    # Data Columns
    sis_login_system_id = db.Column(
        db.Integer(), db.Identity(
            start=1), primary_key=True)
    system_id = db.Column(db.Integer(), db.ForeignKey("system.system_id"))
    username = db.Column(db.String(250))
    password = db.Column(db.String(250))
    status = db.Column(db.Integer())
    created_at = db.Column(db.DateTime())
    created_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    updated_at = db.Column(db.DateTime())
    updated_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    blocked_at = db.Column(db.DateTime())
    blocked_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
