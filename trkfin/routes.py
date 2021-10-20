from flask import flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from trkfin import app, db
from trkfin.forms import LoginForm, RegisterForm
from trkfin.models import Users


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        
        # flash form data -- TEMP
        flash("user: {}; email: {}; passw: {}; confirm: {}".format(
            form.username.data, form.email.data, form.password.data, form.confirm.data
        ))

        # remember registration info
        user = form.username.data
        email = form.email.data
        passw_hash = generate_password_hash(form.password.data)
        flash(generate_password_hash(form.password.data))

        # insert into db
        new_register = Users(user, email, passw_hash)
        db.session.add(new_register)
        db.session.commit()

        # success
        flash('registered')
        return redirect('/register')

    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        # flash form data
        flash("form:: user: {}; email: {}; passw: {}; remember: {}".format(
            form.username.data, form.email.data, form.password.data, form.remember_me.data
        ))

        # check if user is in db
        user = Users.query.filter_by(username=form.username.data).first()        
        
        if not user:
            flash('no user')
            return redirect('/login')
        
        if not check_password_hash(form.password.data, user.password_hash):
            flash('wrong password')
            flash("user hash: " + user.password_hash)
            return redirect('/login')

        # success
        flash('success: id', user[0].id)
        return redirect('/login')
    
    return render_template('login.html', form=form)
