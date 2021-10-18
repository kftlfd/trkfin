from flask import flash, redirect, render_template, request, session
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return render_template('login.html', form=form) # redirect('/index')
    
    return render_template('login.html', form=form)