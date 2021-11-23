from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from trkfin import db, login, app


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'< user | id:{self.id} | username:{self.username} | created:{self.created}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def user(id):
        return Users.query.filter_by(id=id).first()


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Wallets(db.Model):
    wallet_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    currency = db.Column(db.String(8))
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return str({
            'wallet': self.wallet_id,
            'user': self.user_id,
            'name': self.name,
            'type': self.type,
            'currency': self.currency,
            'amount': self.amount
        })
        # f'< wallet | uid:{self.user_id} | type:{self.type} | name:{self.name} | amount:{self.amount} >'

    def count(uid):
        return Wallets.query.filter((user_id==uid).count())
        # len(Wallets.query.filter_by(user_id=uid).all())

    def wallets(uid):
        return Wallets.query.filter_by(user_id=uid).order_by('type').all()


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    ts_utc = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)    
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
        return str({
            'user': self.user_id,
            'ts_uts': self.ts_utc,
            'ts_local': str(self.ts_year) + '-' + str(self.ts_month) + '-' + str(self.ts_day) + '_' + \
                str(self.ts_hour) + '-' + str(self.ts_minute) + '-' + str(self.ts_second) + '_' + str(self.ts_ms),
            'action': self.action,
            'from': self.source,
            'to': self.destination,
            'amount': self.amount,
            'description': self.description
        })

    def user_history(uid):
        return History.query.filter_by(user_id=uid).order_by(History.id.desc()).all()

    def month_report(uid, month):
        if len(month) is not 7:
            return False
        user = Users.query.get(int(uid))
        if not user:
            return False
        data = History.query.join(Users).filter(Users.id==uid, History.ts_year==month[0:4], History.ts_month==month[5:]).all()

        app.logger.info(data)

        inc_records = []
        inc_wallets = set()
        spend_records = []
        spend_wallets = set()
        for record in data:
            if record.action == "income":
                inc_records.append(record)
                inc_wallets.add(record.destination)
            elif record.action == "spending":
                spend_records.append(record)
                spend_wallets.add(record.source)
        
        # income
        income = {}
        for wallet in inc_wallets:
            income[wallet] = 0
            for record in inc_records:
                if record.destination == wallet:
                    income[wallet] += record.amount
        income['total'] = sum([x for x in income.values()])
        
        # spending
        spending = {}
        for wallet in spend_wallets:
            spending[wallet] = 0
            for record in spend_records:
                if record.source == wallet:
                    spending[wallet] += record.amount
        spending['total'] = sum([x for x in spending.values()])

        out = {
            'income': income,
            'spending': spending
        }

        app.logger.info(out)
        
        return out
