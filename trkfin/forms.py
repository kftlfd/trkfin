from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField, HiddenField, RadioField
from wtforms.validators import ValidationError, DataRequired, Optional, EqualTo
from wtforms.widgets.html5 import NumberInput

from trkfin.models import Users, Wallets


class RegistrationForm(FlaskForm):    
    username = StringField('Username', validators=[DataRequired()])    
    email = StringField('E-Mail', validators=[Optional()])    
    password = PasswordField('Password', validators=[DataRequired()])    
    confirm = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password', message="must match")])    
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is not available.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[Optional()])    
    password = PasswordField('Password', validators=[DataRequired()])    
    remember_me = BooleanField('Remember Me')    
    submit = SubmitField('Sign In')


class AddWallet(FlaskForm):
    timestamp = HiddenField('timestamp')
    name = StringField('Name', validators=[Optional()], render_kw={'placeholder': 'Name'})
    type = SelectField('Type', validators=[Optional()], render_kw={'placeholder': 'Type'})
    type_new = StringField('Type', validators=[Optional()], render_kw={'placeholder': 'Type'})
    currency = StringField('Currency', validators=[Optional()], render_kw={'placeholder': 'Currency'})
    submit = SubmitField('Add')


class MainForm(FlaskForm):
    timestamp = HiddenField('timestamp')
    action = RadioField(choices=['spending', 'income', 'transfer'], default='spending')
    source = SelectField("From", validators=[DataRequired()]) 
    destination = SelectField("To", validators=[DataRequired()])
    amount = DecimalField('amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    description = StringField('description', validators=[Optional()], render_kw={'placeholder': 'description'})
    submit = SubmitField('>')
