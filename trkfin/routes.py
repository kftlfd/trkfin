from datetime import datetime
from functools import wraps
from json import dumps
from shutil import rmtree
from zipfile import ZipFile
import os

from flask import flash, redirect, render_template, request, send_file, url_for
from flask.ctx import after_this_request
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from trkfin import app, db
from trkfin.forms import AddWalletForm, MainForm
from trkfin.models import History, Reports, Users, Wallets



def check_if_report_due(func):
    # decorator for generating reports
    @wraps(func)
    def wrapper(*args, **kwargs):
        if datetime.utcnow().timestamp() >= current_user.next_report_ts:
            current_user.create_new_report()
            flash("New report is ready!")
        return func(*args, **kwargs)
    return wrapper

def only_personal_data(func):
    # decorator to restrict user to only their own data
    # not necessary, affects only page address (adress bar)
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
        return render_template("home.html")

    form = MainForm()

    # load user's wallets to form
    wallets = current_user.get_wallets_json()
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

        # prevent tranfering from wallet to itself
        if form.action.data == "Transfer" and form.source.data == form.destination.data:
            return redirect(url_for('home'))

        # calculate time
        ts_utc = datetime.utcnow().timestamp() # float
        ts_user_local = ts_utc + current_user.tz_offset # float
        user_local_time = datetime.fromtimestamp(ts_user_local).__str__()[:19]

        # add history entry
        record = History(
            user_id = current_user.id,
            ts_utc = ts_utc,
            local_time = user_local_time,
            action = form.action.data,
            amount = form.amount.data,
            description = form.description.data
        )
        if record.action == 'Spending':
            record.source = form.source.data
        elif record.action == 'Income':
            record.destination = form.destination.data
        else: # Transfer
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
        else: # Transfer
            ws = Wallets.query.get(form.source.data)            
            ws.balance -= float(form.amount.data)
            ws.transfers -= float(form.amount.data)
            wi = Wallets.query.get(form.destination.data)
            wi.balance += float(form.amount.data)
            wi.transfers += float(form.amount.data)
        db.session.commit()

        # success
        flash(f"{record.action} recorded")
        return redirect(url_for('home'))

    return render_template("home.html", form=form, wallets=wallets)



@app.route("/u/<username>/wallets", methods=["GET", "POST"])
@login_required
@only_personal_data
@check_if_report_due
def wallets(username, **kwargs):

    form = AddWalletForm()
    
    # load wallet group names to form
    wallets = current_user.get_wallets_json()
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
            user_id = current_user.id,
            ts_utc = ts_utc,
            local_time = user_local_time,
            action = "Added wallet",
            destination = new_wallet.id,
            amount = form.amount.data
        )
        db.session.add(record)
        db.session.commit()

        # show success message and redirect
        msg = f'Added new wallet "{new_wallet.name}"'
        if new_wallet.group:
            msg += f' to group "{new_wallet.group}"'
        flash(msg)
        return redirect(url_for('wallets', username=current_user.username))
    
    data = {
        'groups': form.group.choices,
        'walletcount': current_user.walletcount
        }
    
    return render_template('wallets.html', form=form, wallets=wallets, data=data)

