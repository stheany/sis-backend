"""
Response schema we return to clients after we accept/process PM Book requests.
Keeps the external shape stable even if internals change.
"""
from marshmallow import Schema, fields

class PMBookCreateResponse(Schema):
    id                    = fields.Integer()        # settle_pm_book_id
    settlement_status     = fields.String()         # PENDING/SUCCESS/FAIL/ERROR
    created_at            = fields.DateTime()

    # Selected Flexcube response fields (if/when available)
    msgstat               = fields.String(allow_none=True)
    txn_ref_no            = fields.String(allow_none=True)
    user_ref_no           = fields.String(allow_none=True)
    flexcube_message      = fields.String(allow_none=True)

    # Convenience echo (optional)
    dr_ac_no              = fields.String(allow_none=True)
    cr_ac_no              = fields.String(allow_none=True)
    transaction_amount    = fields.Decimal(allow_none=True, as_string=True, places=2)
    transaction_currency  = fields.String(allow_none=True)
    txn_value_date        = fields.Date(allow_none=True)