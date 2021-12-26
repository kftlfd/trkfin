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
    stats = db.Column(NestedMutableJson)
    report_previous = db.Column(db.Integer, db.ForeignKey('reports.id'))
    report_current = db.Column(db.Integer, db.ForeignKey('reports.id'))
    password_hash = db.Column(db.String(128), nullable=False)
    # timezone - TODO

    def __init__(self, username):
        self.username = username
        self.walletcount = 0
        self.stats = {}

    def __repr__(self):
        return '< User: ' + str({
            'id': self.id,
            'username': self.username,
            'created': self.created,
            'email': self.email,
            'walletcount': self.walletcount,
            'stats': self.stats
        }) + ' >'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_wallets_list(self):
        list = {}
        sorted_by_type = Wallets.query.filter_by(user_id=self.id).order_by('group').order_by('name').all()
        groups = set()
        for w in sorted_by_type:
            if w.group not in groups:
                groups.add(w.group)
                list[w.group] = {'list': [], 'sum': 0}
            list[w.group]['list'].append({'wallet_id': w.wallet_id,
                                          'name': w.name,
                                          'amount': w.amount})
            list[w.group]['sum'] += w.amount
        return list

    def get_report_previous(self):
        return Reports.query.get(int(self.report_previous))

    def get_report_current(self):
        return Reports.query.get(int(self.report_current))

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
            'wallet': self.wallet_id,
            'user': self.user_id,
            'name': self.name,
            'group': self.group,
            'amount': self.amount
        }) + ' >'


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    ts_utc = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ts_local = db.Column(db.String(23))

    ts_year = db.Column(db.Integer)
    ts_month = db.Column(db.Integer)
    ts_day = db.Column(db.Integer)
    ts_hour = db.Column(db.Integer)
    ts_minute = db.Column(db.Integer)
    ts_second = db.Column(db.Integer)
    ts_ms = db.Column(db.Integer)
    
    action = db.Column(db.String(20))
    source = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id'))
    destination = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id'))
    amount = db.Column(db.Float)
    description = db.Column(db.String(120))
    
    def __repr__(self):
        return '< History: ' + str({
            'id': self.id,
            'user': self.user_id,
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
    data = db.Column(NestedMutableJson)

    def __init__(self, user_id):
        self.user_id = user_id
        self.data = {}
