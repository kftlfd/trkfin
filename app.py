from flask import Flask, redirect, render_template, request, session
from flask_session import Session

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")
