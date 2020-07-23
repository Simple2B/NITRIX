from flask import Blueprint, render_template, url_for, redirect, flash, request, session, abort
from flask_login import login_user, logout_user, login_required
from io import BytesIO

from app.models import User
from app.forms import LoginForm
from app.forms import ChangePasswordForm
from app.logger import log

import pyqrcode

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    log(log.INFO, '/login')
    if form.validate_on_submit():
        # check if user has active two-factor auth
        user = User.query.filter(form.user_name.data).first()
        if not user.otp_active:
            # pass corresponding user_name with redirect
            session['user_name'] = user.user_name
            return redirect(url_for('auth.two_factor_setup'))
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
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(user_name=session['user_name']).first()
    if user is None:
        return redirect(url_for('auth.login'))
    # render QR code without caching it in browser
    return render_template('two-factor-setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@auth_blueprint.route('/qrcode')
def qrcode():
    if 'user_name' not in session:
        abort(404)
    user = User.query.filter_by(user_name=session['user_name']).first()
    if user is None:
        abort(404)

    # remove user_name from session for added security
    del session['user_name']

    # render qrcode for Google Authenticator
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


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
