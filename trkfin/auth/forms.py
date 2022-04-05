from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Optional, EqualTo, Regexp

from trkfin.models import Users

import re
pattern = "\w{1,15}"


class RegistrationForm(FlaskForm):
    tz_offset = HiddenField('timezone offset')
    username = StringField('Username', validators=[DataRequired("Username required")], render_kw={'placeholder': 'Username', "maxlength": "15", 'pattern': '\w{1,15}', "title": "Letters, numbers, underscores (_), – 1-15 characters"})
    password = PasswordField('Password', validators=[DataRequired("Password required")], render_kw={'placeholder': 'Password'})
    confirm = PasswordField('Repeat password', validators=[DataRequired("Confirm password"), EqualTo('password', message="Passwords do not match")], render_kw={'placeholder': 'Repeat Password'})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if not re.match(pattern, username.data):
            raise ValidationError('Only letters, numbers and underscores')
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is not available')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired("Username required")], render_kw={'placeholder': 'Username', "maxlength": "15", 'pattern': '\w{1,15}', "title": "Letters, numbers, underscores (_) – 1-15 characters"})
    email = StringField('E-Mail', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired("Password required")], render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate_username(self, username):
        if not re.match(pattern, username.data):
            raise ValidationError('Only letters, numbers and underscores')
        user = Users.query.filter(Users.username==self.username.data).first()
        if not user:
            raise ValidationError("Username not found")

    def validate_password(self, password):
        user = Users.query.filter(Users.username==self.username.data).first()
        if user and not user.check_password(password.data):
            raise ValidationError("Wrong password")
