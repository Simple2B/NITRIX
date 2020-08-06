from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired


class PhoneForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()], default=-1)
    name = StringField("Model:", validators=[DataRequired()])
    price = FloatField("Price:", validators=[DataRequired()])
    status = SelectField(
        "Status:",
        default="active",
        choices=[("not_active", "Not Active"), ("active", "Active")],
    )
