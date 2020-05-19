from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired
# from wtforms.widgets import CheckboxInput
from app.models import Product


class ProductForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()])
    name = StringField("Product Name:", validators=[DataRequired()])
    months = IntegerField("Available months:")
    status = SelectField(
        "Status:", default=Product.Status.not_active,
        choices=[(Product.Status.not_active, 'Not Active'), (Product.Status.active, 'Active')]
        )
