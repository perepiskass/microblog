import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.flaskenv'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'appFlask.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [os.environ.get('MAIL_USERNAME')]
    MAIL_FROM = os.environ.get('MAIL_USERNAME')

    POSTS_PER_PAGE = 3  #кол-во элементов (сообщений пользователей) на странице
    LANGUAGES = ['en', 'ru']

    API_NLP_KEY = os.environ.get('API_NLP_KEY')
    API_NLP_URL = os.environ.get('API_NLP_URL')
    API_NLP_HOST = os.environ.get('API_NLP_HOST')

    API_YANDEX_KEY = os.environ.get('API_YANDEX_KEY')
    API_YANDEX_CATALOG_ID = os.environ.get('API_YANDEX_CATALOG_ID')
    API_YANDEX_URL = os.environ.get('API_YANDEX_URL')