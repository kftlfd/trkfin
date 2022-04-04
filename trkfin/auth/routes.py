from datetime import datetime
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
        return redirect(url_for('home'))

    # process registration form
    form = RegistrationForm()
    if form.validate_on_submit():

        # record user to db
        new_user = Users(
            username = form.username.data.strip(),
            created = datetime.utcnow().timestamp(), # float
            tz_offset = int(form.tz_offset.data), # int
            report_frequency = 'month'
            )
        new_user.next_report = new_user.get_next_report_ts()       
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        # add history entry
        record = History(
            user_id = new_user.id,
            ts_utc = new_user.created,
            local_time = datetime.fromtimestamp(new_user.created + new_user.tz_offset).__str__()[:19],
            action = 'Created account'
            )
        db.session.add(record)
        db.session.commit()

        # auto-login
        login_user(new_user)
        flash('Successfully Registered!')
        return redirect(url_for('home'))

    return render_template("auth/register.html", form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    # process login form
    form = LoginForm()
    if form.validate_on_submit():

        # check if user is in db
        user = Users.query.filter_by(username=form.username.data.strip()).first()        
        if user is None:
            flash('Username not found')
            return redirect(url_for('auth.login'))
        
        # check password
        if not user.check_password(form.password.data):
            flash('Wrong password')
            return redirect((url_for('auth.login')))

        # log user in
        login_user(user, remember=form.remember_me.data)

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
    return redirect(url_for('auth.login'))
