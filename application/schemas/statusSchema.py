from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema

from application.models.status import Status


class StatusSchema(SQLAlchemySchema):
    class Meta:
        model = Status
        exclude = ()

    id = fields.Integer(dump_only=True)
    status = fields.String()
    description = fields.String()
    settle = fields.Nested('SettleSchema', many=False, load=True)
