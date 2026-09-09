from marshmallow import fields

from application import ma
from application.models.systemLoginSis import SystemLoginSis


class SystemLoginSisSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True)

    class Meta:
        model = SystemLoginSis
        include_fk = True
