from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField
from wtforms.validators import DataRequired


class AccountExtensionForm(FlaskForm):
    id = IntegerField("Account ID", validators=[DataRequired()])
    reseller_id = IntegerField("Reseller", validators=[DataRequired()])
    extension_date = DateField("Activation date", validators=[DataRequired()], default=datetime.now)
    months = IntegerField("Month", [DataRequired()])
