from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired


class ResellerProductForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()], default=-1)
    product_id = IntegerField("Product:", validators=[DataRequired()])
    reseller_id = IntegerField("Reseller:", validators=[DataRequired()])
    months = IntegerField("Months:", validators=[DataRequired()])
    price = FloatField("Price:", validators=[DataRequired()])
    submit = SubmitField("Save")
