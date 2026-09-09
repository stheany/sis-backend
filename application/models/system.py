"""
System ORM model for the 'SYSTEM' table in SIS Oracle database.
"""
from application import db


class System(db.Model):
    def __init__(self, system: dict):
        """
        Initialize a System by passing in a dictionary
        :param system: A dictionary with fields matching the System fields
        """
        self.system_id = system.get("system_id")
        self.system_name = system.get("system_name")
        self.short_name = system.get("short_name")
        self.bic_code = system.get("bic_code")
        self.settlement_account_number = system.get("settlement_account_number")
        self.url = system.get("url")
        self.ip_address = system.get("ip_address")
        self.status = system.get("status")
        self.created_at = system.get("created_at")
        self.created_by = system.get("created_by")
        self.updated_at = system.get("updated_at")
        self.updated_by = system.get("updated_by")

    __tablename__ = "system"

    # Data Columns
    system_id = db.Column(db.Integer(), primary_key=True)
    system_name = db.Column(db.String(500))
    short_name = db.Column(db.String(10))
    bic_code = db.Column(db.String(11))
    settlement_account_number = db.Column(
        db.String(50),
        comment="Registered settlement/debit account number for this bank, exposed via getCBSAccountBalanceNCS")
    url = db.Column(db.String(500))
    ip_address = db.Column(db.String(500))
    status = db.Column(db.String(10))
    created_at = db.Column(db.DateTime())
    created_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
    updated_at = db.Column(db.DateTime())
    updated_by = db.Column(db.Integer(), db.ForeignKey("users_login_sis.users_login_sis_id"))
