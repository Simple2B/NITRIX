from flask import Blueprint, render_template, url_for, redirect, flash, request, session, abort
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
    log(log.INFO, '/login')
    if form.validate_on_submit():
        user = User.authenticate(form.user_name.data, form.password.data)
        if user is not None:
            session['user_name'] = form.user_name.data
            # check if user has OTP activated
            if user.otp_active:
                session['auth_status'] = True
                return redirect(url_for('auth.otp_verify'))

            # redirect to Two Factor Setup
            else:
                return redirect(url_for('auth.two_factor_warning'))
        flash("Wrong user name or password.", "danger")
        log(log.WARNING, "Invalid user data")
    return render_template("login.html", form=form)


@auth_blueprint.route('/otp_verify', methods=['GET', 'POST'])
def otp_verify():
    # check if user passed username & password verification
    if 'auth_status' not in session:
        log(log.WARNING, 'auth_status not confirmed')
        return redirect(url_for('auth.login'))
    form = TwoFactorForm()
    if form.validate_on_submit():
        user = User.query.filter(session['user_name']).first()
        if session['auth_status'] and user.verify_totp(form.token.data):
            login_user(user)

            # remove session data for added security
            del session['user_name']
            del session['auth_status']

            flash("Login successful.", "success")
            return redirect(url_for('main.index'))
        flash("Invalid OTP token", "danger")
        log(log.WARNING, "Invalid OTP token")
    return render_template('otp_form.html', form=form)


@auth_blueprint.route('/two_factor_warning')
def two_factor_warning():
    return render_template('two_factor_warning.html')


@auth_blueprint.route('/two_factor_setup')
def two_factor_setup():
    if 'user_name' not in session:
        log(log.WARNING, 'user_name not in session')
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

    # update otp status in users DB
    user.otp_active = True
    db.session.commit()

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
