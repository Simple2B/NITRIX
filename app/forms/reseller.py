from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class ResellerForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()], default=-1)
    name = StringField("Name:", validators=[DataRequired()])
    status = SelectField("Activated:", default='active',
                         choices=[('not_active', 'Not Active'), ('active', 'Active')])
    comments = StringField("Comment:", widget=TextArea())
    submit = SubmitField("Save")
