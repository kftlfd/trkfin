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
    wallet_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, index=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    # currency = db.Column(db.String(8), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'< wallet | uid:{self.user_id} | type:{self.type} | name:{self.name} | amount:{self.amount} >'

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
