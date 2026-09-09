from application import ma
from application.models.iroha import Iroha


class IrohaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Iroha
        include_fk = True
