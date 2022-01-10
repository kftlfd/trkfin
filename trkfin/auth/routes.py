from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from trkfin import db
from trkfin.auth import bp
from trkfin.auth.forms import RegistrationForm, LoginForm
from trkfin.models import Users, Wallets, History, Reports


@bp.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # process registration form
    form = RegistrationForm()
    if form.validate_on_submit():

        # record user to db
        new_user = Users(form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        # add history entry
        record = History()
        record.user_id = new_user.id
        record.action = 'Created account'
        record.ts_local = form.timestamp.data
        db.session.add(record)
        db.session.commit()

        # prevent auto-login
        # logout_user()
        flash('Successfully Registered')
        return redirect(url_for('auth.login'))

    return render_template("auth/register.html", form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # process login form
    form = LoginForm()
    if form.validate_on_submit():

        # check if user is in db
        user = Users.query.filter_by(username=form.username.data).first()        
        if user is None:
            flash('username not found')
            return redirect(url_for('login'))
        
        # check password
        if not user.check_password(form.password.data):
            flash('wrong password')
            return redirect((url_for('login')))

        # log user in
        login_user(user, remember=form.remember_me.data)
        flash('Logged in')

        # redirect to next page
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))
