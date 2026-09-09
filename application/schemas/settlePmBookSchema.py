"""
Marshmallow schema for SettlePmBook rows (master table).
This represents how we serialize DB objects out to API clients.
"""
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema

from application.models.settlePmBook import SettlePmBook


class SettlePmBookSchema(SQLAlchemySchema):
    class Meta:
        model = SettlePmBook
        include_fk = True

    # PK / FKs
    settle_pm_book_id = fields.Integer(dump_only=True)
    system_id = fields.Integer()
    settlement_status_id = fields.Integer()

    # Request/response artifacts & audit
    reference_id = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime(allow_none=True)
    sent_at = fields.DateTime(allow_none=True)

    # Flexcube payload & response
    flexcube_content = fields.String(allow_none=True)
    flexcube_message = fields.String(allow_none=True)
    flexcube_response_status_id = fields.Integer(allow_none=True)
    flexcube_response_at = fields.DateTime(allow_none=True)

    # Selected response fields (for quick access)
    msgstat = fields.String(allow_none=True)
    txn_ref_no = fields.String(allow_none=True)
    user_ref_no = fields.String(allow_none=True)

    # Convenience fields
    dr_ac_no = fields.String(allow_none=True)
    cr_ac_no = fields.String(allow_none=True)
    transaction_amount = fields.Decimal(allow_none=True, as_string=True, places=2)
    transaction_currency = fields.String(allow_none=True)
    txn_value_date = fields.Date(allow_none=True)