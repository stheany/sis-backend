"""
SettleNcsBklvBatch ORM model for the 'SETTLE_NCS_BKLV_BATCH' table in SIS Oracle database.
Stores the netfile header for a NCS upload_File_GI_FLATFILE submission; each line
inside that netfile becomes its own SettleBklv row (see application/models/settleBklv.py),
linked back here via SettleBklv.batch_id.
"""
from application import db


class SettleNcsBklvBatch(db.Model):
    def __init__(self, settle_ncs_bklv_batch: dict):
        """
        Initialize a SettleNcsBklvBatch by passing in a dictionary
        :param settle_ncs_bklv_batch: A dictionary with fields matching the SettleNcsBklvBatch fields
        """
        self.settle_ncs_bklv_batch_id = settle_ncs_bklv_batch.get("settle_ncs_bklv_batch_id")
        self.system_id = settle_ncs_bklv_batch.get("system_id")
        self.file_name = settle_ncs_bklv_batch.get("file_name")
        self.currency_code = settle_ncs_bklv_batch.get("currency_code")
        self.batch_status_id = settle_ncs_bklv_batch.get("batch_status_id")
        self.submitted_content = settle_ncs_bklv_batch.get("submitted_content")
        self.created_at = settle_ncs_bklv_batch.get("created_at")
        self.updated_at = settle_ncs_bklv_batch.get("updated_at")

    __tablename__ = "settle_ncs_bklv_batch"

    # Data Columns
    settle_ncs_bklv_batch_id = db.Column(
        db.Integer(), db.Identity(start=1), primary_key=True)
    system_id = db.Column(
        db.Integer(),
        db.ForeignKey("system.system_id"),
        nullable=False)
    file_name = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
        comment="Netfile name (pFileName)")
    currency_code = db.Column(db.String(10))
    batch_status_id = db.Column(
        db.Integer(),
        db.ForeignKey("status.status_id"),
        nullable=False,
        comment="Aggregate status rolled up from child SettleBklv lines")
    submitted_content = db.Column(
        db.Text(),
        comment="Raw pContent as received from NCS, for audit")
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())
