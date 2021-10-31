from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from trkfin import db, login


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True)
    created_utc = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'< user | id:{self.id} | username:{self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def user(id):
        return Users.query.filter_by(id=id).all()


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Wallets(db.Model):
    wid = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, index=True)
    wallet = db.Column(db.String(20))
    holds = db.Column(db.Float)

    def __repr__(self):
        return f'< wallets | uid:{self.user_id} | wallet:{self.wallet} | holds:{self.holds} >'

    def wallet_count(self, uid):
        return len(Wallets.query.filter_by(user_id=uid).all())

    def wallets(uid):
        return Wallets.query.filter_by(user_id=uid).all()


# class UsersHistory(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     # timestamp
#     # user_id
#     # type of transaction
#     # from category
#     # to category
#     # amount

#     def __repr__(self):
#         return f'< history >'
