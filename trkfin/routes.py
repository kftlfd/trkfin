from flask import flash, redirect, render_template, request, session
from flask_session import Session
from trkfin import app, db
from trkfin.forms import LoginForm
from trkfin.models import Users


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        flash(f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')

        login = Users(form.username.data, form.email.data, form.password.data)
        db.session.add(login)
        db.session.commit()

        records = Users.query.all()

        flash(records)

        return render_template('login.html', form=form) # redirect('/index')
    
    return render_template('login.html', form=form)
