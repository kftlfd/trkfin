from flask import Blueprint

bp = Blueprint('auth', __name__)

from trkfin.auth import routes
