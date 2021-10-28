from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField
from wtforms.validators import ValidationError, DataRequired, Optional, EqualTo
from wtforms.widgets.html5 import NumberInput

from trkfin.models import Users

tdSources = {
    'cash': 0,
    'card': 0,
}


class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password', message="must match")])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')


class FormSpending(FlaskForm):

    ts = ""
    action = "spending"
    
    srcs = []
    for key, value in tdSources.items():
        srcs.append(key)
    source_sp = SelectField("Source", validators=[DataRequired()], choices=srcs)

    amount_sp = DecimalField('Amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    
    description_sp = StringField('Description', validators=[Optional()], render_kw={'placeholder': 'description'})
    
    submit_sp = SubmitField('Submit', id='submit-spending')

    def __repr__(self):
        return f'<SP | {self.ts} | {self.action} | {self.source_sp} | {self.amount_sp} | {self.description_sp}>'


class FormIncome(FlaskForm):

    ts = ""
    action = "income"
    
    srcs = []
    for key, value in tdSources.items():
        srcs.append(key)
    destination_inc = SelectField("Destination", validators=[DataRequired()], choices=srcs)

    amount_inc = DecimalField('Amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    
    description_inc = StringField('Description', validators=[Optional()], id="descr_inc", render_kw={'placeholder': 'description'})

    submit_inc = SubmitField('Submit', id='submit-income')


class FormTransfer(FlaskForm):

    ts = ""
    action = "transfer"
    # from
    # to
    description = StringField('Description', validators=[Optional()], id="descr_tr")
    submit = SubmitField('Submit')