from application import ma
from application.models.action import Action


class ActionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Action
        include_fk = True
