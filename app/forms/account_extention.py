from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField
from wtforms.validators import DataRequired


class AccountExtensionForm(FlaskForm):
    id = IntegerField("Extension ID", validators=[DataRequired()])
    reseller_id = IntegerField("Reseller", validators=[DataRequired()])
    extension_date = DateField("Extension date", validators=[DataRequired()], default=datetime.now)
    months = IntegerField("Month", [DataRequired()])
    product_id = IntegerField("Product", validators=[DataRequired()])
