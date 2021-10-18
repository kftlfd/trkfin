from flask import redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from trkfin import app
from trkfin.forms import LoginForm

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////trkfin.db'
engine = create_engine('sqlite:///trkfin.db')
db = engine.connect()

@app.route("/")
@app.route("/index")
def index():
    # res = db.execute("SELECT * FROM users").all()
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)