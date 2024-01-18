import os
from datetime import timedelta


class BaseConfig:
    CELERY = {
        "broker_url": "redis://redis:6379/0",
        "result_backend": "redis://redis:6379/0",
        "task_ignore_result": True,
    }

    DB_NAMING_CONVENTION = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=14)

    EMAIL_API_URL = "https://api.brevo.com/v3/smtp/email"
    SKIP_EMAIL_ACTIVATION = False


class ProdConfig(BaseConfig):
    SECRET_KEY = os.getenv("secret_key")
    JWT_SECRET_KEY = os.getenv("jwt_key")
    BREVO_API_KEY = os.getenv("brevo_api_key")

    PG_USER = os.getenv("postgres_user")
    PG_PASSWORD = os.getenv("postgres_password")
    PG_DB = os.getenv("postgres_db")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@db:5432/{PG_DB}"
    )


class DevConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = False

    BREVO_API_KEY = os.getenv("brevo_api_key")
    PG_USER = "postgres"
    PG_PASSWORD = "postgres"
    PG_DB = "postgres"
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@db:5432/{PG_DB}"
    )

    SECRET_KEY = "very12312secret!key"
    JWT_SECRET_KEY = "super123!secret!6456456key"

    SKIP_EMAIL_ACTIVATION = True


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = False
    BREVO_API_KEY = "mock_sending_mails"

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    BREVO_API_KEY = os.getenv("brevo_api_key")
    SECRET_KEY = "very12312secret!key"
    JWT_SECRET_KEY = "super123!secret!6456456key"
