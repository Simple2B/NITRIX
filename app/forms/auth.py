from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    user_name = StringField("Name", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    token = StringField("OTP Token", [DataRequired(), Length(6, 6)])
    submit = SubmitField("Login")
