from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()], default=-1)
    name = StringField("Product Name:", validators=[DataRequired()])
    months = IntegerField("Available months:", validators=[DataRequired()])
    status = SelectField(
        "Status:", default='not_active',
        choices=[('not_active', 'Not Active'), ('active', 'Active')]
        )
