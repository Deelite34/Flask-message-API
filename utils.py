import uuid

from flask import request, url_for
from sqlalchemy import select

from extensions import db, jwt


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    from models import User

    identity = jwt_data["sub"]
    return db.session.scalars(select(User).where(User.id == identity)).first()


def make_uuid():
    return str(uuid.uuid4())


def make_simple_activation_template(code):
    """Used in account activation email"""
    base = request.host_url[:-1]
    url = f"{base}{url_for('api.accountactivateendpoint', code=code)}"
    content = f"Activate your account here: {url}"
    template = f"<html><head></head><body>{content}</body></html>"
    return template


def api_exception(message, status):
    return {"errors": message}, status
