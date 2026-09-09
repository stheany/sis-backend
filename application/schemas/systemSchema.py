from application import ma
from application.models.system import System


class SystemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = System
        include_fk = True
