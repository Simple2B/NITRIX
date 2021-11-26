from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, Length


class PhoneForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()], default=-1)
    name = StringField("Model:", validators=[DataRequired(), Length(min=1, max=60)])
    price = FloatField("Price:", validators=[DataRequired()])
    status = SelectField(
        "Status:",
        default="active",
        choices=[("not_active", "Not Active"), ("active", "Active")],
    )
