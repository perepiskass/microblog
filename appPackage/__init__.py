import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()

def create_app(config_class = Config):
    appFlask = Flask(__name__)
    appFlask.config.from_object(config_class)

    db.init_app(appFlask)
    migrate.init_app(appFlask, db)
    login.init_app(appFlask)
    mail.init_app(appFlask)
    bootstrap.init_app(appFlask)
    moment.init_app(appFlask)
    babel.init_app(appFlask)

    from appPackage.errors import bp as errors_bp
    appFlask.register_blueprint(errors_bp)

    from appPackage.auth import bp as auth_bp
    appFlask.register_blueprint(auth_bp, url_prefix='/auth')

    from appPackage.main import bp as main_bp
    appFlask.register_blueprint(main_bp)

    if not appFlask.debug:
        if appFlask.config['MAIL_SERVER']:
            auth = None
            if appFlask.config['MAIL_USERNAME'] or appFlask.config['MAIL_PASSWORD']:
                auth = (appFlask.config['MAIL_USERNAME'], appFlask.config['MAIL_PASSWORD'])
            secure = None
            if appFlask.config['MAIL_USE_TLS']:
                secure = ()
            mailruhost = (appFlask.config['MAIL_SERVER'], appFlask.config['MAIL_PORT'])
            print(mailruhost)
            mail_handler = SMTPHandler(
                mailhost=mailruhost,
                fromaddr=appFlask.config['MAIL_FROM'],
                toaddrs=appFlask.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure, timeout=1.0)
            print(mail_handler)
            mail_handler.setLevel(logging.ERROR)
            appFlask.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        appFlask.logger.addHandler(file_handler)

        appFlask.logger.setLevel(logging.INFO)
        appFlask.logger.info('Microblog startup')

    return appFlask

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

from appPackage import models
