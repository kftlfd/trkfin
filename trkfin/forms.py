from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, EqualTo

class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password', message="must match")])
    submit = SubmitField('Sign Up')
