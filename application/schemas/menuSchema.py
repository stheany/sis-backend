from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema

from application.models.menu import Menu


class MenuSchema(SQLAlchemySchema):
    class Meta:
        model = Menu
        exclude = ()

    menu_id = fields.Integer()
    name = fields.String()
    description = fields.String()
    status = fields.Integer()
    icon = fields.String()
    url = fields.String()
    created_at = fields.DateTime()
    created_by = fields.Integer()
    updated_at = fields.DateTime()
    updated_by = fields.Integer()
