from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Product, HistoryChange
from app.forms import ProductForm
from app.logger import log

product_blueprint = Blueprint("product", __name__)


@product_blueprint.route("/product_details")
@login_required
def edit():
    log(log.INFO, "/product_details")
    if "id" in request.args:
        id = int(request.args["id"])
        log(log.DEBUG, "Id: [%d]", id)
        product = Product.query.get(id)
        if not product:
            flash("Wrong account id.", "danger")
            log(log.ERROR, "Invalid id")
            return redirect(url_for("main.products"))
        form = ProductForm(id=product.id, name=product.name, status=product.status.name)

        form.is_edit = True
        form.save_route = url_for("product.save")
        form.delete_route = url_for("product.delete")
        form.close_button = url_for("main.products")
        return render_template("product_add_edit.html", form=form)
    else:
        form = ProductForm()
        form.is_edit = False
        form.save_route = url_for("product.save")
        form.delete_route = url_for("product.delete")
        form.close_button = url_for("main.products")
        return render_template("product_add_edit.html", form=form)


@product_blueprint.route("/product_save", methods=["POST"])
@login_required
def save():
    log(log.INFO, "/product_save")
    form = ProductForm(request.form)
    log(log.DEBUG, "form: [%s]", form.errors)
    log(log.DEBUG, "form: [%s]", form.data)
    if form.validate_on_submit():
        if form.id.data > 0:
            product = Product.query.get(form.id.data)
            if product is None:
                flash("Wrong product id.", "danger")
                return redirect(url_for("main.products"))
            HistoryChange(
                change_type=HistoryChange.EditType.changes_product,
                item_id=product.id,
                value_name="name",
                before_value_str=product.name,
                after_value_str=form.name.data,
            ).save()
            product.name = form.name.data
            product.save()
        else:
            product = Product(name=form.name.data, status=form.status.data).save()
            HistoryChange(
                change_type=HistoryChange.EditType.creation_product,
                item_id=product.id,
            ).save()
        log(log.INFO, "Product-{} was saved".format(product.id))
        return redirect(url_for("main.products", id=product.id))
    else:
        flash("Form validation error", "danger")
        log(log.WARNING, "Form validation error")
    return redirect(url_for("product.edit", id=form.id.data))


@product_blueprint.route("/product_delete", methods=["GET"])
@login_required
def delete():
    if "id" in request.args:
        product_id = int(request.args["id"])
        product = Product.query.get(product_id)
        product.deleted = True
        product.save()
        HistoryChange(
            change_type=HistoryChange.EditType.deletion_product,
            item_id=product.id,
        ).save()
        return redirect(url_for("main.products"))
    flash("Wrong request", "danger")
    return redirect(url_for("main.products"))
