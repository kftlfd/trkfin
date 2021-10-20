from trkfin import db

class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True)    
    username = db.Column(db.String(64), index=True, unique=True)    
    email = db.Column(db.String(120), index=True)    
    password_hash = db.Column(db.String(128))

    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return f'<User:: id:{self.id}; username:{self.username}; email:{self.email};>'
