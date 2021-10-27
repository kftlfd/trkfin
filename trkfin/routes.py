from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from trkfin import app, db
from trkfin.models import Users
from trkfin.forms import LoginForm, RegistrationForm


@app.route("/")
@app.route("/index")
def index():

    if current_user.is_authenticated:
        msg = "logged-in!"
        return render_template("index.html", msg=msg)

    if not current_user.is_authenticated:
        return redirect(url_for('welcome'))

    return render_template("index.html")


@app.route("/welcome")
def welcome():
    return render_template("welcome.html")


@app.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    # if received a valid form
    if form.validate_on_submit():

        # remember registration info
        new_user = Users(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)

        # insert write new user to db        
        db.session.add(new_user)
        db.session.commit()

        # success
        flash('Successfully registered')
        return redirect(url_for('login'))

    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    # if received a valid form
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
            next_page = url_for('index')
        return redirect(next_page)
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/u/<username>')
@login_required
def account(username):
    
    if username is not current_user.username:
        return redirect('/u/' + current_user.username)

    user = Users.query.filter_by(username=username).first_or_404()

    return render_template('account.html')
