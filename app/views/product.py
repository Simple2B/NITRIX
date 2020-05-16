from flask import render_template, Blueprint


product_blueprint = Blueprint('product', __name__)


@product_blueprint.route("/product_add_edit")
def product_add_edit():
    return render_template("product_add_edit.html")
