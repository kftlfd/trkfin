from datetime import datetime, timedelta

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from trkfin import app, db, login


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True) # no email support curently
    password_hash = db.Column(db.String(128), nullable=False)
    created = db.Column(db.Float, nullable=False) # utc-posix-timestamp
    tz_offset = db.Column(db.Integer) # no. of seconds to add to utc_ts to get users local time
    report_frequency = db.Column(db.String(5), default="month") # "month" , "week", or no. of days (>=1)
    next_report_ts = db.Column(db.Float, index=True) # utc-timestamp, timezone adjusted. Indexing for background jobs (TODO)
    email_reports = db.Column(db.Boolean, default=False) # no email support curently
    walletcount = db.Column(db.Integer)


    ###   Basics   ###

    def __init__(self, username, created, tz_offset, report_frequency="month"):
        self.username = username
        self.created = created
        self.tz_offset = tz_offset
        self.report_frequency = report_frequency
        self.walletcount = 0

    def __repr__(self):
        return f"< User id-{self.id} >"

    def export(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created": self.created,
            "tz_offset": self.tz_offset,
            "report_frequency": self.report_frequency,
            "next_report_ts": self.next_report_ts,
            "email_reports": self.email_reports,
            "walletcount": self.walletcount
        }


    ###   Password   ###

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    ###   Wallets   ###

    def get_wallets(self):
        return Wallets.query.filter_by(user_id=self.id).order_by("group").order_by("name").all()

    def get_wallets_json(self):
        wallets = self.get_wallets()
        report = {
            "wallets": {},
            "groups": {},
            "groupsize": {},
            "sums": {}
        }
        for w in wallets:
            report["wallets"][w.id] = {
                "name": w.name,
                "group": w.group,
                "balance": w.balance
            }
            if w.group not in report["groups"]:
                report["groups"][w.group] = {}
                report["groupsize"][w.group] = 0
                report["sums"][w.group] = {
                    "initial_sum": 0,
                    "income_sum": 0,
                    "spendings_sum": 0,
                    "balance_sum": 0
                }
            report["groups"][w.group][w.id] = {
                "name": w.name,
                "initial": w.initial,
                "income": w.income,
                "spendings": w.spendings,
                "transfers": w.transfers,
                "balance": w.balance
            }
            report["groupsize"][w.group] += 1
            report["sums"][w.group]["initial_sum"] += w.initial
            report["sums"][w.group]["income_sum"] += w.income
            report["sums"][w.group]["spendings_sum"] += w.spendings
            report["sums"][w.group]["balance_sum"] += w.balance
        return report


    ###   History   ###

    def get_history(self):
        return History.query.filter_by(user_id=self.id).order_by(History.id.desc()).all()

    def get_history_json(self, start=None, end=None):
        if start and end:
            history_raw = History.query.filter(History.user_id==self.id, History.ts_utc>=start, History.ts_utc<end).order_by(History.id.desc()).all()
        else:
            history_raw = self.get_history()
        history = []
        for entry in history_raw:
            history.append({
                "id": entry.id,
                "local_time": entry.local_time,
                "action": entry.action,
                "source": entry.source,
                "destination": entry.destination,
                "amount": entry.amount,
                "description": entry.description,
            })
        return history
    
    
    ###   CalcTime   ###

    def update_next_report_ts(self):
        freq = self.report_frequency
        user_time = datetime.utcnow().timestamp() + self.tz_offset
        if freq == "month":
            nextts = (datetime.fromtimestamp(user_time).replace(day=1) + timedelta(days=35))
            nextts = nextts.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            nextts = nextts.timestamp() - self.tz_offset
        elif freq == "week":
            d = datetime.fromtimestamp(user_time)
            nextts = d + timedelta(days=(7 - d.weekday()))
            nextts = nextts.replace(hour=0, minute=0, second=0, microsecond=0)
            nextts = nextts.timestamp() - self.tz_offset
        else:
            d = datetime.fromtimestamp(user_time)
            nextts = d + timedelta(days=int(freq))
            nextts = nextts.replace(hour=0, minute=0, second=0, microsecond=0)
            nextts = nextts.timestamp() - self.tz_offset
        self.next_report_ts = nextts
        return nextts


    ###   Reports   ###

    def get_reports(self):
        return Reports.query.filter(Reports.user_id==self.id).order_by(Reports.id.desc()).all()
    
    def create_new_report(self, end=None):

        new_report = Reports(self.id, self.tz_offset)

        # time start
        last_report = Reports.query.filter(Reports.user_id==self.id).order_by(Reports.id.desc()).first()
        if last_report: new_report.time_start = last_report.time_end + 0.001 # plus one milisecond = next_report_ts
        else: new_report.time_start = self.created

        # time end
        if end: new_report.time_end = end
        else: new_report.time_end = self.next_report_ts - 0.001 # minus one milisecond = previous day of next_report_ts

        # data
        new_report.wallets = self.get_wallets_json()
        new_report.history = self.get_history_json(start=new_report.time_start, end=new_report.time_end)

        # reset users wallets
        wallets = self.get_wallets()
        for w in wallets:
            w.initial = w.balance
            w.spendings = 0
            w.income = 0
            w.transfers = 0

        # update next report time
        if not end: self.update_next_report_ts()

        # write to db
        db.session.add(new_report)
        db.session.commit()


    ###   Exports   ###

    def get_export_data(self):
        u = Users.query.get(self.id)
        w = Wallets.query.filter(Wallets.user_id==self.id).all()
        h = History.query.filter(History.user_id==self.id).all()
        r = Reports.query.filter(Reports.user_id==self.id).all()
        data = {}
        data["user"] = u.export()
        data["wallets"] = [item.export() for item in w]
        data["history"] = [item.export() for item in h]
        data["reports"] = [item.export() for item in r]
        return data



