from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.types import PickleType
from werkzeug.security import generate_password_hash, check_password_hash

from trkfin import db, login, app


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    email = db.Column(db.String(120), index=True)
    walletcount = db.Column(db.Integer)
    stats = db.Column(PickleType)
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
        grouped = {}
        sorted_by_type = Wallets.query.filter_by(user_id=self.id).order_by('group').order_by('name').all()
        groups = set()
        for w in sorted_by_type:
            if w.group not in groups:
                groups.add(w.group)
                grouped[w.group] = []
            grouped[w.group].append(w)
        return grouped

    def get_history(self):
        return History.query.filter_by(user_id=self.id).order_by(History.id.desc()).all()

    def month_report(uid, year, month):

        # query db for all records
        data = History.query.filter(History.user_id==uid, History.ts_year==year, History.ts_month==month).all()
        if not data:
            return False

        # sort data, populate income and spending dicts
        income = {'total': 0}
        inc_wallets = set()
        spending = {'total': 0}
        spend_wallets = set()
        for record in data:
            
            # income
            if record.action == "income":
                if record.destination not in inc_wallets:
                    w = Wallets.query.filter(Wallets.wallet_id==record.destination).first()
                    income[record.destination] = {
                        'name': w.name,
                        'type': w.type,
                        'amount': record.amount
                    }
                    inc_wallets.add(record.destination)
                else:
                    income[record.destination]['amount'] += record.amount
                income['total'] += record.amount
            
            # spending
            elif record.action == "spending":
                if record.source not in spend_wallets:
                    w = Wallets.query.filter(Wallets.wallet_id==record.source).first()
                    spending[record.source] = {
                        'name': w.name,
                        'type': w.type,
                        'amount': record.amount
                    }
                    spend_wallets.add(record.source)
                else:
                    spending[record.source]['amount'] += record.amount
                spending['total'] += record.amount
        
        # balance
        balance = {}
        user_wallets = Wallets.query.filter(Wallets.user_id==uid).all()
        for w in user_wallets:
            balance[w.wallet_id] = {
                'name': w.name,
                'type': w.type,
                'amount': w.amount
            }

        return {
            'income': income,
            'spending': spending,
            'balance': balance
        }


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
