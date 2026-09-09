from application import ma
from application.models.settlementIrohaContentDetail import SettlementIrohaContentDetail


class SettlementIrohaContentDetailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SettlementIrohaContentDetail
        include_fk = True
