from flask import Blueprint

hosting_bp = Blueprint("hosting", __name__)

from . import routes