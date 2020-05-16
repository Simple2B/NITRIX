from flask import render_template, Blueprint


account_blueprint = Blueprint('account', __name__)


@account_blueprint.route("/account_details")
def account_details():
    return render_template("account_details.html")
