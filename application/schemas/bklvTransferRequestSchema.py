"""
Validating incoming BKLV fund transfer requests.
Validates required fields, types, and basic constraints.
"""
from marshmallow import Schema, fields, validate


class BklvTransferRequestSchema(Schema):
    ext_ref = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={"description": "External reference ID for idempotency"}
    )
    source_bank = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={"description": "Source bank system_name (must be active in SYSTEM table)"}
    )
    destination_bank = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={"description": "Destination bank system_name (must be active in SYSTEM table)"}
    )
    debit_account = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
        metadata={"description": "Debit account number"}
    )
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0.01),
        metadata={"description": "Transfer amount (must be > 0)"}
    )
    currency = fields.String(
        required=True,
        validate=validate.OneOf(["USD", "KHR"]),
        metadata={"description": "Currency code"}
    )
    iso_message = fields.String(
        required=True,
        validate=validate.Length(min=1),
        metadata={"description": "ISO 20022 pain.001 XML message"}
    )
    execution_date = fields.String(
        required=False,
        metadata={"description": "Check ReqdExctnDt inside iso_message"}
    )
    debtor_name = fields.String(
        required=False,
        metadata={"description": "Check Dbtr/Nm inside iso_message"}
    )
    creditor_name = fields.String(
        required=False,
        metadata={"description": "Check Cdtr/Nm inside iso_message"}
    )
    receiver_account_id = fields.String(
        required=False,
        metadata={"description": "Check CdtrAcct/Id/Othr/Id inside iso_message"}
    )
