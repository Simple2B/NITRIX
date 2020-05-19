from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired
from wtforms.widgets import CheckboxInput
from app.models import User


class UserForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()])
    name = StringField("User Name:", validators=[DataRequired()])
    user_type = SelectField("User type:", validators=[DataRequired()],
                            choices=[
                                    (User.Type.super_admin, 'Super Admin'),
                                    (User.Type.admin, 'Admin'),
                                    (User.Type.user, 'User')
                                    ])
    password = StringField("Password:", validators=[DataRequired()])
    activated = SelectField("Activated:", default=0, choices=[(0, 'Not Active'), (1, 'Active')])
