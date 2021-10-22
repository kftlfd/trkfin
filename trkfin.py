from trkfin import app, db
from trkfin.models import Users


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Users': Users}
