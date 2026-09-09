from application import ma
from application.models.environment import Environment


class EnvironmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Environment
        include_fk = True
