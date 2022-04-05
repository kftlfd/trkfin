from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField, HiddenField, RadioField
from wtforms.validators import ValidationError, DataRequired, Optional, EqualTo
from wtforms.widgets import NumberInput

from trkfin.models import Users, Wallets

import re
pattern = "[\w\s()-]{1,20}"

class AddWalletForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={'placeholder': 'Wallet name', "maxlength": "20", 'pattern': '[\w\s()-]{1,20}', 'title': 'Letters, numbers, brackets (), undersores (_) and hypens (-), up to 20 characters'})
    group = SelectField('Group', validators=[Optional()], render_kw={'placeholder': 'Wallet group'})
    group_new = StringField('Group_New', validators=[Optional()], render_kw={'placeholder': 'New group', "maxlength": "20", 'pattern': '[\w\s()-]{1,20}', 'title': 'Letters, numbers, brackets (), undersores (_) and hypens (-), up to 20 characters'})
    amount = DecimalField('Amount', validators=[Optional()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    submit = SubmitField('Add')

    def validate_name(self, name):
        if not re.match(pattern, name.data):
            raise ValidationError('Wrong format')

    def validate_group_new(self, group_new):
        if not re.match(pattern, group_new.data):
            raise ValidationError('Wrong format')


class MainForm(FlaskForm):
    action = RadioField(choices=['Spending', 'Income', 'Transfer'], default='Spending')
    source = SelectField("From", validators=[Optional()]) 
    destination = SelectField("To", validators=[Optional()])
    amount = DecimalField('Amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    description = StringField('Description', validators=[Optional()], render_kw={'placeholder': 'Description', "maxlength": "50"})
    submit = SubmitField('>')

    def validate_source(self, source):
        w = Wallets.query.get(source.data)
        if w is None:
            raise ValidationError('No such wallet')
        if w.user_id is not current_user.id:
            raise ValidationError('Wallet owned by someone else')
    
    def validate_destination(self, destination):
        w = Wallets.query.get(destination.data)
        if w is None:
            raise ValidationError('No such wallet')
        if w.user_id is not current_user.id:
            raise ValidationError('Wallet owned by someone else')
