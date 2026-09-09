from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema

from application.models.userRole import UserRole


class UserRoleSchema(SQLAlchemySchema):
    class Meta:
        model = UserRole
        exclude = ()

    user_role_id = fields.Integer(dump_only=True)
    role_id = fields.Integer()
    users_login_sis_id = fields.Integer()
    created_at = fields.DateTime()
    created_by = fields.Integer()
    updated_at = fields.DateTime()
    updated_by = fields.Integer()
    blocked_at = fields.DateTime()
    blocked_by = fields.Integer()
