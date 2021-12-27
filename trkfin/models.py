from datetime import datetime
from flask_login import UserMixin
from sqlalchemy_json import NestedMutableJson
from werkzeug.security import generate_password_hash, check_password_hash

from trkfin import db, login, app


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    email = db.Column(db.String(120), index=True)
    walletcount = db.Column(db.Integer)
    current_report = db.Column(db.Integer, db.ForeignKey('reports.id'))
    password_hash = db.Column(db.String(128), nullable=False)
    # timezone - TODO

    def __init__(self, username):
        self.username = username
        self.walletcount = 0

    def __repr__(self):
        return '< User: ' + str({
            'id': self.id,
            'username': self.username,
            'created': self.created,
            'email': self.email,
            'walletcount': self.walletcount,
            'report-id': self.current_report
        }) + ' >'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_wallets_list(self):
        ''' output dict:
            {w_group1: {'list': {w1_id: {name: ... ,
                                         amount: ...
                                        },
                                w2_id: {...}
                                ... 
                                },
                        'sum': sum
                        },
            w_group2: ...,
            ...
            }
        '''
        
        wallets = {}
        sorted_by_type = Wallets.query.filter_by(user_id=self.id).order_by('group').order_by('name').all()
        groups = set()
        for w in sorted_by_type:
            if w.group not in groups:
                groups.add(w.group)
                wallets[w.group] = {'list': {}, 'sum': 0}
            wallets[w.group]['list'][w.wallet_id] = {'name': w.name,
                                                     'amount': w.amount}
            wallets[w.group]['sum'] += w.amount
        return wallets

    def get_report_previous(self):
        return Reports.query.get(int(self.report_previous))

    def get_report_current(self):
        return Reports.query.get(int(self.report_current))

    def get_report(self):
        return Reports.query.get(int(self.current_report))
    
    def start_new_report(self, date):
        pass
        # TODO:
        # write date to current user's report
        # create new Report object
        # copy old.balance_current to new.balance_initial
        # save new as user's current_report

    def get_history(self):
        return History.query.filter_by(user_id=self.id).order_by(History.id.desc()).all()


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Wallets(db.Model):
    wallet_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    # currency = db.Column(db.String(8)) - TODO

    def __repr__(self):
        return '< Wallet: ' + str({
            'w_id': self.wallet_id,
            'u_id': self.user_id,
            'name': self.name,
            'group': self.group,
            'amount': self.amount
        }) + ' >'


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
        return '< History: ' + str({
            'record-id': self.id,
            'u_id': self.user_id,
            'ts_uts': self.ts_utc,
            'ts_local': self.ts_local,
            'action': self.action,
            'from': self.source,
            'to': self.destination,
            'amount': self.amount,
            'description': self.description
        }) + ' >'


class Reports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.String(23))
    balance_initial = db.Column(NestedMutableJson)
    income  = db.Column(NestedMutableJson)
    spendings = db.Column(NestedMutableJson)
    transfers = db.Column(NestedMutableJson)
    balance_current = db.Column(NestedMutableJson)

    def __init__(self, user_id):
        self.user_id = user_id
        self.balance_initial = {}
        self.income = {}
        self.spendings = {}
        self.transfers = {}
        self.balance_current = {}

    def __repr__(self):
        return '< Report: ' + str({
            'rep_id': self.id,
            'u_id': self.user_id,
            'date': self.date,
            'initial': self.balance_initial,
            'income': self.income,
            'spendings': self.spendings,
            'transfers': self.transfers,
            'current': self.balance_current
        })
