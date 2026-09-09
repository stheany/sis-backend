from application import ma
from application.models.sisLoginSystem import SisLoginSystem


class SisLoginSystemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SisLoginSystem
        include_fk = True
