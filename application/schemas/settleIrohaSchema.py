from application import ma
from application.models.settleIroha import SettleIroha


class SettleIrohaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SettleIroha
        include_fk = True
