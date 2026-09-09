from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema

from application.models.settleCbs import SettleCbs


class SettleCbsSchema(SQLAlchemySchema):
    class Meta:
        model = SettleCbs
        exclude = ()

    settle_cbs_id = fields.Integer(dump_only=True)
    system_id = fields.Integer(dump_only=True)
    settlement_cbs_content = fields.String()
    settlement_status_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    sent_at = fields.DateTime()
    flexcube_content = fields.String()
    flexcube_response_status_id = fields.Integer()
    flexcube_response_at = fields.DateTime()
    flexcube_message = fields.String()
