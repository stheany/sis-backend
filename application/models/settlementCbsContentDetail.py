"""
Settlement CBS Content Detail ORM model for the 'SETTLEMENT_CBS_CONTENT_DETAIL' table in SIS Oracle database
"""
from application import db


class SettlementCbsContentDetail(db.Model):
    def __init__(self, settlement_cbs_content_detail: dict):
        """
        Initialize a SettlementCbsContentDetail by passing in a dictionary
        :param settlement_cbs_content_detail: A dictionary with fields matching the SettlementCbsContentDetail fields
        """
        self.settle_cbs_con_detail_id = settlement_cbs_content_detail.get("settle_cbs_con_detail_id")
        self.settle_cbs_id = settlement_cbs_content_detail.get("settle_cbs_id")
        self.currency_code = settlement_cbs_content_detail.get("currency_code")
        self.customer_account = settlement_cbs_content_detail.get("customer_account")
        self.cr_dr = settlement_cbs_content_detail.get("cr_dr")
        self.amount = settlement_cbs_content_detail.get("amount")
        self.transaction_code = settlement_cbs_content_detail.get("transaction_code")
        self.entry_date = settlement_cbs_content_detail.get("entry_date")
        self.value_date = settlement_cbs_content_detail.get("value_date")
        self.financial_year = settlement_cbs_content_detail.get("financial_year")
        self.financial_period = settlement_cbs_content_detail.get("financial_period")
        self.description = settlement_cbs_content_detail.get("description")
        self.flexcube_id = settlement_cbs_content_detail.get("flexcube_id")

    __tablename__ = "settlement_cbs_content_detail"

    # Data Columns
    settle_cbs_con_detail_id = db.Column(
        db.Integer(), primary_key=True)
    settle_cbs_id = db.Column(db.Integer(),
                              db.ForeignKey("settle_cbs.settle_cbs_id"))
    currency_code = db.Column(db.String(3), nullable=False)
    customer_account = db.Column(db.String(20), nullable=False)
    cr_dr = db.Column(db.String(5), nullable=False)
    amount = db.Column(db.Float(precision=6), nullable=False)
    transaction_code = db.Column(db.String(5))
    entry_date = db.Column(db.DateTime(), nullable=False)
    value_date = db.Column(db.DateTime(), nullable=False)
    financial_year = db.Column(db.String(5), nullable=False)
    financial_period = db.Column(db.String(5), nullable=False)
    description = db.Column(db.String(500))
    flexcube_id = db.Column(db.Integer(),
                            db.ForeignKey("flexcube.flexcube_id"))
