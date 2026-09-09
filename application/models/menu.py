"""
Menu ORM model for the 'MENU' table in SIS Oracle database.
"""
from application import db


class Menu(db.Model):
    def __init__(self, menu: dict):
        """
        Initialize a Menu by passing in a dictionary
        :param menu: A dictionary with fields matching the Menu fields
        """
        self.menu_id = menu.get("menu_id")
        self.name = menu.get("name")
        self.description = menu.get("description")
        self.status = menu.get("status")
        self.created_at = menu.get("created_at")
        self.created_by = menu.get("created_by")
        self.updated_at = menu.get("updated_at")
        self.updated_by = menu.get("updated_by")
        self.url = menu.get("url")
        self.icon = menu.get("icon")

    __tablename__ = "menu"

    # Data Columns
    menu_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(500))
    description = db.Column(db.String(2500))
    status = db.Column(db.String(10))
    created_at = db.Column(db.DateTime())
    created_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    updated_at = db.Column(db.DateTime())
    updated_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    url = db.Column(db.String(250))
    icon = db.Column(db.String(500))
