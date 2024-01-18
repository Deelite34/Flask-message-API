from flask import Blueprint

base_bp = Blueprint("base", __name__, url_prefix="")
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
