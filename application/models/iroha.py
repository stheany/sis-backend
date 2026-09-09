"""
Iroha ORM model for the 'IROHA' table in SIS Oracle database.
"""
from application import db


class Iroha(db.Model):
    def __init__(self, iroha: dict):
        """
        Initialize a Iroha by passing in a dictionary
        :param iroha: A dictionary with fields matching the Iroha fields
        """
        self.iroha_id = iroha.get("iroha_id")
        self.environment_id = iroha.get("environment_id")
        self.created_at = iroha.get("created_at")
        self.created_by = iroha.get("created_by")
        self.updated_at = iroha.get("updated_at")
        self.updated_by = iroha.get("updated_by")
        self.ip = iroha.get("ip")
        self.port = iroha.get("port")
        self.account_id = iroha.get("account_id")

    __tablename__ = "iroha"

    # Data Columns
    iroha_id = db.Column(db.Integer(), primary_key=True)
    environment_id = db.Column(
        db.Integer(),
        db.ForeignKey("environment.env_id"),
        nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    created_by = db.Column(
        db.Integer(),
        db.ForeignKey("users_login_sis.users_login_sis_id"),
        nullable=False)
    updated_at = db.Column(db.DateTime(), nullable=False)
    updated_by = db.Column(
        db.Integer(),
        db.ForeignKey("users_login_sis.users_login_sis_id"),
        nullable=False)
    ip = db.Column(db.String(250), nullable=False)
    port = db.Column(db.Integer(), nullable=False)
    account_id = db.Column(db.String(255), nullable=False)
