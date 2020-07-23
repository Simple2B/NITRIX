from flask import Blueprint, render_template, url_for, redirect, flash, request
from flask_login import login_user, logout_user, login_required

from app.models import User
from app.forms import LoginForm
from app.forms import ChangePasswordForm
from app.logger import log

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    log(log.INFO, '/login')
    if form.validate_on_submit():
        # check if user has active two-factor auth
        user = User.query.filter(form.user_name.data).first()
        if not user.otp_active:
            return 'Set up Two Factor Authentication first.'
        user = User.authenticate(form.user_name.data, form.password.data)
        if user is not None:
            if user.verify_totp(form.token.data):
                login_user(user)
                flash("Login successful.", "success")
                return redirect(url_for("main.index"))
            else:
                flash("Your OTP password is invalid. Please try again.", "danger")
                log(log.WARNING, "Invalid OTP token")
        flash("Wrong user name or password.", "danger")
        log(log.WARNING, "Invalid user data")
    return render_template("login.html", form=form)


@auth_blueprint.route('/two_factor_setup')
def two_factor_setup():
    pass

@auth_blueprint.route("/logout")
@login_required
def logout():
    log(log.INFO, '/logout')
    logout_user()
    flash("You were logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_blueprint.route("/change_password", methods=["POST", "GET"])
def change_password():
    if request.method == "POST":
        user_name = request.form["user_name"]
        log(log.INFO, 'User: %s change password', user_name)
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        repeat_new_password = request.form["repeat_new_password"]

        if new_password != repeat_new_password:
            flash("Wrong user name or password.", "danger")
            return redirect(url_for("auth.change_password"))

        user = User.authenticate(user_name, old_password)
        if user is not None:
            if check_password(new_password):
                user.password = new_password
                user.save()
                flash("Password change was successful.", "success")
                return redirect(url_for("auth.login"))
            else:
                flash("The password cannot be plain text (add at least one figure and Capital letter).", "danger")
                return redirect(url_for("auth.change_password"))
        else:
            flash("Wrong data", "danger")
            log(log.WARNING, '/logout Wrong data')
            return redirect(url_for("auth.change_password"))
    else:
        log(log.INFO, '/change_password')
        form = ChangePasswordForm()
        return render_template("change_password.html", form=form)


def check_password(password):
    return not(len(password) < 8 or password.isdigit() or password.isdigit()
               or password.isalpha() or password.islower() or password.isupper())
