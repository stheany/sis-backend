"""
Environment ORM model for the 'ENVIRONMENT' table in SIS Oracle database.
"""
from application import db


class Environment(db.Model):
    def __init__(self, environment: dict):
        """
        Initialize a Environment by passing in a dictionary
        :param environment: A dictionary with fields matching the Environment fields
        """
        self.env_id = environment.get("env_id")
        self.url = environment.get("url")
        self.name = environment.get("name")
        self.description = environment.get("description")
        self.created_at = environment.get("created_at")
        self.created_by = environment.get("created_by")
        self.updated_at = environment.get("updated_at")
        self.updated_by = environment.get("updated_by")

    __tablename__ = "environment"

    # Data Columns
    env_id = db.Column(db.Integer(), primary_key=True)
    url = db.Column(
        db.String(250),
        nullable=False,
        comment="URL of environment")
    name = db.Column(
        db.String(500),
        nullable=False,
        comment="Name of environment")
    description = db.Column(db.String(2500))
    created_at = db.Column(db.DateTime())
    created_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    updated_at = db.Column(db.DateTime())
    updated_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
