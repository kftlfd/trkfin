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
            raise ValidationError('Username is not available.')


class FormSpending(FlaskForm):

    sp_ts = "timestamp"    

    srcs = []
    for key, value in tdSources.items():
        srcs.append(key)
    sp_source = SelectField("Source", validators=[DataRequired()], choices=srcs)

    sp_amount = DecimalField('Amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    
    sp_description = StringField('Description', validators=[Optional()], render_kw={'placeholder': 'description'})
    
    sp_submit = SubmitField('Submit') #, id='submit-spending'


class FormIncome(FlaskForm):

    inc_ts = "timestamp"
    
    srcs = []
    for key, value in tdSources.items():
        srcs.append(key)
    inc_destination = SelectField("Destination", validators=[DataRequired()], choices=srcs)

    inc_amount = DecimalField('Amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    
    inc_description = StringField('Description', validators=[Optional()], render_kw={'placeholder': 'description'})

    inc_submit = SubmitField('Submit') #, id='submit-income'


class FormTransfer(FlaskForm):

    tr_ts = "timestamp"
    
    srcs = []
    for key, value in tdSources.items():
        srcs.append(key)

    tr_source = SelectField("From", validators=[DataRequired()], choices=srcs)

    tr_destination = SelectField("To", validators=[DataRequired()], choices=srcs)

    tr_amount = DecimalField('Amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})

    tr_description = StringField('Description', validators=[Optional()], render_kw={'placeholder': 'description'})
    
    tr_submit = SubmitField('Submit')
