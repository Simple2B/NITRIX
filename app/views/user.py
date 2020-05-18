from flask import render_template, Blueprint


user_blueprint = Blueprint('user', __name__)


@user_blueprint.route("/user_edit")
def edit():
    return render_template("user_edit.html")
