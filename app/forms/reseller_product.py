from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, StringField, SubmitField
from wtforms.validators import DataRequired


class ResellerProductForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()], default=-1)
    product_id = IntegerField("product_id:", validators=[DataRequired()])
    product_name = StringField("Product:")
    reseller_id = IntegerField("Reseller:", validators=[DataRequired()])
    months = IntegerField("Months:", validators=[DataRequired()])
    init_price = FloatField("Init_Price:", validators=[DataRequired()])
    ext_price = FloatField("Ext_Price:", validators=[DataRequired()])
    submit = SubmitField("Save")