@app.route("/u/<username>/wallet-controls", methods=["POST"])
def wallet_controls(username, **kwargs):

    if request.form.get('rename-group'):
        group = request.form.get('rename-group')
        if group == "*empty": group = ""
        new_name = request.form.get('new-group-name')
        if group != new_name:
            wallets = Wallets.query.filter(Wallets.user_id==current_user.id, Wallets.group==group).all()
            for w in wallets:
                w.group = new_name
            db.session.commit()
            if group == "": flash(f'Ungrouped wallets moved to "{new_name}"')
            else: flash(f'Group "{group}" renamed to "{new_name}"')

    elif request.form.get('delete-group'):
        group = request.form.get('delete-group')
        if group == "*empty": group = ""
        wallets = Wallets.query.filter(Wallets.user_id==current_user.id, Wallets.group==group).all()
        
        ts_utc = datetime.utcnow().timestamp() # float
        ts_user_local = ts_utc + current_user.tz_offset # float
        user_local_time = datetime.fromtimestamp(ts_user_local).__str__()[:19]
        
        for w in wallets:
            w_name = w.name
            w_group = w.group
            if request.form.get('delete-wallets'):
                db.session.add(History(
                    user_id = current_user.id,
                    ts_utc = ts_utc,
                    local_time = user_local_time,
                    action = "Deleted wallet",
                    description = f'"{w_name} ({w_group})"' if w_group else f'"{w_name}"'
                ))
                db.session.delete(w)
                current_user.walletcount -= 1
                db.session.commit()
            else:
                w.group = ""
        db.session.commit()
        
        if group and request.form.get('delete-wallets'):
            flash(f'Group "{group}" and wallets deleted')
        elif group:
            flash(f'Group "{group}" deleted, wallets moved to ungrouped')
        else:
            flash("Ungrouped wallets deleted")

    elif request.form.get('rename-w'):
        w_id = request.form.get('rename-w')
        new_name = request.form.get('new-name')
        to_rnm = Wallets.query.get(w_id)
        old_name = to_rnm.name
        group = to_rnm.group
        to_rnm.name = new_name
        db.session.commit()
        if group: flash(f'"{old_name} ({group})" renamed to "{new_name} ({group})"')
        else: flash(f'"{old_name}" renamed to "{new_name}"')

    elif request.form.get('change-w-group'):
        w_id = request.form.get('change-w-group')
        to_change = Wallets.query.get(w_id)
        name = to_change.name
        old_group = to_change.group
        new_group = request.form.get('user-group')
        if new_group == "*New":
            new_group = request.form.get('new-group')
        if to_change.group != new_group:
            to_change.group = new_group
            db.session.commit()
            if old_group and new_group: flash(f'"{name} ({old_group})" changed group to "{name} ({new_group})"')
            elif old_group: flash(f'"{name} ({old_group})" moved to ungrouped')
            else: flash(f'"{name}" moved to group "{new_group}"')

    elif request.form.get('delete-w'):
        w_id = request.form.get('delete-w')
        to_del = Wallets.query.get(w_id)
        name = to_del.name
        group = to_del.group
        db.session.delete(to_del)
        current_user.walletcount -= 1
        
        ts_utc = datetime.utcnow().timestamp() # float
        ts_user_local = ts_utc + current_user.tz_offset # float
        user_local_time = datetime.fromtimestamp(ts_user_local).__str__()[:19]

        record = History(
            user_id = current_user.id,
            ts_utc = ts_utc,
            local_time = user_local_time,
            action = "Deleted wallet",
            description = f'"{name} ({group})"' if group else f'"{name}"'
        )
        db.session.add(record)
        db.session.commit()
        flash(f'Deleted wallet "{name} (group)"')
    
    return redirect(url_for('wallets', username=current_user.username))



@app.route('/u/<username>/reports')
@login_required
@only_personal_data
@check_if_report_due
def reports(username):
    reports = current_user.get_reports()
    return render_template('reports.html', reports=reports, next_report_ts=current_user.next_report_ts, user_tz=current_user.tz_offset)

@app.route('/u/<username>/new-report', methods=['POST'])
def new_report(username):
    time_end = datetime.utcnow().timestamp()
    current_user.create_new_report(end=time_end)
    flash("New report created!")
    return redirect(url_for('reports', username=current_user.username))

@app.route('/ajax-report')
def ajax_report():
    return "Nothing here yet"



@app.route("/u/<username>/history")
@login_required
@only_personal_data
@check_if_report_due
def history(username):
    history = current_user.get_history_json()
    wallets = current_user.get_wallets_json()
    return render_template('history.html', history=history, wallets=wallets)



