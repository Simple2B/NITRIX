from flask import render_template, Blueprint


reseller_blueprint = Blueprint('reseller', __name__)


@reseller_blueprint.route("/reseller_add_edit")
def reseller_add_edit():
    return render_template("reseller_add_edit.html")
