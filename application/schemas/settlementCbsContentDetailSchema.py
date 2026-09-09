from application import ma
from application.models.settlementCbsContentDetail import SettlementCbsContentDetail


class SettlementCbsContentDetailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SettlementCbsContentDetail
        include_fk = True
