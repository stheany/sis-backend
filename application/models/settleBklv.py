"""
SettleBklv ORM model for the 'SETTLE_BKLV' table in SIS Oracle database.
Stores Bakong Large Value fund transfer settlement records.
"""
from application import db


class SettleBklv(db.Model):
    def __init__(self, settle_bklv: dict):
        """
        Initialize a SettleBklv by passing in a dictionary
        :param settle_bklv: A dictionary with fields matching the SettleBklv fields
        """
        self.settle_bklv_id = settle_bklv.get("settle_bklv_id")
        self.system_id = settle_bklv.get("system_id")
        self.ext_ref = settle_bklv.get("ext_ref")
        self.source_bank = settle_bklv.get("source_bank")
        self.destination_bank = settle_bklv.get("destination_bank")
        self.debit_account = settle_bklv.get("debit_account")
        self.amount = settle_bklv.get("amount")
        self.currency = settle_bklv.get("currency")
        self.iso_message = settle_bklv.get("iso_message")
        self.settlement_status_id = settle_bklv.get("settlement_status_id")
        self.bklv_request_content = settle_bklv.get("bklv_request_content")
        self.bklv_response_content = settle_bklv.get("bklv_response_content")
        self.bklv_response_status_id = settle_bklv.get("bklv_response_status_id")
        self.bklv_response_at = settle_bklv.get("bklv_response_at")
        self.bklv_reference = settle_bklv.get("bklv_reference")
        self.created_at = settle_bklv.get("created_at")
        self.updated_at = settle_bklv.get("updated_at")
        self.sent_at = settle_bklv.get("sent_at")
        self.batch_id = settle_bklv.get("batch_id")
        self.line_no = settle_bklv.get("line_no")

    __tablename__ = "settle_bklv"

    # Data Columns
    settle_bklv_id = db.Column(
        db.Integer(), db.Identity(start=1), primary_key=True)
    system_id = db.Column(
        db.Integer(),
        db.ForeignKey("system.system_id"),
        nullable=False)
    ext_ref = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
        comment="External reference for idempotency")
    source_bank = db.Column(
        db.String(100),
        nullable=False)
    destination_bank = db.Column(
        db.String(100),
        nullable=False)
    debit_account = db.Column(
        db.String(50),
        nullable=False)
    amount = db.Column(
        db.Numeric(18, 2),
        nullable=False)
    currency = db.Column(
        db.String(10),
        nullable=False)
    iso_message = db.Column(
        db.Text(),
        comment="ISO 20022 pain.001 XML message from the calling bank")
    settlement_status_id = db.Column(
        db.Integer(),
        db.ForeignKey("status.status_id"),
        nullable=False)
    bklv_request_content = db.Column(
        db.Text(),
        comment="Full SOAP request sent to BKLV")
    bklv_response_content = db.Column(
        db.Text(),
        comment="Full SOAP response received from BKLV")
    bklv_response_status_id = db.Column(
        db.Integer(),
        db.ForeignKey("status.status_id"),
        comment="BKLV response status id")
    bklv_response_at = db.Column(db.DateTime())
    bklv_reference = db.Column(
        db.String(200),
        comment="BKLV reference from response")
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())
    sent_at = db.Column(
        db.DateTime(),
        comment="Date and time sent to BKLV")
    batch_id = db.Column(
        db.Integer(),
        db.ForeignKey("settle_ncs_bklv_batch.settle_ncs_bklv_batch_id"),
        nullable=True,
        comment="Set when this row is one line of a NCS netfile batch; null for direct REST /bklv/transfer calls")
    line_no = db.Column(
        db.Integer(),
        nullable=True,
        comment="Ordinal position of this line within its batch")
