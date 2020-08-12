from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect,
    flash,
    request,
    session,
    abort,
)
from flask_login import login_user, logout_user, login_required
from io import BytesIO
from app.database import db

from app.models import User
from app.forms import LoginForm, TwoFactorForm
from app.forms import ChangePasswordForm
from app.logger import log

import pyqrcode


auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    log(log.INFO, "/login")
    if form.validate_on_submit():
        log(log.INFO, "username password form validated")
        user = User.authenticate(form.user_name.data, form.password.data)
        if user is not None:
            session["id"] = user.id
            # check if user has OTP activated
            if user.otp_active:
                log(log.INFO, "redirect to otp_verify")
                return redirect(url_for("auth.otp_verify"))

            # redirect to Two Factor Setup
            else:
                log(log.INFO, "user otp_status inactive")
                return redirect(url_for("auth.two_factor_warning"))
        flash("Wrong user name or password.", "danger")
        log(log.WARNING, "Invalid user data")
    return render_template("login.html", form=form)


@auth_blueprint.route("/otp_verify", methods=["GET", "POST"])
def otp_verify():
    log(log.INFO, "/otp_verify")
    # check if user passed username & password verification
    if not session.get("id"):
        log(log.WARNING, "user auth_status not confirmed")
        flash("Please login to your account first", "danger")
        return redirect(url_for("auth.login"))
    form = TwoFactorForm(request.form)
    if form.validate_on_submit():
        log(log.INFO, "otp form validated")
        user = User.query.filter(User.id == session.get("id")).first()
        if session["id"] and user.verify_totp(form.token.data):
            log(log.INFO, "user logged in")
            login_user(user)

            # remove session data for added security
            del session["id"]

            log(log.INFO, "session cookie cleared")
            flash("Login successful.", "success")
            return redirect(url_for("main.index"))
        flash("Invalid OTP token. Try again.", "danger")
        log(log.WARNING, "Invalid OTP token")
    elif form.is_submitted():
        log(log.WARNING, "OTP form validation error")
    return render_template("otp_form.html", form=form)


@auth_blueprint.route("/two_factor_warning")
def two_factor_warning():
    log(log.INFO, "/two_factor_warning")
    return render_template("two_factor_warning.html")


@auth_blueprint.route("/two_factor_setup", methods=["GET", "POST"])
def two_factor_setup():
    log(log.INFO, "/two_factor_setup")
    form = TwoFactorForm(request.form)
    user_id = session.get("id", None)
    if user_id is None:
        log(log.WARNING, "user_name not in session")
        flash("We could not verify your credentials. Please log in first.")
        return redirect(url_for("auth.login"))
    user = User.query.filter(
        User.id == user_id, User.deleted == False  # noqa E712
    ).first()
    if not user:
        log(log.WARNING, "user not found in database.")
        flash("We could not verify your credentials. Please try loggin in first.")
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        if form.validate_on_submit() and user.verify_totp(form.token.data):
            return redirect(url_for("auth.otp_set_up_verification"))
        else:
            flash("Invalid OTP token. Please try again.", "danger")
            return redirect(url_for("auth.two_factor_setup"))
    # render QR code without caching it in browser
    return (
        render_template("two-factor-setup.html", user=user, form=form),
        200,
        {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@auth_blueprint.route("/qrcode")
def qrcode():
    if not session.get("id"):
        log(log.WARNING, "no such user id in session")
        flash("You do not have permissions to access this page.", "danger")
        return redirect(url_for("auth.login"))
    user = User.query.filter(User.id == session.get("id")).first()
    if user.otp_active:
        flash("Two-factor authentication is activated`. Please log in.", "warning")
        return redirect(url_for("auth.login"))
    if user is None:
        abort(404)
    # render qrcode for Google Authenticator
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return (
        stream.getvalue(),
        200,
        {
            "Content-Type": "image/svg+xml",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@auth_blueprint.route("/otp_set_up_verification")
def otp_set_up_verification():
    """ This route finalises 2FA process set up """
    user = User.query.filter(User.id == session.get("id")).first()
    # remove user id from session for added security
    if not user.otp_active:
        del session["id"]
        # update otp status in users DB
        user.otp_active = True
        db.session.commit()
        flash(
            "Two-Factor Authentication is set up successfully. You can now log in.",
            "success",
        )
        return redirect(url_for("auth.login"))
    flash("Two-Factor Authentication is active. Please log in.", "warning")
    return redirect(url_for("auth.login"))


@auth_blueprint.route("/logout")
@login_required
def logout():
    log(log.INFO, "/logout")
    logout_user()
    flash("You were logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_blueprint.route("/change_password", methods=["POST", "GET"])
def change_password():
    if request.method == "POST":
        user_name = request.form["user_name"]
        log(log.INFO, "User: %s change password", user_name)
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
                flash(
                    "The password cannot be plain text (add at least one figure and Capital letter).",
                    "danger",
                )
                return redirect(url_for("auth.change_password"))
        else:
            flash("Wrong data", "danger")
            log(log.WARNING, "/logout Wrong data")
            return redirect(url_for("auth.change_password"))
    else:
        log(log.INFO, "/change_password")
        form = ChangePasswordForm()
        return render_template("change_password.html", form=form)


def check_password(password):
    return not (
        len(password) < 8
        or password.isdigit()
        or password.isdigit()
        or password.isalpha()
        or password.islower()
        or password.isupper()
    )
