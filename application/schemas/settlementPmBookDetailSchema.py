"""
Marshmallow schema for SettlementPmBookDetail rows (detail table).
Auto schema with FKs included, aligned with project style.
"""
from application import ma
from application.models.settlementPmBookDetail import SettlementPmBookDetail


class SettlementPmBookDetailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SettlementPmBookDetail
        include_fk = True