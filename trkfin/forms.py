from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Optional, EqualTo

from trkfin.models import Users


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
    source = StringField("Source")
    amount = FloatField('Amount')
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Submit')


class FormIncome(FlaskForm):

    ts = ""
    action = "income"
    # to
    # amount
    description = StringField('Description', validators=[Optional()], id="descr_inc")
    submit = SubmitField('Submit')


class FormTransfer(FlaskForm):

    ts = ""
    action = "transfer"
    # from
    # to
    description = StringField('Description', validators=[Optional()], id="descr_tr")
    submit = SubmitField('Submit')