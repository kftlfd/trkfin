from flask import flash, redirect, render_template, request, url_for, jsonify
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
        # mb do addWalletForm here after all
        # no need to load groups/ids
        return redirect(url_for('wallets', username=current_user.username, next='home'))

    form = MainForm()
    wallets = current_user.get_wallets_status()

    # load user's wallets to form
    srcs = []
    for group in wallets['groups']:
        for w_id in wallets['groups'][group]:
            if len(group) > 0:
                srcs.append( (w_id, group + ' | ' + wallets['groups'][group][w_id]['name']) )
            else:
                srcs.append( (w_id, wallets['groups'][group][w_id]['name']) )
    form.source.choices = srcs
    form.destination.choices = srcs

    # process MainForm - TODO
    if form.validate_on_submit():

        # add history entry
        record = History()
        record.user_id = current_user.id
        record.ts_local = form.timestamp.data
        record.action = form.action.data
        if record.action == 'Spending':
            record.source = form.source.data
        elif record.action == 'Income':
            record.destination = form.destination.data
        else:
            record.source = form.source.data
            record.destination = form.destination.data
        record.amount = form.amount.data
        record.description = form.description.data
        db.session.add(record)

        # update wallets
        if form.action.data == 'Spending':
            ws = Wallets.query.get(form.source.data)
            ws.balance_current -= float(form.amount.data)
            ws.spendings -= float(form.amount.data)
            db.session.add(ws)
        elif form.action.data == 'Income':
            wi = Wallets.query.get(form.destination.data)
            wi.balance_current += float(form.amount.data)
            wi.income += float(form.amount.data)
            db.session.add(wi)
        else:
            ws = Wallets.query.get(form.source.data)            
            wi = Wallets.query.get(form.destination.data)

            ws.balance_current -= float(form.amount.data)
            ws.transfers_from -= float(form.amount.data)

            wi.balance_current += float(form.amount.data)
            wi.transfers_to += float(form.amount.data)

            db.session.add(ws)
            db.session.add(wi)

        db.session.commit()

        flash("action recorded")

        return redirect(url_for('home'))

    return render_template("home.html", form=form, wallets=wallets)

@app.route('/test')
def test():
    # wallets = current_user.generate_current_report()
    # return jsonify(wallets)
    # return current_user.get_full_report()
    # return current_user.get_wallets_status()
    # return current_user.get_history()
    # return jsonify(current_user.get_wallets_groups())
    # return current_user.get_wallets_list()
    report = current_user.get_full_report()
    return render_template('rep.html', report=report)


# decorator to restrict user to only their own data
# not necessary, affects only page address (adress bar)
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
    wallets = current_user.get_wallets_status()

    # load wallet group names to form
    groups = set()
    for g in wallets['groups']:
        groups.add(g)
    if groups:
        form.group.choices = [(g, g) for g in groups]
    else:
        form.group.choices = [1]
    form.group.choices[0] = ('', '-- None --') # change display of unnamed group
    form.group.choices.append(('New', '-- New --'))

    # process add-wallet form
    if form.validate_on_submit():
        
        # record new wallet
        new_wallet = Wallets(current_user.id, form.name.data, form.amount.data)
        if form.group.data == 'New':
            new_wallet.group = form.group_new.data
        else:
            new_wallet.group = form.group.data
        db.session.add(new_wallet)
        current_user.walletcount += 1
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
        record.amount = form.amount.data
        db.session.add(record)
        db.session.commit()

        # show success message and redirect
        msg = f'Added new wallet "{new_wallet.name}"'
        if len(new_wallet.group) > 0:
            msg += f' to group "{new_wallet.group}"'
        flash(msg)
        if request.args:
            next_page = url_for(request.args.get('next'))
        else:
            next_page = url_for('wallets', username=current_user.username)
        return redirect(next_page)
    
    return render_template('wallets.html', form=form, wallets=wallets)


@app.route('/u/<username>/reports')
@login_required
@only_personal_data
def reports(username):
    return render_template('reports.html')


@app.route("/u/<username>/history")
@login_required
@only_personal_data
def history(username):
    # add pagination or continuous load - TODO
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
