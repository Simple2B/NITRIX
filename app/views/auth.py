from flask import Blueprint, render_template, url_for, redirect, flash, request
from flask_login import login_user, logout_user, login_required

from ..models import User
from ..forms import LoginForm
from app.logger import log

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    log(log.INFO, '/login')
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.authenticate(form.user_name.data, form.password.data)
        if user is not None:
            login_user(user)
            flash("Login successful.", "success")
            return redirect(url_for("main.index"))
        flash("Wrong user name or password.", "danger")
        log(log.WARNING, "Invalid user data.")
    return render_template("login.html", form=form)


@auth_blueprint.route("/logout")
@login_required
def logout():
    log(log.DEBUG, '/logout')
    logout_user()
    flash("You were logged out.", "info")
    log(log.INFO, 'User logged out.')
    return redirect(url_for("auth.login"))
