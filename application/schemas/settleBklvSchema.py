from application import ma
from application.models.settleBklv import SettleBklv


class SettleBklvSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SettleBklv
        include_fk = True
