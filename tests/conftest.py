import pytest
from flask_jwt_extended import create_access_token
from sqlalchemy import select

from app import create_app
from config.settings import TestConfig
from extensions import db
from models import User

TEST_USERNAME = "testuser"
TEST_EMAIL = "testemail@test.com"
TEST_PASSWORD = "testpassword123"


@pytest.fixture()
def app():
    app = create_app(config_obj=TestConfig)

    with app.app_context():
        db.create_all()
        test_user = User(
            username=TEST_USERNAME, email=TEST_EMAIL, password=TEST_PASSWORD
        )
        db.session.add(test_user)
        db.session.commit()

    app_context = app.test_request_context()
    app_context.push()

    yield app

    app_context.pop()


@pytest.fixture()
def token(app):
    user = db.session.scalars(
        select(User).where(User.username == TEST_USERNAME)
    ).first()
    access_token = create_access_token(identity=user)
    return access_token


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def mocked_send_activation_email(mocker):
    return mocker.patch("tasks.send_activation_email.delay")
