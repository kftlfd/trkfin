from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////trkfin.db'
engine = create_engine('sqlite:///trkfin.db')
db = engine.connect()

@app.route("/")
@app.route("/index")
def index():
    res = db.execute("SELECT * FROM users").all()
    return render_template("index.html", res=res)

@app.route("/register")
def register():
    return render_template("register.html")