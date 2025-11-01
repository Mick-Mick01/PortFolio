from flask import Blueprint

portFolio_bp = Blueprint("portFolio", __name__)

from . import routes