from email.policy import HTTP
from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_current_user, jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy import insert, select, update

from extensions import db
from models import Message, User
from serializers import MessageSchema


message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)

NOT_FOUND = "Specified message could not be found."
ID_FIELD_REQUIRED = "Numeric ID field is required."


class MessageEndpoint(Resource):
    method_decorators = [
        jwt_required(),
    ]

    def get(self, id=None):
        user = get_current_user()
        query = select(Message).join(User).where(User.id == user.id)
        if id:
            data = db.session.scalars(query.where(Message.id == int(id))).first()
            schema = message_schema
            if not data:
                return {"errors": NOT_FOUND}, HTTPStatus.NOT_FOUND
        else:
            data = db.session.scalars(query).all()
            schema = messages_schema
        return schema.dump(data)

    def post(self):
        data = request.get_json()
        try:
            validated_data = message_schema.load(data)
        except ValidationError as err:
            return {"errors": err.messages}, HTTPStatus.BAD_REQUEST

        user = get_current_user()
        message = Message(**validated_data, user=user)
        db.session.add(message)
        db.session.commit()
        return message_schema.dump(message), HTTPStatus.CREATED

    def put(self):
        new_data = request.get_json()

        try:
            validated_data = message_schema.load(new_data)
            id = validated_data.get("id")
            if not id or type(id) is not int:
                raise ValidationError(ID_FIELD_REQUIRED)
        except ValidationError as err:
            return {"errors": err.messages}, HTTPStatus.BAD_REQUEST

        user = get_current_user()
        data = db.session.scalars(
            select(Message)
            .join(User)
            .where(User.id == user.id)
            .where(Message.id == int(id))
        ).first()

        if not data:
            message = Message(**validated_data, user=user)
            db.session.add(message)
            status = HTTPStatus.CREATED
        else:
            query = (
                update(Message).where(Message.id == int(id)).values(**validated_data)
            )
            db.session.execute(query)
            status = HTTPStatus.OK

        db.session.commit()
        return message_schema.dump(new_data), status

    def delete(self, id=0):
        user = get_current_user()
        data = db.session.scalars(
            select(Message)
            .join(User)
            .where(User.id == user.id)
            .where(Message.id == int(id))
        ).first()
        if not data:
            return {"errors": NOT_FOUND}, HTTPStatus.NOT_FOUND
        db.session.delete(data)
        db.session.commit()
        return {}, HTTPStatus.NO_CONTENT
