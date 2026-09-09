"""
UserLoginSis ORM model for the 'USER_LOGIN_SIS' table in SIS Oracle database.
"""
from application import db


class UsersLoginSis(db.Model):
    def __init__(self, users_login_sis: dict):
        """
        Initialize a UsersLoginSis by passing in a dictionary
        :param users_login_sis: A dictionary with fields matching the UsersLoginSis fields
        """
        self.users_login_sis_id = users_login_sis.get("users_login_sis_id")
        self.username = users_login_sis.get("username")
        self.password = users_login_sis.get("password")
        self.first_name = users_login_sis.get("first_name")
        self.last_name = users_login_sis.get("last_name")
        self.full_name = users_login_sis.get("full_name")
        self.email = users_login_sis.get("email")
        self.description = users_login_sis.get("description")
        self.status = users_login_sis.get("status")
        self.created_at = users_login_sis.get("created_at")
        self.created_by = users_login_sis.get("created_by")
        self.updated_at = users_login_sis.get("updated_at")
        self.updated_by = users_login_sis.get("updated_by")
        self.blocked_at = users_login_sis.get("blocked_at")
        self.blocked_by = users_login_sis.get("blocked_by")

    __tablename__ = "users_login_sis"

    # Data Columns
    users_login_sis_id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    full_name = db.Column(db.String(500))
    email = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.String(2500))
    status = db.Column(db.Integer())
    created_at = db.Column(db.DateTime())
    created_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    updated_at = db.Column(db.DateTime())
    updated_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    blocked_at = db.Column(db.DateTime())
    blocked_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
