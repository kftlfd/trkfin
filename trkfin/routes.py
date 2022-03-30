from datetime import datetime
from functools import wraps
from json import dumps
from os import path, remove
from shutil import rmtree
from zipfile import ZipFile

from flask import flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from trkfin import app, db
from trkfin.forms import AddWalletForm, MainForm
from trkfin.models import History, Reports, Users, Wallets



# decorator for generating reports
def check_if_report_due(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if datetime.utcnow().timestamp() >= current_user.next_report:
            current_user.generate_report()
        return func(*args, **kwargs)
    return wrapper



# decorator to restrict user to only their own data
# not necessary, affects only page address (adress bar)
def only_personal_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['username'] is not current_user.username:
            return redirect(url_for(func.__name__, username=current_user.username))
        return func(*args, **kwargs)
    return wrapper



@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return render_template("index.html")



@app.route("/home", methods=["GET", "POST"])
@login_required
@check_if_report_due
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

    # process MainForm
    if form.validate_on_submit():

        # calculate time
        ts_utc = datetime.utcnow().timestamp() # float
        ts_user_local = ts_utc + current_user.tz_offset # float
        user_local_time = datetime.fromtimestamp(ts_user_local).__str__()[:19]

        # add history entry
        record = History(
            user_id=current_user.id,
            ts_utc=ts_utc,
            local_time=user_local_time,
            action=form.action.data,
            amount=form.amount.data,
            description=form.description.data)
        if record.action == 'Spending':
            record.source = form.source.data
        elif record.action == 'Income':
            record.destination = form.destination.data
        else:
            record.source = form.source.data
            record.destination = form.destination.data
        db.session.add(record)

        # update wallets
        if form.action.data == 'Spending':
            ws = Wallets.query.get(form.source.data)
            ws.balance -= float(form.amount.data)
            ws.spendings -= float(form.amount.data)
        elif form.action.data == 'Income':
            wi = Wallets.query.get(form.destination.data)
            wi.balance += float(form.amount.data)
            wi.income += float(form.amount.data)
        else:
            ws = Wallets.query.get(form.source.data)            
            ws.balance -= float(form.amount.data)
            ws.transfers -= float(form.amount.data)
            wi = Wallets.query.get(form.destination.data)
            wi.balance += float(form.amount.data)
            wi.transfers += float(form.amount.data)
        db.session.commit()

        flash("action recorded")

        return redirect(url_for('home'))

    return render_template("home.html", form=form, wallets=wallets)



@app.route("/u/<username>/wallets", methods=["GET", "POST"])
@login_required
@only_personal_data
@check_if_report_due
def wallets(username, **kwargs):

    # wallet controls (kinda ugly)

    if request.form.get('rename-group'):
        group = request.form.get('rename-group')
        if group == "*empty": group = ""
        new_name = request.form.get('new-group-name')
        if group != new_name:
            wallets = Wallets.query.filter(Wallets.user_id==current_user.id, Wallets.group==group).all()
            for w in wallets:
                w.group = new_name
            db.session.commit()
            flash('group renamed')
        return redirect(url_for('wallets', username=current_user.username))

    if request.form.get('delete-group'):
        group = request.form.get('delete-group')
        if group == "*empty": group = ""
        wallets = Wallets.query.filter(Wallets.user_id==current_user.id, Wallets.group==group).all()
        for w in wallets:
            if request.form.get('delete-wallets'):
                db.session.delete(w)
                current_user.walletcount -= 1
            else:
                w.group = ""
        db.session.commit()
        if request.form.get('delete-wallets'):
            flash('group and wallets deleted')
        else:
            flash('group deleted, wallets moved to ungrouped')
        return redirect(url_for('wallets', username=current_user.username))

    if request.form.get('rename-w'):
        w_id = request.form.get('rename-w')
        new_name = request.form.get('new-name')
        to_rnm = Wallets.query.get(w_id)
        to_rnm.name = new_name
        db.session.commit()
        flash(f'renamed to "{new_name}"')
        return redirect(url_for('wallets', username=current_user.username))

    if request.form.get('change-w-group'):
        w_id = request.form.get('change-w-group')
        to_change = Wallets.query.get(w_id)
        new_group = request.form.get('user-group')
        if new_group == "*New":
            new_group = request.form.get('new-group')
        if to_change.group != new_group:
            to_change.group = new_group
            db.session.commit()
            flash('changed group')
        return redirect(url_for('wallets', username=current_user.username))

    if request.form.get('delete-w'):
        w_id = request.form.get('delete-w')
        to_del = Wallets.query.get(w_id)
        db.session.delete(to_del)
        current_user.walletcount -= 1
        db.session.commit()
        flash(f'deleted wallet with id {w_id}')
        return redirect(url_for('wallets', username=current_user.username))

    form = AddWalletForm()
    
    wallets = current_user.get_wallets_status()

    # load wallet group names to form
    groups = set()
    for g in wallets['groups']:
        groups.add(g)
    form.group.choices = [(g, g) for g in groups]
    if groups and form.group.choices[0][0] != "":
        form.group.choices.insert(0, ('', '-- None --'))
    elif groups:
        form.group.choices[0] = ('', '-- None --')
    else:
        form.group.choices.append(('', '-- None --'))
    form.group.choices.append(('*New', '-- New --'))

    # process add-wallet form
    if form.validate_on_submit():
        
        # calculate time
        ts_utc = datetime.utcnow().timestamp() # float
        ts_user_local = ts_utc + current_user.tz_offset # float
        user_local_time = datetime.fromtimestamp(ts_user_local).__str__()[:19]

        # record new wallet
        new_wallet = Wallets(current_user.id, form.name.data, form.amount.data)
        if form.group.data == '*New':
            new_wallet.group = form.group_new.data
        else:
            new_wallet.group = form.group.data
        db.session.add(new_wallet)
        current_user.walletcount += 1
        db.session.commit()
        
        # add history entry
        record = History(
            user_id=current_user.id,
            ts_utc=ts_utc,
            local_time=user_local_time,
            action="Added wallet",
            destination=new_wallet.id,
            amount=form.amount.data)
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
    
    data = {
        'groups': form.group.choices,
        'walletcount': current_user.walletcount
    }
    
    return render_template('wallets.html', form=form, wallets=wallets, data=data)



@app.route('/u/<username>/reports')
@login_required
@only_personal_data
@check_if_report_due
def reports(username):
    # if request.args.get('newrep') == "yes":
    #     current_user.generate_report()
    #     return redirect(url_for('reports', username=current_user.username))
    reports = current_user.get_all_reports()
    return render_template('reports.html', reports=reports)



@app.route("/u/<username>/history")
@login_required
@only_personal_data
@check_if_report_due
def history(username):
    history = current_user.get_history_json()
    wallets = current_user.get_wallets_json()
    return render_template('history.html', history=history, wallets=wallets)



@app.route('/u/<username>', methods=['GET', 'POST'])
@login_required
@only_personal_data
@check_if_report_due
def account(username):

    # kinda ugly

    if request.form.get("new-username"):
        check = Users.query.filter(Users.username==request.form.get("new-username")).all()
        if len(check) != 0:
            return redirect(url_for('account', username=current_user.username))
        current_user.username = request.form.get("new-username")
        db.session.commit()
        flash('changed username')
        return redirect(url_for('account', username=current_user.username))

    if request.form.get("new-email"):
        current_user.email = request.form.get("new-email")
        db.session.commit()
        flash('changed email')
        return redirect(url_for('account', username=current_user.username))

    if request.form.get("new-password"):
        if not current_user.check_password(request.form.get("old-password")):
            flash('wrong password')
            return redirect(url_for('account', username=current_user.username))
        current_user.set_password(request.form.get("new-password"))
        db.session.commit()
        flash('changed password')
        return redirect(url_for('account', username=current_user.username))

    if request.form.get("new-timezone"):
        flash('tz upd')
        current_user.tz_offset = request.form.get("new-timezone")
        db.session.commit()
        flash('updated timezone')
        return redirect(url_for('account', username=current_user.username))

    if request.form.get("new-report-frequency"):
        new_freq = request.form.get("new-report-frequency")
        if new_freq == 'other':
            new_freq = request.form.get("ndays")
        if len(new_freq) < 1:
            return redirect(url_for('account', username=current_user.username))
        current_user.report_frequency = new_freq
        db.session.commit()
        flash('set new rep freq')
        return redirect(url_for('account', username=current_user.username))
    
    if request.form.get("email-reports-pref"):
        if request.form.get("email-reports") and not current_user.email_reports:
            current_user.email_reports = True
            flash('emailing reports')
        elif request.form.get("email-reports") and current_user.email_reports:
            pass
        elif current_user.email_reports:
            current_user.email_reports = False
            flash('emailing stoped')
        db.session.commit()
        return redirect(url_for('account', username=current_user.username))

    if request.form.get("export-data"):
        flash('export requested')
        data = current_user.get_export_data()
        with ZipFile('trkfin/exports/export.zip', 'w') as zip:
            with open('trkfin/exports/raw.json', 'w') as file:
                file.write(dumps(data))
            zip.write('trkfin/exports/raw.json', arcname="raw.json")
        return send_file('exports/export.zip')
    
    if request.form.get("delete-account"):
        id = current_user.id
        logout_user()
        u = Users.query.get(id)
        w = Wallets.query.filter(Wallets.user_id==id).all()
        h = History.query.filter(History.user_id==id).all()
        r = Reports.query.filter(Reports.user_id==id).all()
        db.session.delete(u)
        for i in w: db.session.delete(i)
        for i in h: db.session.delete(i)
        for i in r: db.session.delete(i)
        db.session.commit()
        flash('account deleted')
        return redirect(url_for('index'))

    data = {
        'username': current_user.username,
        'email': current_user.email,
        'timezone': current_user.tz_offset,
        'rep-freq': current_user.report_frequency,
        'email-reports': current_user.email_reports
    }

    return render_template('account.html', data=data)

@app.after_request
def delete_user_export(response):
    if request.endpoint == "account" and request.form.get("export-data"):
        rmtree("trkfin/exports/")
    return response



############### TESTING ###############

# RESET DB - FOR TESTING ONLY
@app.route('/resetdb')
def resetdb():
    if path.exists('trkfin.db'):
        remove("trkfin.db")
    f = open('trkfin.db', 'x')
    f.close()
    db.create_all()
    return redirect('/')

@app.route('/test')
def test():
    report = current_user.get_wallets_status()
    report['history'] = current_user.get_history_json()
    # return render_template('rep.html', report=report)
    return report