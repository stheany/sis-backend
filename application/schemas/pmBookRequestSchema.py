"""
Request schema for PM Book create API (JSON → validated DTO).
Enforces safe Flexcube-ish limits so we fail fast before building SOAP.
"""
from marshmallow import Schema, fields, validate

# validators (picked to be “safe defaults” across FCUBS installs)
LEN  = lambda n: validate.Length(max=n)
ACCT = validate.Regexp(r"^[0-9]{1,32}$")   # core accounts often 16–32 digits
CCY  = validate.Regexp(r"^[A-Z]{3}$")      # ISO-4217

class PMBookCreateRequest(Schema):
    # Idempotency / correlation
    reference_id     = fields.String(required=True, validate=LEN(64))

    # Header-like items (some may be defaulted from FLEXCUBE table)
    msgid            = fields.String(required=True, validate=LEN(50))
    branch           = fields.String(required=True, validate=validate.Regexp(r"^[0-9]{3}$"))
    entity           = fields.String(required=True, validate=LEN(12))
    source_code      = fields.String(required=True, validate=LEN(10))   # e.g., IBUS/IBKHR
    network_code     = fields.String(required=True, validate=LEN(30))   # e.g., BOOK_TRANSFER
    host_code        = fields.String(required=True, validate=LEN(16))   # bank specific

    # Accounts & amount
    dr_ac_no         = fields.String(required=True, validate=ACCT)
    cr_ac_no         = fields.String(required=True, validate=ACCT)
    cr_ac_ccy        = fields.String(required=True, validate=CCY)
    cr_amt           = fields.Decimal(required=True, as_string=True, places=2)  # 18,2 safe

    # Dates & narrative
    txn_value_date   = fields.Date(required=True)
    instruction_date = fields.Date(required=True)
    remarks          = fields.String(allow_none=True, validate=LEN(255))

    # Optional charge component
    charge_component = fields.String(allow_none=True, validate=LEN(30))
    charge_amount    = fields.Decimal(allow_none=True, as_string=True, places=2)