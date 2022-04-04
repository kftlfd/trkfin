from trkfin import app, db
from trkfin.models import Users, Wallets, History, Reports


# doesn't work, no idea why. FLASK_APP is set correctly
@app.shell_context_processor
def make_shell_context():
    symbols = {
        'db': db,
        'Users': Users,
        'Wallets': Wallets,
        'History': History,
        'Reports': Reports
        }
    return symbols
