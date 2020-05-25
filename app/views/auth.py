from flask import Blueprint, render_template, url_for, redirect, flash, request
from flask_login import login_user, logout_user, login_required

from ..models import User
from ..forms import LoginForm
from ..forms import ChangePasswordForm

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.authenticate(form.user_name.data, form.password.data)
        if user is not None:
            login_user(user)
            flash("Login successful.", "success")
            return redirect(url_for("main.index"))
        flash("Wrong user name or password.", "danger")
    return render_template("login.html", form=form)


@auth_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_blueprint.route("/change_password", methods=["POST", "GET"])
def change_password():
    if request.method == "POST":
        user_name = request.form["user_name"]
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        reapet_new_password = request.form["reapet_new_password"]

        if new_password != reapet_new_password:
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
            return redirect(url_for("auth.change_password"))
    else:
        form = ChangePasswordForm()
        return render_template("change_password.html", form=form)


def check_password(password):
    return not(len(password) < 8 or password.isdigit() or password.isdigit()
               or password.isalpha() or password.islower() or password.isupper())
