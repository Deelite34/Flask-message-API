import sib_api_v3_sdk
from flask_admin import Admin
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from blueprints import api_bp
from config.settings import BaseConfig

# https://stackoverflow.com/questions/62640576/flask-migrate-valueerror-constraint-must-have-a-name
metadata = MetaData(naming_convention=BaseConfig.DB_NAMING_CONVENTION)
db = SQLAlchemy(metadata=metadata)
api = Api(api_bp)
migrate = Migrate()
ma = Marshmallow()
admin = Admin(name="weather_app", template_mode="bootstrap3")
jwt = JWTManager()


configuration = sib_api_v3_sdk.Configuration()

brevo_api = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)
