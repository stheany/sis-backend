"""
SettlementPmBookDetail ORM model for the 'SETTLEMENT_PM_BOOK_DETAIL' table in SIS Oracle database.
"""
from application import db


class SettlementPmBookDetail(db.Model):
    def __init__(self, detail: dict):
        self.settlement_pm_book_detail_id = detail.get("settlement_pm_book_detail_id")
        self.settle_pm_book_id = detail.get("settle_pm_book_id")
        self.dr_ac_no = detail.get("dr_ac_no")
        self.cr_ac_no = detail.get("cr_ac_no")
        self.currency_code = detail.get("currency_code")
        self.amount = detail.get("amount")
        self.txn_value_date = detail.get("txn_value_date")
        self.instruction_date = detail.get("instruction_date")
        self.source_code = detail.get("source_code")
        self.network_code = detail.get("network_code")
        self.txn_branch = detail.get("txn_branch")
        self.host_code = detail.get("host_code")
        self.remarks = detail.get("remarks")
        self.charge_component = detail.get("charge_component")
        self.charge_amount = detail.get("charge_amount")
        self.flexcube_id = detail.get("flexcube_id")

    __tablename__ = "settlement_pm_book_detail"

    settlement_pm_book_detail_id = db.Column(db.Integer(), primary_key=True)

    # FK to header
    settle_pm_book_id = db.Column(
        db.Integer(),
        db.ForeignKey("settle_pm_book.settle_pm_book_id"),
        nullable=False,
        index=True
    )

    # Core transaction fields
    dr_ac_no = db.Column(db.String(32), nullable=False)
    cr_ac_no = db.Column(db.String(32), nullable=False)
    currency_code = db.Column(db.String(3), nullable=False)
    amount = db.Column(db.Numeric(20, 2), nullable=False)

    # Dates
    txn_value_date = db.Column(db.Date(), nullable=False)
    instruction_date = db.Column(db.Date(), nullable=False)

    # Codes
    source_code = db.Column(db.String(16), nullable=False)             # IBUS / IBKH
    network_code = db.Column(db.String(32), nullable=False)            # BOOK_TRANSFER
    txn_branch = db.Column(db.String(8), nullable=False)               # "001"
    host_code = db.Column(db.String(16), nullable=False)               # NBC

    # Optional fields
    remarks = db.Column(db.String(255))
    charge_component = db.Column(db.String(32))                        # IBKHROCHG / IBUSDOCHG   
    charge_amount = db.Column(db.Numeric(20, 2))

    # Link to Flexcube config
    flexcube_id = db.Column(db.Integer(), db.ForeignKey("flexcube.flexcube_id"))