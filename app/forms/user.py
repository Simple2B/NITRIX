from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length


class UserForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()], default=-1)
    name = StringField("User Name:", validators=[DataRequired(), Length(min=1, max=60)])
    user_type = SelectField(
        "User type:",
        default="user",
        choices=[("super_admin", "Super Admin"), ("admin", "Admin"), ("user", "User")],
    )
    password = StringField("Password:", validators=[DataRequired()])
    activated = SelectField(
        "Activated:",
        default="active",
        choices=[("not_active", "Not Active"), ("active", "Active")],
    )
