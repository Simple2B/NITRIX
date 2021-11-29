from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    user_name = StringField("Name", [DataRequired(), Length(min=1, max=60)])
    password = PasswordField("Password", [DataRequired()])
    submit = SubmitField("Login")


class TwoFactorForm(FlaskForm):
    token = StringField("Enter your OTP Token", [DataRequired(), Length(min=6, max=6)])
    submit = SubmitField("Verify OTP")
