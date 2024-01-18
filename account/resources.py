import logging
from http import HTTPStatus

from flask import current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt_identity,
    jwt_required,
)
from flask_restful import Resource, abort
from marshmallow import ValidationError, fields
from sqlalchemy import select

from extensions import db
from models import User
from serializers import TokenSchema, UserLoginSchema, UserRegisterSchema, UserSchema
from tasks import send_activation_email
from utils import api_exception, make_simple_activation_template

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()
user_schema = UserSchema()
token_schema = TokenSchema()

USER_ALREADY_EXISTS = "This email or username is already in use, try again."
FAILED_LOGIN = "Invalid credentials, try again."
ACCOUNT_ACTIVATED = "Account has been activated"


class AccountActivateEndpoint(Resource):
    def get(self, code):
        user = db.session.scalars(
            select(User).where(User.activation_code == code)
        ).first()
 
        if not user:
            abort(404)
        
        user.activated = True
        db.session.commit()
        return {"status": ACCOUNT_ACTIVATED}, 200


class AccountRegisterEndpoint(Resource):
    def post(self):
        data = request.get_json()
        try:
            validated_data = register_schema.load(data)
        except ValidationError as err:
            return api_exception(err.messages, HTTPStatus.BAD_REQUEST)

        user = db.session.scalars(
            select(User).where(User.username == validated_data.get("username"))
        ).first()
        if user:
            return {"errors": USER_ALREADY_EXISTS}, HTTPStatus.BAD_REQUEST

        user = User(**validated_data)
        user.password = validated_data.get("_password")
        db.session.add(user)
        db.session.commit()

        user = db.session.scalars(
            select(User).where(User.username == validated_data.get("username"))
        ).first()

        if current_app.config["SKIP_EMAIL_ACTIVATION"]:
            logging.info(
                "SKIP_EMAIL_ACTIVATION setting is enabled, user will be created activated."
            )
            user.activated = True
            db.session.commit()
        else:
            template = make_simple_activation_template(user.activation_code)
            send_activation_email.delay(user.email, template)
        return register_schema.dump(user), HTTPStatus.CREATED


class AccountLoginEndpoint(Resource):
    def post(self):
        data = request.get_json()
        try:
            validated_data = login_schema.load(data)
        except ValidationError as err:
            return api_exception(err.messages, HTTPStatus.BAD_REQUEST)

        user = db.session.scalars(
            select(User).where(User.username == validated_data.get("username"))
        ).first()

        if not user:
            return api_exception(FAILED_LOGIN, HTTPStatus.UNAUTHORIZED)
        if not user.activated:
            logging.info(f"Inactive user attempted to log in: {user.username}")
            return api_exception(FAILED_LOGIN, HTTPStatus.UNAUTHORIZED)

        if user.verify_password(validated_data.get("_password")) is True:
            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)
            return jsonify(access_token=access_token, refresh_token=refresh_token)
        return api_exception(FAILED_LOGIN, HTTPStatus.UNAUTHORIZED)


class AccountLoginRefreshEndpoint(Resource):
    @jwt_required(refresh=True)
    def post(self):
        user = db.session.scalars(
            select(User).where(User.id == get_jwt_identity())
        ).first()
        access_token = create_access_token(identity=user)
        return jsonify(access_token=access_token)