@login.user_loader
def load_user(id):
    return Users.query.get(int(id))



class Wallets(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    group = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    initial = db.Column(db.Float, nullable=False)
    income = db.Column(db.Float, nullable=False)
    spendings = db.Column(db.Float, nullable=False)
    transfers = db.Column(db.Float, nullable=False)
    balance = db.Column(db.Float, nullable=False)

    def __init__(self, user_id, name, amount):
        self.user_id = user_id
        self.name = name
        self.initial = amount or 0
        self.income = 0
        self.spendings = 0
        self.transfers = 0
        self.balance = amount or 0

    def __repr__(self):
        return f"< Wallet id-{self.id} >"

    def export(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "group": self.group,
            "name": self.name,
            "initial": self.initial,
            "income": self.income,
            "spendings": self.spendings,
            "transfers": self.transfers,
            "balance": self.balance
        }




class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    ts_utc = db.Column(db.Float, nullable=False) # utc-posix-timestamp
    local_time = db.Column(db.String(19)) # user's local time in ISO format
    action = db.Column(db.String(20))
    source = db.Column(db.Integer, db.ForeignKey("wallets.id"))
    destination = db.Column(db.Integer, db.ForeignKey("wallets.id"))
    amount = db.Column(db.Float)
    description = db.Column(db.String(120))
    
    def __repr__(self):
        return f"< History id-{self.id} >"

    def export(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ts_utc": self.ts_utc,
            "local_time": self.local_time,
            "action": self.action,
            "source": self.source,
            "destination": self.destination,
            "amount": self.amount,
            "description": self.description
        }



class Reports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    time_start = db.Column(db.Float) # utc-posix-timestamp
    time_end = db.Column(db.Float) # utc-posix-timestamp
    time_tz = db.Column(db.Integer)
    wallets = db.Column(db.JSON)
    history = db.Column(db.JSON)

    def __init__(self, user_id, time_tz):
        self.user_id = user_id
        self.time_tz = time_tz
        self.data = {}

    def __repr__(self):
        return f"< Report id-{self.id} >"

    def export(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "time_start": self.time_start,
            "time_end": self.time_end,
            "time_tz": self.time_tz,
            "wallets": self.wallets,
            "history": self.history
        }
