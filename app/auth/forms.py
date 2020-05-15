from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo

from ..models import User


class LoginForm(FlaskForm):
    user_id = StringField("Name", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    submit = SubmitField("Login")
