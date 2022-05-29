from flask import Blueprint

bp = Blueprint('main', __name__)

from appPackage.main import routes