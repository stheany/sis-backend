from marshmallow import fields

from application import ma
from application.models.flexcube import Flexcube


class FlexcubeSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True)

    class Meta:
        model = Flexcube
        include_fk = True
