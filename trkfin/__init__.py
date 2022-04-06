import logging
import os
import time
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# create app instance
app = Flask(__name__)

# load config
from config import Config
app.config.from_object(Config)

# create SQLAlchemy instance
db = SQLAlchemy(app)

# session and login
login = LoginManager(app)
login.login_view = 'auth.login'

# setup logging
if app.config['LOG_TO_STDOUT']: # Heroku env variable
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
else: # local logs
    if not os.path.exists('logs'): os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/trkfin.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# blueprints
from trkfin.auth import bp as auth_bp
app.register_blueprint(auth_bp)

# import app modules
from trkfin import errors, models, routes

# create database if not any
db.create_all()

# jinja filters
def num(value):
    return f'{value:,.2f}'
def tostr(value):
    return str(value)
app.jinja_env.filters['num'] = num
app.jinja_env.filters['str'] = tostr

# launched successfully
app.logger.info('trkfin launched')
