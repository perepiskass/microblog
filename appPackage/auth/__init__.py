from flask import Blueprint

bp = Blueprint('auth', __name__)

from appPackage.auth import routes