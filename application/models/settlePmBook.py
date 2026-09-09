"""
SettlePmBook ORM model for the 'SETTLE_PM_BOOK' table in SIS Oracle database.
"""
from datetime import datetime, timezone
from application import db


class SettlePmBook(db.Model):
    def __init__(self, settle_pm_book: dict):
        self.settle_pm_book_id = settle_pm_book.get("settle_pm_book_id")
        self.system_id = settle_pm_book.get("system_id")
        self.settlement_status_id = settle_pm_book.get("settlement_status_id")
        self.created_at = settle_pm_book.get("created_at")
        self.updated_at = settle_pm_book.get("updated_at")
        self.sent_at = settle_pm_book.get("sent_at")
        self.flexcube_content = settle_pm_book.get("flexcube_content")
        self.flexcube_response_status_id = settle_pm_book.get("flexcube_response_status_id")
        self.flexcube_response_at = settle_pm_book.get("flexcube_response_at")
        self.flexcube_message = settle_pm_book.get("flexcube_message")
        self.reference_id = settle_pm_book.get("reference_id")
        self.msgstat = settle_pm_book.get("msgstat")
        self.txn_ref_no = settle_pm_book.get("txn_ref_no")
        self.user_ref_no = settle_pm_book.get("user_ref_no")
        self.dr_ac_no = settle_pm_book.get("dr_ac_no")
        self.cr_ac_no = settle_pm_book.get("cr_ac_no")
        self.transaction_amount = settle_pm_book.get("transaction_amount")
        self.transaction_currency = settle_pm_book.get("transaction_currency")
        self.txn_value_date = settle_pm_book.get("txn_value_date")

    __tablename__ = "settle_pm_book"

    settle_pm_book_id = db.Column(db.Integer(), primary_key=True)

    # FK to system and status
    system_id = db.Column(db.Integer(), db.ForeignKey("system.system_id"), nullable=False)
    settlement_status_id = db.Column(db.Integer(), db.ForeignKey("status.status_id"), nullable=False)

    # Business reference (unique)
    reference_id = db.Column(db.String(64), nullable=False, unique=True, index=True)

    # Audit timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime())
    sent_at = db.Column(db.DateTime())

    # SOAP request / response
    flexcube_content = db.Column(db.Text())      # request XML
    flexcube_message = db.Column(db.Text())      # response XML
    flexcube_response_status_id = db.Column(db.Integer(), db.ForeignKey("status.status_id"))
    flexcube_response_at = db.Column(db.DateTime())

    # Response metadata
    msgstat = db.Column(db.String(16))           # SUCCESS / FAILURE
    txn_ref_no = db.Column(db.String(32), index=True)
    user_ref_no = db.Column(db.String(32))

    # Convenience denormalized fields
    dr_ac_no = db.Column(db.String(32))
    cr_ac_no = db.Column(db.String(32))
    transaction_amount = db.Column(db.Numeric(20, 2))
    transaction_currency = db.Column(db.String(3))
    txn_value_date = db.Column(db.Date())