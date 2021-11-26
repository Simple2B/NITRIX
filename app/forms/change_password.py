from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo


class ChangePasswordForm(FlaskForm):
    user_name = StringField("Name", [DataRequired(), Length(min=1, max=60)])
    old_password = PasswordField("Old password", [DataRequired()])
    new_password = PasswordField("New password", [DataRequired()])
    repeat_new_password = PasswordField(
        "Repeat new password", [DataRequired(), EqualTo("new_password")]
    )
