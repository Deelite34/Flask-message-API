import logging

from celery import Celery, Task
from flask import Flask, redirect, url_for

from account.resources import (
    AccountActivateEndpoint,
    AccountLoginEndpoint,
    AccountLoginRefreshEndpoint,
    AccountRegisterEndpoint,
)
from blueprints import api_bp, base_bp
from config.settings import BaseConfig, DevConfig
from extensions import admin, api, db, jwt, ma, migrate
from manage import run_pytest
from messages.resources import MessageEndpoint


logging.basicConfig(level=logging.DEBUG)


celery = Celery(__name__, broker=BaseConfig.CELERY["broker_url"])


def init_celery(app: Flask, celery: Celery) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    if not celery:
        celery = Celery(app.name, task_cls=FlaskTask)
    celery.config_from_object(app.config["CELERY"])
    celery.set_default()
    app.extensions["celery"] = celery
    return celery


@base_bp.route("/")
def redirect_to_api():
    return redirect(url_for("api.messageendpoint"), code=302)


def init_extensions(app):
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    admin.init_app(app)
    jwt.init_app(app)
    init_celery(app, celery)


def add_resources():
    api.add_resource(MessageEndpoint, "/message/", "/message/<int:id>/")
    api.add_resource(AccountRegisterEndpoint, "/account/")
    api.add_resource(AccountActivateEndpoint, "/account/activate/<string:code>")
    api.add_resource(AccountLoginEndpoint, "/account/login/")
    api.add_resource(AccountLoginRefreshEndpoint, "/account/login/refresh/")


def register_blueprints(app: Flask):
    with app.app_context():
        app.register_blueprint(base_bp)
        app.register_blueprint(api_bp)


def create_app(config_obj=DevConfig):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_obj)

    flask_app.cli.add_command(run_pytest)

    init_extensions(flask_app)
    register_blueprints(flask_app)
    add_resources()

    from extensions import configuration

    configuration.api_key["api-key"] = flask_app.config["BREVO_API_KEY"]

    return flask_app
