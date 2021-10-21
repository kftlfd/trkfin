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
        return render_template("index.html")

    return render_template("index.html")


@app.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        
        # flash form data -- TEMP
        flash("user: {}; email: {}; passw: {}; confirm: {}".format(
            form.username.data, form.email.data, form.password.data, form.confirm.data
        ))

        # remember registration info
        new_user = Users(form.username.data)
        new_user.email = form.email.data
        new_user.set_password(form.password.data)

        # insert into db        
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

    if form.validate_on_submit():

        # flash form data
        flash("form:: user: {}; email: {}; passw: {}; remember: {}".format(
            form.username.data, form.email.data, form.password.data, form.remember_me.data
        ))

        # check if user is in db
        user = Users.query.filter_by(username=form.username.data).first()        
        
        if user is None:
            flash('username not found')
            return redirect(url_for('login'))
        
        if not user.check_password(form.password.data):
            flash('wrong password')
            return redirect((url_for('login')))

        # success        
        login_user(user, remember=form.remember_me.data)
        flash('logged in: id ' + str(user.id))
        flash(f"{current_user}")

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


@app.route('/account')
@login_required
def account():
    return render_template('account.html')