from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField, HiddenField, RadioField
from wtforms.validators import ValidationError, DataRequired, Optional, EqualTo
from wtforms.widgets import NumberInput

from trkfin.models import Users, Wallets


class AddWalletForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={'placeholder': 'Wallet name'})
    group = SelectField('Group', validators=[Optional()], render_kw={'placeholder': 'Wallet group'})
    group_new = StringField('Group_New', validators=[Optional()], render_kw={'placeholder': 'New group'})
    amount = DecimalField('Amount', validators=[Optional()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    submit = SubmitField('Add')


class MainForm(FlaskForm):
    action = RadioField(choices=['Spending', 'Income', 'Transfer'], default='Spending')
    source = SelectField("From", validators=[Optional()]) 
    destination = SelectField("To", validators=[Optional()])
    amount = DecimalField('Amount', validators=[DataRequired()], widget=NumberInput(min=0.0, step=0.01), render_kw={'placeholder': '0.00'})
    description = StringField('Description', validators=[Optional()], render_kw={'placeholder': 'Description'})
    submit = SubmitField('>')

    def validate_source(self, source):
        w = Wallets.query.get(source.data)
        if w is None:
            raise ValidationError('No such wallet')
        if w.user_id is not current_user.id:
            raise ValidationError('Wallet owned by someone else')
