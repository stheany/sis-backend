"""
SystemLoginSis ORM model for the 'SYSTEM_LOGIN_SIS' table in SIS Oracle database.
"""
from application import db


class SystemLoginSis(db.Model):
    def __init__(self, system_login_sis: dict):
        """
        Initialize a SystemLoginSis by passing in a dictionary
        :param system_login_sis: A dictionary with fields matching the SystemLoginSis fields
        """
        self.system_login_sis_id = system_login_sis.get("system_login_sis_id")
        self.system_id = system_login_sis.get("system_id")
        self.username = system_login_sis.get("username")
        self.password = system_login_sis.get("password")
        self.status = system_login_sis.get("status")
        self.created_at = system_login_sis.get("created_at")
        self.created_by = system_login_sis.get("created_by")
        self.updated_at = system_login_sis.get("updated_at")
        self.updated_by = system_login_sis.get("updated_by")
        self.blocked_at = system_login_sis.get("blocked_at")
        self.blocked_by = system_login_sis.get("blocked_by")

    __tablename__ = "system_login_sis"

    system_login_sis_id = db.Column(
        db.Integer(), primary_key=True)
    system_id = db.Column(db.Integer(), db.ForeignKey("system.system_id"))
    username = db.Column(db.String(250))
    password = db.Column(db.String(250))
    status = db.Column(db.Integer())
    created_at = db.Column(db.DateTime())
    created_by = db.Column(db.Integer(), db.ForeignKey(
        "users_login_sis.users_login_sis_id"))
    updated_at = db.Column(db.DateTime())
    updated_by = db.Column(db.Integer(), db.ForeignKey(
        "users_login_sis.users_login_sis_id"))
    blocked_at = db.Column(db.DateTime())
    blocked_by = db.Column(db.Integer(), db.ForeignKey(
        "users_login_sis.users_login_sis_id"))
