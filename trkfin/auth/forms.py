from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Optional, EqualTo

from trkfin.models import Users


class RegistrationForm(FlaskForm):
    timestamp = HiddenField('timestamp')
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