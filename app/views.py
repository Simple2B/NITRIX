from flask import render_template, Blueprint


main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    return render_template('base.html')


@main_blueprint.route("/account_details")
def account_details():
    return render_template("account_details.html")


@main_blueprint.route("/product_add_edit")
def product_add_edit():
    return render_template("product_add_edit.html")
    

@main_blueprint.route("/reseller_add_edit")
def reseller_add_edit():
    return render_template("reseller_add_edit.html")


@main_blueprint.route("/user_edit")
def user_edit():
    return render_template("user_edit.html")


@main_blueprint.route("/accounts")
def accounts():
    return render_template("accounts.html")


@main_blueprint.route("/resellers")
def resellers():
    return render_template("reseller.html")


@main_blueprint.route("/users")
def users():
    return render_template("users.html")







