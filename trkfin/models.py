from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from trkfin import db, login, app


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    email = db.Column(db.String(120), index=True)
    walletcount = db.Column(db.Integer)
    password_hash = db.Column(db.String(128), nullable=False)
    # timezone - TODO


    ###   Basics   ###

    def __init__(self, username):
        self.username = username
        self.walletcount = 0

    def __repr__(self):
        return f'< User id-{self.id} >'


    ###   Password   ###

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    ###   Wallets   ###

    def get_wallets(self):
        return Wallets.query.filter_by(user_id=self.id).order_by('group').order_by('name').all()

    def get_wallets_status(self):
        wallets = self.get_wallets()
        report = {
            'wallets': {},
            'groups': {},
            'sums': {}
        }
        for w in wallets:
            report['wallets'][w.wallet_id] = {
                'name': w.name,
                'group': w.group,
                'balance': w.balance_current
            }
            if w.group not in report['groups']:
                report['groups'][w.group] = {}
                report['sums'][w.group] = {
                    'balance_initial_sum': 0,
                    'income_sum': 0,
                    'spendings_sum': 0,
                    'transfers_sum': 0,
                    'transfers_from_sum': 0,
                    'transfers_to_sum': 0,
                    'balance_current_sum': 0
                }
            report['groups'][w.group][w.wallet_id] = {
                'name': w.name,
                'balance_initial': w.balance_initial,
                'income': w.income,
                'spendings': w.spendings,
                'transfers': w.transfers_from + w.transfers_to,
                'transfers_from': w.transfers_from,
                'transfers_to': w.transfers_to,
                'balance_current': w.balance_current
            }
            report['sums'][w.group]['balance_initial_sum'] += w.balance_initial
            report['sums'][w.group]['income_sum'] += w.income
            report['sums'][w.group]['spendings_sum'] += w.spendings
            report['sums'][w.group]['transfers_sum'] += w.transfers_from + w.transfers_to
            report['sums'][w.group]['transfers_from_sum'] += w.transfers_from
            report['sums'][w.group]['transfers_to_sum'] += w.transfers_to
            report['sums'][w.group]['balance_current_sum'] += w.balance_current
        return report


    ###   History   ###

    def get_history(self):
        return History.query.filter_by(user_id=self.id).order_by(History.id.desc()).all()

    def get_history_json(self):
        history_raw = self.get_history()
        history = []
        for entry in history_raw:
            history.append({
                'id': entry.id,
                # 'ts_utc': entry.ts_utc,
                'ts_local': entry.ts_local,
                'action': entry.action,
                'source': entry.source,
                'destination': entry.destination,
                'amount': entry.amount,
                'description': entry.description,
            })
        return history
    
    
    ###   Reports   ###

    def get_all_reports(self):
        return Reports.query.filter(Reports.user_id==self.id).order_by(Reports.id.desc()).all()
    
    def get_last_report(self):
        return Reports.query.filter(Reports.user_id==self.id).order_by(Reports.id.desc()).first()
    
    def create_report(self, date):
        # 1) [✓] get all wallets, parse into json, create Report();
        # 2) [ ] write Report time: start = end of last report (or account creation),
        #        end = datetime.utcnow default in db;
        # 3) [ ] reset all user's wallets (initial balance = current; inc/spend/transf = 0);
        
        new_rep = Reports(self.id)
        new_rep.time_start = 'test'
        # new_rep.time_start = self.get_last_report()[0]['time_end'] or None
        
        data = self.get_wallets_status()
        data['history'] = self.get_history_json()
        new_rep.data = data

        db.session.add(new_rep)
        db.session.commit()



@login.user_loader
def load_user(id):
    return Users.query.get(int(id))



class Wallets(db.Model):
    wallet_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    balance_initial = db.Column(db.Float, nullable=False)
    income = db.Column(db.Float, nullable=False)
    spendings = db.Column(db.Float, nullable=False)
    transfers_from = db.Column(db.Float, nullable=False)
    transfers_to = db.Column(db.Float, nullable=False)
    balance_current = db.Column(db.Float, nullable=False)
    # currency = db.Column(db.String(8)) - TODO

    def __init__(self, user_id, name, amount):
        self.user_id = user_id
        self.name = name
        self.balance_initial = amount or 0
        self.income = 0
        self.spendings = 0
        self.transfers_from = 0
        self.transfers_to = 0
        self.balance_current = amount or 0

    def __repr__(self):
        return f'< Wallet id-{self.wallet_id} >'



class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ts_utc = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ts_local = db.Column(db.String(23))
    action = db.Column(db.String(20))
    source = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id'))
    destination = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id'))
    amount = db.Column(db.Float)
    description = db.Column(db.String(120))
    
    def __repr__(self):
        return f'< History id-{self.id} >'



class Reports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    time_start = db.Column(db.String(23))
    time_end = db.Column(db.String(23))
    data = db.Column(db.JSON)

    def __init__(self, user_id):
        self.user_id = user_id
        self.data = {}

    def __repr__(self):
        return f'< Report id-{self.id} >'
