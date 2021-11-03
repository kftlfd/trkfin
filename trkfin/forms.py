from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField
from wtforms.validators import ValidationError, DataRequired, Optional, EqualTo
from wtforms.widgets.html5 import NumberInput

from trkfin.models import Users, Wallets


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
            raise ValidationError('Username is not available.')


class FormSpending(FlaskForm):
    sp_ts = "timestamp"        
    sp_source = SelectField("Source", validators=[DataRequired()])
    sp_amount = DecimalField('Amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})    
    sp_description = StringField('Description', validators=[Optional()], render_kw={'placeholder': 'description'})    
    sp_submit = SubmitField('>') #, id='submit-spending'


class FormIncome(FlaskForm):
    inc_ts = "timestamp"        
    inc_destination = SelectField("Destination", validators=[DataRequired()])
    inc_amount = DecimalField('Amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})    
    inc_description = StringField('Description', validators=[Optional()], render_kw={'placeholder': 'description'})
    inc_submit = SubmitField('Submit') #, id='submit-income'


class FormTransfer(FlaskForm):
    tr_ts = "timestamp"
    tr_source = SelectField("From", validators=[DataRequired()])
    tr_destination = SelectField("To", validators=[DataRequired()])
    tr_amount = DecimalField('Amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    tr_description = StringField('Description', validators=[Optional()], render_kw={'placeholder': 'description'})    
    tr_submit = SubmitField('Submit')

class AddWallet(FlaskForm):
    aw_ts = "timestamp"
    name = StringField('Name', validators=[Optional()], render_kw={'placeholder': 'Name, e.g.: "Cash"'})
    type = StringField('Type', validators=[Optional()], render_kw={'placeholder': 'Type, e.g.: "On hand", "Savings"'})
    submit = SubmitField('Add')