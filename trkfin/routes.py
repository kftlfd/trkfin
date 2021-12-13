from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from os import remove, path

from trkfin import app, db
from trkfin.models import Users, Wallets, History
from trkfin.forms import LoginForm, RegistrationForm, AddWalletForm, MainForm


@app.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('welcome'))
    else:
        return redirect(url_for('home'))


@app.route("/haddw", methods=['GET', 'POST'])
def haddw():
    form = AddWalletForm()
    if form.validate_on_submit():
        new_wallet = Wallets(user_id=current_user.id)
        new_wallet.name = form.name.data
        if form.type.data is not None:
            new_wallet.type = form.type.data
        else:
            new_wallet.type = form.type_new.data
        new_wallet.currency = None
        new_wallet.amount = 0

        db.session.add(new_wallet)
        db.session.commit()  

        return redirect(url_for('home'))

@app.route("/home", methods=['GET', 'POST'])
def home():    

    if not current_user.is_authenticated:
        return redirect(url_for('welcome'))

    # prepare form objects
    if current_user.wallets_count() < 1:
        mf = AddWalletForm()
        return render_template("home.html", mf=mf, nw=True)
    else:
        mf = MainForm()

    # load wallets
    srcs = [(w.wallet_id, w.name) for w in Wallets.query.filter_by(user_id=current_user.id).order_by('name')]
    mf.source.choices = srcs
    mf.destination.choices = srcs

    # received main form
    if mf.submit.data and mf.validate():

        if mf.action.data == 'spending':
            mf.amount.data = float(mf.amount.data) * (-1.0)

        w = Wallets.query.get(mf.source.data)
        w.amount += float(mf.amount.data)
        
        record = History()
        record.user_id = current_user.id
        ts = mf.timestamp.data
        record.ts_year = ts[0:4]
        record.ts_month = ts[5:7]
        record.ts_day = ts[8:10]
        record.ts_hour = ts[11:13]
        record.ts_minute = ts[14:16]
        record.ts_second = ts[17:19]
        record.ts_ms = ts[20:]
        record.action = mf.action.data
        record.source = mf.source.data
        record.destination = mf.destination.data
        record.amount = mf.amount.data
        record.description = mf.description.data

        current_user.stats = {}
        current_user.stats['test'] = 'test'
        
        db.session.add(record)
        db.session.commit()
        flash(record)
        

    info = {}
    if current_user.is_authenticated:
        info['user'] = Users.user(current_user.id)
        info['wallets'] = Wallets.wallets(current_user.id)
        info['history'] = History.user_history(current_user.id)
        info['report'] = History.month_report(current_user.id, 2021, 11)
        info['stats'] = current_user.get_stats()

    return render_template("home.html", mf=mf, info=info)


@app.route("/welcome")
def welcome():
    return render_template("welcome.html")



@app.route('/u/<username>', methods=['GET', 'POST'])
@login_required
def account(username):
    
    if username is not current_user.username:
        return redirect('/u/' + current_user.username)

    user = Users.query.filter_by(username=username).first_or_404()
    wallets = Wallets.wallets(current_user.id)
    history = History.user_history(current_user.id)

    form = AddWalletForm()
    srcs = []
    for w in Wallets.query.filter_by(user_id=current_user.id).all():
        srcs.append(w.type)
    form.type.choices = srcs

    if form.validate_on_submit():
        new_wallet = Wallets(user_id=current_user.id)
        new_wallet.name = form.name.data
        if form.type.data is not None:
            new_wallet.type = form.type.data
        else:
            new_wallet.type = form.type_new.data
        new_wallet.currency = None
        new_wallet.amount = 0

        db.session.add(new_wallet)
        db.session.commit()  

        return redirect(url_for('account', username=current_user.username))    

    return render_template('account.html', user=user, wallets=wallets, history=history, form=form)


@app.route("/u/<username>/history")
@login_required
def history(username):
    
    if username is not current_user.username:
        return redirect('/u/' + current_user.username + '/history')

    history = History.user_history(current_user.id)

    return render_template('history.html', history=history)


@app.route("/u/<username>/wallets")
@login_required
def wallets(username):
    
    if username is not current_user.username:
        return redirect('/u/' + current_user.username + '/wallets')

    wallets = Wallets.wallets(current_user.id)
    form = AddWalletForm()

    return render_template('wallets.html', wallets=wallets, form=form)
    

@app.route('/resetdb')
def resetdb():
    if path.exists('trkfin.db'):
        remove("trkfin.db")
    f = open('trkfin.db', 'x')
    f.close()
    db.create_all()
    return redirect('/')
