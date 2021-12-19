from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField, HiddenField, RadioField
from wtforms.validators import ValidationError, DataRequired, Optional, EqualTo
from wtforms.widgets.html5 import NumberInput

from trkfin.models import Users, Wallets


class AddWalletForm(FlaskForm):
    timestamp = HiddenField('timestamp')
    name = StringField('Name', validators=[DataRequired()], render_kw={'placeholder': 'Name'})
    type = SelectField('Type', validators=[Optional()], render_kw={'placeholder': 'Type'})
    type_new = StringField('Type', validators=[Optional()], render_kw={'placeholder': 'Type'})
    # currency = StringField('Currency', validators=[Optional()], render_kw={'placeholder': 'Currency'})
    amount = DecimalField('amount', default=0, validators=[Optional()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    submit = SubmitField('Add')


class MainForm(FlaskForm):
    timestamp = HiddenField('timestamp')
    action = RadioField(choices=['spending', 'income', 'transfer'], default='spending')
    source = SelectField("From", validators=[Optional()]) 
    destination = SelectField("To", validators=[Optional()])
    amount = DecimalField('amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    description = StringField('description', validators=[Optional()], render_kw={'placeholder': 'description'})
    submit = SubmitField('>')

    def validate_source(self, source):
        w = Wallets.query.get(source.data)
        if w is None:
            raise ValidationError('No such wallet')
        if w.user_id is not current_user.id:
            raise ValidationError('Wallet owned by someone else')
