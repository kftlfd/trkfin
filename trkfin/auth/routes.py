from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from trkfin import db
from trkfin.auth import bp
from trkfin.auth.forms import RegistrationForm, LoginForm
from trkfin.models import Users, Wallets, History


@bp.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # process registration form
    form = RegistrationForm()
    if form.validate_on_submit():

        # record user to db
        new_user = Users(username=form.username.data, email=form.email.data, stats={})
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        # history entry        
        user = Users.query.filter_by(username=new_user.username).first()
        record = History()
        record.user_id = user.id
        record.action = 'Created account'
        db.session.add(record)
        db.session.commit()

        # success; log user in / redirect to login page
        flash('Successfully Registered')       
        # login_user(user, remember=False)
        # return redirect(url_for('home'))
        return redirect(url_for('login'))

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
