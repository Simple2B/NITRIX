from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class AccountForm(FlaskForm):
    id = IntegerField("id", [DataRequired()])
    name = StringField("Name", [DataRequired()])
    product_id = IntegerField("Product", [DataRequired()])
    reseller_id = IntegerField("Reseller", [DataRequired()])
    sim = StringField("SIM", [DataRequired()])
    comment = StringField("Comment", widget=TextArea())
    activation_date = DateField("Activation date", validators=[DataRequired()], default=datetime.now)
    months = IntegerField("Month", [DataRequired()])
