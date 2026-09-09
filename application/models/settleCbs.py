"""
Settle CBS ORM model for the 'SETTLE_CBS' table in SIS Oracle database.
"""
from application import db


class SettleCbs(db.Model):
    def __init__(self, settle_cbs: dict):
        """
        Initialize a SettleCbs by passing in a dictionary
        :param settle_cbs: A dictionary with fields matching the SettleCbs fields
        """
        self.settle_cbs_id = settle_cbs.get("settle_cbs_id")
        self.system_id = settle_cbs.get("system_id")
        self.settlement_cbs_content = settle_cbs.get("settlement_cbs_content")
        self.settlement_status_id = settle_cbs.get("settlement_status_id")
        self.created_at = settle_cbs.get("created_at")
        self.sent_at = settle_cbs.get("sent_at")
        self.flexcube_content = settle_cbs.get("flexcube_content")
        self.flexcube_response_status_id = settle_cbs.get("flexcube_response_status_id")
        self.flexcube_response_at = settle_cbs.get("flexcube_response_at")
        self.flexcube_message = settle_cbs.get("flexcube_message")
        self.reference_id = settle_cbs.get("reference_id")

    __tablename__ = "settle_cbs"

    # Data Columns
    settle_cbs_id = db.Column(
        db.Integer(), primary_key=True)
    system_id = db.Column(db.Integer(), db.ForeignKey("system.system_id"))
    settlement_cbs_content = db.Column(db.Text())
    settlement_status_id = db.Column(
        db.Integer(), db.ForeignKey("status.status_id"))
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())
    sent_at = db.Column(db.DateTime())
    flexcube_content = db.Column(db.Text())
    flexcube_response_status_id = db.Column(
        db.Integer(), db.ForeignKey("status.status_id"))
    flexcube_response_at = db.Column(db.DateTime())
    flexcube_message = db.Column(db.Text())
    reference_id = db.Column(db.Integer())
