from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class ChangePasswordForm(FlaskForm):
    user_name = StringField("Name", [DataRequired()])
    old_password = PasswordField("Old password", [DataRequired()])
    new_password = PasswordField("New password", [DataRequired()])
    repeat_new_password = PasswordField("Repeat new password", [DataRequired()])