@app.route('/u/<username>')
@login_required
@only_personal_data
@check_if_report_due
def account(username):
    data = {
        'username': current_user.username,
        'email': current_user.email,
        'timezone': current_user.tz_offset,
        'rep-freq': current_user.report_frequency,
        'email-reports': current_user.email_reports
    }
    return render_template('account.html', data=data)

@app.route('/u/<username>/account-settings', methods=['POST'])
@login_required
def account_settings(username):

    if request.form.get("new-username"):
        check = Users.query.filter(Users.username==request.form.get("new-username")).all()
        if len(check) != 0:
            flash("New username is not available")
        else:
            current_user.username = request.form.get("new-username")
            db.session.commit()
            flash(f'Username changed to "{current_user.username}"')

    elif request.form.get("new-email"):
        current_user.email = request.form.get("new-email")
        db.session.commit()
        flash(f'E-mail is set to "{current_user.email}"')

    elif request.form.get("new-password"):
        if not current_user.check_password(request.form.get("old-password")):
            flash('Wrong password')
        elif request.form.get("new-password") != request.form.get("repeat-password"):
            flash("Passwords don't match")
        else:
            current_user.set_password(request.form.get("new-password"))
            db.session.commit()
            flash('Password changed')

    elif request.form.get("new-timezone"):
        current_user.tz_offset = request.form.get("new-timezone")
        db.session.commit()
        flash('Timezone updated')

    elif request.form.get("new-report-frequency"):

        new_freq = request.form.get("new-report-frequency")
        if current_user.report_frequency == new_freq or current_user.report_frequency == request.form.get("ndays"):
            pass
        elif new_freq == 'other' and request.form.get("ndays") >= 1 and request.form.get("ndays") <= 365:
            current_user.report_frequency = request.form.get("ndays")
            flash(f'Reports are set to every {request.form.get("ndays")} days')
        else:
            current_user.report_frequency = new_freq
            flash(f'Reports are set to every {new_freq}')
        
        if request.form.get("email-reports") == "on" and not current_user.email_reports:
            current_user.email_reports = True
            flash('E-mailing reports')
        elif not request.form.get("email-reports") and current_user.email_reports:
            current_user.email_reports = False
            flash('Stoped e-mailing reports')
            
        current_user.update_next_report_ts()
        db.session.commit()
    
    return redirect(url_for('account', username=current_user.username))

@app.route('/export-data', methods=['POST'])
@login_required
def export_data():

    @after_this_request
    def delete_export(response):
        rmtree("trkfin/export/")
        return response

    data = current_user.get_export_data()
    if not os.path.exists('trkfin/export/'):
        os.mkdir('trkfin/export/')
    with ZipFile('trkfin/export/export.zip', 'w') as zf:
        with open('trkfin/export/raw.json', 'w') as f:
            f.write(dumps(data))
        with open('trkfin/export/export.html', 'w') as f2:
            f2.write(render_template('export.html', data=data))
        zf.write('trkfin/export/raw.json', arcname="raw.json")
        zf.write('trkfin/export/export.html', arcname="export.html")

    return send_file('export/export.zip')

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    
    # remember id
    id = current_user.id
    logout_user()
    
    # gather and delete data from db
    u = Users.query.get(id)
    w = Wallets.query.filter(Wallets.user_id==id).all()
    h = History.query.filter(History.user_id==id).all()
    r = Reports.query.filter(Reports.user_id==id).all()
    db.session.delete(u)
    for i in w: db.session.delete(i)
    for i in h: db.session.delete(i)
    for i in r: db.session.delete(i)
    db.session.commit()
    
    flash('Account deleted')
    return redirect(url_for('index'))



############### TESTING ###############

# RESET DB - FOR TESTING ONLY
@app.route('/resetdb')
def resetdb():
    if os.path.exists('trkfin.db'):
        os.remove("trkfin.db")
    f = open('trkfin.db', 'x')
    f.close()
    db.create_all()
    return redirect('/')

@app.route('/test-export')
def test_export():
    data = current_user.get_export_data()
    return render_template('export.html', data=data)
