from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()])
    name = StringField("User Name:", validators=[DataRequired()])
    user_type = SelectField("User type:", validators=[DataRequired()],
                            default='user',
                            choices=[
                                    ('super_admin', 'Super Admin'),
                                    ('admin', 'Admin'),
                                    ('user', 'User')
                                    ])
    password = StringField("Password:", validators=[DataRequired()])
    activated = SelectField("Activated:", default='not_active',
                            choices=[('not_active', 'Not Active'), ('active', 'Active')])
