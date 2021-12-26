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
    report = {'prev': current_user.get_report_previous().data,
              'curr': current_user.get_report_current().data}

    # MainForm
    form = MainForm()
    # load wallets
    srcs = []
    tmp =report['prev'] 
    for g in tmp:
        for w in tmp[g]['list']:
            if len(g) > 0:
                srcs.append((w['wallet_id'], g + ' | ' + w['name']))
            else:
                srcs.append((w['wallet_id'], w['name']))
    # srcs = [(w.wallet_id, w.group + ' | ' + w.name) for w in report]
    # srcs = [(w.wallet_id, w.group + ' | ' + w.name) for w in Wallets.query.filter_by(user_id=current_user.id).order_by('name')]
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

    return render_template("home.html", form=form, report=report)


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

    wallets = current_user.get_wallets_list()
    form = AddWalletForm()
    if wallets:
        form.group.choices = [(t, t) for t in wallets]
    else:
        form.group.choices = [1]
    form.group.choices[0] = ('', '-- None --')
    form.group.choices.append(('New', '-- New --'))

    if form.validate_on_submit():
        
        # record new wallet
        new_wallet = Wallets()
        new_wallet.user_id = current_user.id
        if form.group.data == 'New':
            new_wallet.group = form.group_new.data
        else:
            new_wallet.group = form.group.data
        new_wallet.name = form.name.data
        new_wallet.amount = form.amount.data
        if not form.amount.data:
            new_wallet.amount = 0
        db.session.add(new_wallet)
        current_user.walletcount += 1
        db.session.commit()

        # add wallet to user's reports
        rep_pr = current_user.get_report_previous()
        rep_cr = current_user.get_report_current()
        for r in [rep_pr.data, rep_cr.data]:
            if new_wallet.group not in r:
                r[new_wallet.group] = {'list': [], 'sum': 0}
            r[new_wallet.group]['list'].append({'wallet_id': new_wallet.wallet_id, 
                                                'name': new_wallet.name,
                                                'amount': new_wallet.amount})
            r[new_wallet.group]['sum'] += new_wallet.amount
        db.session.add(rep_pr)
        db.session.add(rep_cr)
        db.session.commit()
        
        # add history entry
        record = History()
        record.user_id = current_user.id
        record.ts_local = form.timestamp.data
        record.action = "Added wallet"
        if new_wallet.group:
            record.description = str(new_wallet.group) + ": " + str(new_wallet.name)
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
    
    return render_template('wallets.html', form=form, wallets=wallets)


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
