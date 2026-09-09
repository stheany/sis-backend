"""
UserRole ORM model for the 'USER_ROLE' table in SIS Oracle database.
"""
from sqlalchemy import UniqueConstraint
from application import db


class UserRole(db.Model):
    def __init__(self, user_role: dict):
        """
        Initialize a UserRole by passing in a dictionary
        :param user_role: A dictionary with fields matching the UserRole fields
        """
        self.user_role_id = user_role.get("user_role_id")
        self.role_id = user_role.get("role_id")
        self.users_login_sis_id = user_role.get("users_login_sis_id")
        self.created_at = user_role.get("created_at")
        self.created_by = user_role.get("created_by")
        self.updated_at = user_role.get("updated_at")
        self.updated_by = user_role.get("updated_by")
        self.blocked_at = user_role.get("blocked_at")
        self.blocked_by = user_role.get("blocked_by")

    __tablename__ = "user_role"
    __table_args__ = (
        UniqueConstraint("users_login_sis_id", "role_id", name="uq_user_role_user_role"),
    )

    # Data Columns
    user_role_id = db.Column(
        db.Integer(), primary_key=True)
    role_id = db.Column(db.Integer(), db.ForeignKey("role.role_id"))
    users_login_sis_id = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    created_at = db.Column(db.DateTime())
    created_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    updated_at = db.Column(db.DateTime())
    updated_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    blocked_at = db.Column(db.DateTime())
    blocked_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
