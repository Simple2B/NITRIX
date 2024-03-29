from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length


class ProductForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()], default=-1)
    name = StringField(
        "Product Name:", validators=[DataRequired(), Length(min=1, max=60)]
    )
    status = SelectField(
        "Status:",
        default="active",
        choices=[("not_active", "Not Active"), ("active", "Active")],
    )
