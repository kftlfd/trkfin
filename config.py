import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    # for cryptography (flast-wtf, wtforms mainly?)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-coded-value'
    
    # use Heroku's Postgres db or local SQLite db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'sqlite:///' + os.path.join(basedir, 'trkfin.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # logging on Heroku
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    # reset database
    RESET_DB_PASSWORD = os.environ.get('RESET_DB_PASSWORD') or 'reset'
