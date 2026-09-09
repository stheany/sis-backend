"""
Settlement Iroha Content Detail ORM model for the 'SETTLEMENT_CBS_CONTENT_DETAIL' table in SIS Oracle database
"""
from application import db


class SettlementIrohaContentDetail(db.Model):
    def __init__(self, settlement_iroha_content_detail: dict):
        """
        Initialize a SettlementIrohaContentDetail by passing in a dictionary
        :param settlement_iroha_content_detail: A dictionary with fields matching the SettlementIrohaContentDetail fields
        """
        self.settle_iroha_con_detail_id = settlement_iroha_content_detail.get("settle_iroha_con_detail_id")
        self.settle_iroha_id = settlement_iroha_content_detail.get("settle_iroha_id")
        self.currency_code = settlement_iroha_content_detail.get("currency_code")
        self.sender_account_id = settlement_iroha_content_detail.get("sender_account_id")
        self.receiver_account_id = settlement_iroha_content_detail.get("receiver_account_id")
        self.amount = settlement_iroha_content_detail.get("amount")
        self.description = settlement_iroha_content_detail.get("description")
        self.iroha_id = settlement_iroha_content_detail.get("iroha_id")

    __tablename__ = "settlement_iroha_content_detail"

    # Data Columns
    settle_iroha_con_detail_id = db.Column(
        db.Integer(), primary_key=True)
    settle_iroha_id = db.Column(
        db.Integer(),
        db.ForeignKey("settle_iroha.settle_iroha_id"),
        nullable=False)
    currency_code = db.Column(db.String(3), nullable=False)
    sender_account_id = db.Column(db.String(), nullable=False)
    receiver_account_id = db.Column(db.String(), nullable=False)
    amount = db.Column(db.Float(precision=6), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    iroha_id = db.Column(
        db.Integer(),
        db.ForeignKey("iroha.iroha_id"),
        nullable=False)
