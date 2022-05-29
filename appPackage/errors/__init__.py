from flask import Blueprint

bp = Blueprint('errors', __name__)

from appPackage.errors import handlers