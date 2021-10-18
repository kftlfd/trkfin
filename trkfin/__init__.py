from flask import Flask

app = Flask(__name__)

from trkfin import routes
