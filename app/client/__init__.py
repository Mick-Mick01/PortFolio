__all__ = ["myMongo", "routes"]

from flask import Blueprint

client_bp = Blueprint("client", __name__)

from . import routes