from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from functools import wraps
from werkzeug.urls import url_parse

from os import remove, path

from trkfin import app, db
from trkfin.models import Users, Wallets, History
from trkfin.forms import MainForm, AddWalletForm


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return render_template("welcome.html")


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():

    if current_user.walletcount < 1:
        return redirect(url_for('wallets', username=current_user.username, next='home'))

    # report - TODO
    report = {'test': 1}
    info = {}
    info['user'] = current_user
    info['wallets'] = current_user.get_wallets_list()
    info['history'] = current_user.get_history()
    info['report'] = History.query.filter(History.user_id==current_user.id).filter(History.ts_local.like('2021%')).all()
    info['stats'] = current_user.stats

    # MainForm
    form = MainForm()
    # load wallets
    srcs = [(w.wallet_id, w.name) for w in Wallets.query.filter_by(user_id=current_user.id).order_by('name')]
    form.source.choices = srcs
    form.destination.choices = srcs
    # process MainForm - TODO
    if form.validate_on_submit():

        # if mf.action.data == 'spending':
        #     mf.amount.data = float(mf.amount.data) * (-1.0)

        # w = Wallets.query.get(mf.source.data)
        # w.amount += float(mf.amount.data)
        
        # record = History()
        # record.user_id = current_user.id
        # ts = mf.timestamp.data
        # record.ts_year = ts[0:4]
        # record.ts_month = ts[5:7]
        # record.ts_day = ts[8:10]
        # record.ts_hour = ts[11:13]
        # record.ts_minute = ts[14:16]
        # record.ts_second = ts[17:19]
        # record.ts_ms = ts[20:]
        # record.action = mf.action.data
        # record.source = mf.source.data
        # record.destination = mf.destination.data
        # record.amount = mf.amount.data
        # record.description = mf.description.data

        # current_user.stats = {}
        # current_user.stats['test'] = 'test'
        
        # db.session.add(record)
        # db.session.commit()
        # flash(record)

        flash("Processing MainForm")

        return redirect(url_for('home'))

    return render_template("home.html", form=form, report=report, info=info)


# decorator to restrict user to only their own data
def only_personal_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['username'] is not current_user.username:
            return redirect(url_for(func.__name__, username=current_user.username))
        return func(*args, **kwargs)
    return wrapper


@app.route("/u/<username>/wallets", methods=["GET", "POST"])
@login_required
@only_personal_data
def wallets(username, **kwargs):

    form = AddWalletForm()
    # load wallet types - TODO

    if form.validate_on_submit():
        
        # record new wallet
        new_wallet = Wallets()
        new_wallet.user_id = current_user.id
        if form.type.data is not None:
            new_wallet.type = form.type.data
        else:
            new_wallet.type = form.type_new.data
        new_wallet.name = form.name.data
        new_wallet.amount = form.amount.data
        db.session.add(new_wallet)
        current_user.walletcount += 1
        db.session.commit()
        
        # add history entry
        record = History()
        record.user_id = current_user.id
        record.ts_local = form.timestamp.data
        record.action = "Added wallet"
        if new_wallet.type:
            record.description = str(new_wallet.type) + ": " + str(new_wallet.name)
        else:
            record.description = str(new_wallet.name)
        record.amount = new_wallet.amount
        db.session.add(record)
        db.session.commit()

        flash("Added new wallet")
        if request.args:
            next_page = url_for(request.args.get('next'))
        else:
            next_page = url_for('wallets', username=current_user.username)
        return redirect(next_page)
    
    return render_template('wallets.html', form=form, wallets=current_user.get_wallets_list())


@app.route("/u/<username>/history")
@login_required
@only_personal_data
def history(username):
    # pagination or continuous load - TODO
    return render_template('history.html', history=current_user.get_history())


@app.route('/u/<username>', methods=['GET', 'POST'])
@login_required
@only_personal_data
def account(username):
    return render_template('account.html')


# RESET DB - FOR TESTING ONLY
@app.route('/resetdb')
def resetdb():
    if path.exists('trkfin.db'):
        remove("trkfin.db")
    f = open('trkfin.db', 'x')
    f.close()
    db.create_all()
    return redirect('/')
