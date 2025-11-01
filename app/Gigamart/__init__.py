from flask import Blueprint

Gigamart_bp = Blueprint("Gigamart", __name__)

from . import routes