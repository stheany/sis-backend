from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema

from application.models.usersLoginSis import UsersLoginSis


class UsersLoginSisSchema(SQLAlchemySchema):
    class Meta:
        model = UsersLoginSis
        exclude = ()

    users_login_sis_id = fields.Integer(dump_only=True)
    username = fields.String()
    password = fields.String(load_only=True)
    first_name = fields.String()
    last_name = fields.String()
    full_name = fields.String()
    email = fields.String()
    description = fields.String()
    status = fields.Integer()
    created_at = fields.DateTime()
    created_by = fields.Integer()
    updated_at = fields.DateTime()
    updated_by = fields.Integer()
    blocked_at = fields.DateTime()
    blocked_by = fields.Integer()
