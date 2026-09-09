from application import ma
from application.models.tokenBlocklist import TokenBlocklist


class TokenBlocklistSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TokenBlocklist
        include_fk = True
