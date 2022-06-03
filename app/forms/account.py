from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import TextArea


class AccountForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()], default=-1)
    name = StringField("Name:", validators=[DataRequired(), Length(min=1, max=60)])
    product_id = IntegerField("Product", validators=[DataRequired()])
    phone_id = IntegerField("Phone", validators=[DataRequired()])
    reseller_id = IntegerField("Reseller", validators=[DataRequired()])
    sim = StringField("SIM", [DataRequired(), Length(min=1, max=20)])
    sim_cost = SelectField(
        "Sim Cost:", default="no", choices=[("yes", "Yes"), ("no", "No")]
    )
    imei = StringField("IMEI", validators=[Length(min=0, max=60)])
    comment = StringField(
        "Comment", validators=[Length(min=0, max=256)], widget=TextArea()
    )
    activation_date = DateField(
        "Activation date", validators=[DataRequired()], default=datetime.now
    )
    extension_date = DateField(
        "Extensions date", validators=[DataRequired()], default=datetime.now
    )
    months = IntegerField("Month", [DataRequired()])
    submit = SubmitField("Save")
