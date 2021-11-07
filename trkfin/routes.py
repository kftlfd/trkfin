from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from trkfin import app, db
from trkfin.models import Users, Wallets
from trkfin.forms import LoginForm, RegistrationForm, FormSpending, FormIncome, FormTransfer, AddWallet


@app.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('welcome'))
    else:
        return redirect(url_for('home'))


@app.route("/home", methods=['GET', 'POST'])
def home():    

    if not current_user.is_authenticated:
        return redirect(url_for('welcome'))

    # prepare form objects
    f_sp = FormSpending()
    f_inc = FormIncome()
    f_tr = FormTransfer()
    forms = {"sp": f_sp, "inc": f_inc, "tr": f_tr}

    # load wallets
    srcs = []
    for w in Wallets.query.filter_by(user_id=current_user.id).all():
        srcs.append(w.name)
    f_sp.sp_source.choices = srcs
    f_inc.inc_destination.choices = srcs
    f_tr.tr_source.choices = srcs
    f_tr.tr_destination.choices = srcs

    # received spendings form
    if f_sp.sp_submit.data and f_sp.validate():
        w = Wallets.query.filter_by(user_id=current_user.id, name=f_sp.sp_source.data).first()
        w.amount -= float(f_sp.sp_amount.data)
        db.session.commit()
    
    # received income form
    if f_inc.inc_submit.data and f_inc.validate():
        w = Wallets.query.filter_by(user_id=current_user.id, name=f_inc.inc_destination.data).first()
        w.amount += float(f_inc.inc_amount.data)
        db.session.commit()

    # received transer form
    # TODO

    info = [
        Users.user(current_user.id),
        Wallets.wallets(current_user.id)
    ]

    return render_template("index.html", forms=forms, info=info)


@app.route("/welcome")
def welcome():
    return render_template("welcome.html")


@app.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # create form object
    form = RegistrationForm()

    # if received a valid form
    if form.validate_on_submit():

        # record user to db
        new_user = Users(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        # create default wallet for user
        new_wallet = Wallets(user_id=new_user.id, type='Wallet', name='Cash', amount=42.15)
        db.session.add(new_wallet)
        db.session.commit()

        # success
        flash('Registered')       
        
        return redirect(url_for('login'))

    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # create form object
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


@app.route('/u/<username>', methods=['GET', 'POST'])
@login_required
def account(username):
    
    if username is not current_user.username:
        return redirect('/u/' + current_user.username)

    user = Users.query.filter_by(username=username).first_or_404()
    wallets = Wallets.wallets(current_user.id)

    form = AddWallet()

    if form.validate_on_submit():
        new_wallet = Wallets(user_id=current_user.id)
        new_wallet.name = form.name.data
        new_wallet.type = form.type.data
        new_wallet.amount = 0

        db.session.add(new_wallet)
        db.session.commit()      

    return render_template('account.html', user=user, wallets=wallets, form=form)
    