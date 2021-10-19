import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-coded-value'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:////trkfin.db'