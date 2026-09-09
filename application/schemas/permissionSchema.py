from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema

from application.models.permission import Permission


class PermissionSchema(SQLAlchemySchema):
    class Meta:
        model = Permission
        exclude = ()

    permission_id = fields.Integer(dump_only=True)
    description = fields.String()
    role_id = fields.Integer()
    action_id = fields.Integer()
    menu_id = fields.Integer()
    created_at = fields.DateTime()
    created_by = fields.Integer()
    updated_at = fields.DateTime()
    updated_by = fields.Integer()
