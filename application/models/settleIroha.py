"""
Settle Iroha ORM model for the 'SETTLE_IROHA' table in SIS Oracle database.
"""
from application import db


class SettleIroha(db.Model):
    def __init__(self, settle_iroha: dict):
        """
        Initialize a SettleIroha by passing in a dictionary
        :param settle_iroha: A dictionary with fields matching the SettleIroha fields
        """
        self.settle_iroha_id = settle_iroha.get("settle_iroha_id")
        self.system_id = settle_iroha.get("system_id")
        self.settlement_iroha_content = settle_iroha.get("settlement_iroha_content")
        self.settlement_status_id = settle_iroha.get("settlement_status_id")
        self.created_at = settle_iroha.get("created_at")
        self.updated_at = settle_iroha.get("updated_at")
        self.sent_at = settle_iroha.get("sent_at")
        self.iroha_content = settle_iroha.get("iroha_content")
        self.iroha_response_status_id = settle_iroha.get("iroha_response_status_id")
        self.iroha_response_transaction_hash = settle_iroha.get("iroha_response_transaction_hash")
        self.iroha_response_at = settle_iroha.get("iroha_response_at")
        self.iroha_message = settle_iroha.get("iroha_message")
        self.reference_id = settle_iroha.get("reference_id")

    __tablename__ = "settle_iroha"

    # Data Columns
    settle_iroha_id = db.Column(
        db.Integer(), db.Identity(
            start=1), primary_key=True)
    system_id = db.Column(
        db.Integer(),
        db.ForeignKey("system.system_id"),
        nullable=False)
    settlement_iroha_content = db.Column(
        db.Text(),
        nullable=False,
        comment="Content of the system that send to SIS")
    settlement_status_id = db.Column(
        db.Integer(),
        db.ForeignKey("status.status_id"),
        nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())
    sent_at = db.Column(db.DateTime(),
                        comment="Date and time send to iroha")
    iroha_content = db.Column(db.Text(),
                              comment="Content of the SIS sends to iroha")
    iroha_response_status_id = db.Column(
        db.Integer(),
        db.ForeignKey("status.status_id"),
        comment="Iroha response status id")
    iroha_response_transaction_hash = db.Column(
        db.Text(), comment="Iroha response translation hash")
    iroha_response_at = db.Column(db.DateTime())
    iroha_message = db.Column(db.Text())
    reference_id = db.Column(db.Integer())
