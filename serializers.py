from flask_marshmallow import Schema
from marshmallow import fields
from marshmallow_sqlalchemy import auto_field

from extensions import ma
from models import Message, User


class UserRegisterSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    username = auto_field()
    password = auto_field(column_name="_password", load_only=True)
    email = auto_field()


class UserLoginSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    username = auto_field()
    password = auto_field(column_name="_password", load_only=True)


class TokenSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


class MessageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Message
