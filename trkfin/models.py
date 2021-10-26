from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from trkfin import db, login


class Users(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True)
    created_utc = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    # categories

    def __repr__(self):
        return f'< user | id:{self.id} | username:{self.username} | email:{self.email} >'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))


class UserStuff(db.Model):

    # user_id
    # category
    # amount

    def __repr__(self):
        return "stuff"


class UsersHistory(db.Model):

    # timestamp
    # user_id
    # type of transaction
    # from category
    # to category
    # amount

    def __repr__(self):
        return "history"