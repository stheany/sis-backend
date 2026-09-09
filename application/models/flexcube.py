"""
Flexcube ORM model for the 'FLEXCUBE' table in SIS Oracle database.
"""
from application import db


class Flexcube(db.Model):
    def __init__(self, flexcube: dict):
        """
        Initialize a Flexcube by passing in a dictionary
        :param flexcube: A dictionary with fields matching the Flexcube fields
        """
        self.flexcube_id = flexcube.get("flexcube_id")
        self.username = flexcube.get("username")
        self.password = flexcube.get("password")
        self.environment_id = flexcube.get("environment_id")
        self.flexcube_url = flexcube.get("flexcube_url")
        self.source = flexcube.get("source")
        self.ubscomp = flexcube.get("ubscomp")
        self.user_id = flexcube.get("user_id")
        self.branch = flexcube.get("branch")
        self.module_id = flexcube.get("module_id")
        self.service = flexcube.get("service")
        self.created_at = flexcube.get("created_at")
        self.created_by = flexcube.get("created_by")
        self.updated_at = flexcube.get("updated_at")
        self.updated_by = flexcube.get("updated_by")

    __tablename__ = "flexcube"

    # Data Columns
    flexcube_id = db.Column(
        db.Integer(), primary_key=True)
    username = db.Column(
        db.String(250),
        comment="Username for login to flexcube")
    password = db.Column(
        db.String(255),
        comment="Password for login to flexcube")
    environment_id = db.Column(
        db.Integer(), db.ForeignKey("environment.env_id"))
    flexcube_url = db.Column(db.String(500))
    source = db.Column(db.String(255))
    ubscomp = db.Column(db.String(255))
    user_id = db.Column(db.String(255), nullable=False,
                        comment="User operating transaction")
    branch = db.Column(
        db.String(255),
        nullable=False,
        comment="Branch Code of the account where the account is opened.")
    module_id = db.Column(db.String(255))
    service = db.Column(db.String(255))
    created_at = db.Column(db.DateTime())
    created_by = db.Column(db.Integer(), db.ForeignKey(
        "users_login_sis.users_login_sis_id"))
    updated_at = db.Column(db.DateTime())
    updated_by = db.Column(db.Integer(), db.ForeignKey(
        "users_login_sis.users_login_sis_id"))
