"""
Permission ORM model for the 'PERMISSION' table in SIS Oracle database.
"""
from application import db


class Permission(db.Model):
    def __init__(self, permission: dict):
        """
        Initialize a Permission by passing in a dictionary
        :param permission: A dictionary with fields matching the Permission fields
        """
        self.permission_id = permission.get("permission_id")
        self.role_id = permission.get("role_id")
        self.action_id = permission.get("action_id")
        self.menu_id = permission.get("menu_id")
        self.created_at = permission.get("created_at")
        self.created_by = permission.get("created_by")
        self.updated_at = permission.get("updated_at")
        self.updated_by = permission.get("updated_by")

    __tablename__ = "permission"

    # Data Columns
    permission_id = db.Column(
        db.Integer(), db.Identity(
            start=1), primary_key=True)
    role_id = db.Column(db.Integer(), db.ForeignKey("role.role_id"))
    action_id = db.Column(db.Integer(), db.ForeignKey("action.action_id"))
    menu_id = db.Column(db.Integer(), db.ForeignKey("menu.menu_id"))
    created_at = db.Column(db.DateTime())
    created_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    updated_at = db.Column(db.DateTime())
    updated_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
