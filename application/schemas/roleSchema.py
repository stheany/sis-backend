from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema

from application.models.role import Role


class RoleSchema(SQLAlchemySchema):
    class Meta:
        model = Role
        exclude = ()

    role_id = fields.Integer(dump_only=True)
    name = fields.String()
    description = fields.String()
    created_at = fields.DateTime()
    created_by = fields.Integer()
    updated_at = fields.DateTime()
    updated_by = fields.Integer()
