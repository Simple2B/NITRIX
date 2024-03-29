from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Product, ResellerProduct, HistoryChange
from app.forms import ResellerProductForm
from app.logger import log
from app.controller.reseller_product import update_reseller_product_history

reseller_product_blueprint = Blueprint("reseller_product", __name__)


@reseller_product_blueprint.route("/reseller_product_add")
@login_required
def add():
    reseller_id = int(request.args["reseller_id"])

    form = ResellerProductForm(reseller_id=reseller_id)
    form.is_edit = False
    form.save_route = url_for("reseller_product.save")
    form.close_button = url_for("reseller.edit", id=reseller_id)
    form.products = Product.query.filter(Product.deleted == False)  # noqa E712
    return render_template("reseller_product.html", form=form)


@reseller_product_blueprint.route("/reseller_product_delete", methods=["GET"])
@login_required
def delete():
    log(log.INFO, "%s /reseller_product_remove", request.method)
    if "id" not in request.args:
        flash("Unknown reseller product id", "danger")
        return redirect(url_for("main.resellers"))
    product = ResellerProduct.query.filter(
        ResellerProduct.id == int(request.args["id"])
    ).first()
    reseller_id = product.reseller_id
    product.delete()
    return redirect(url_for("reseller.edit", id=reseller_id))


@reseller_product_blueprint.route("/reseller_product_edit", methods=["GET"])
@login_required
def edit():
    log(log.INFO, "%s /reseller_product_edit", request.method)
    log(log.DEBUG, "args: %s", request.args)
    if "id" not in request.args:
        flash("Unknown reseller product id", "danger")
        return redirect(url_for("main.resellers"))
    product = ResellerProduct.query.filter(
        ResellerProduct.id == int(request.args["id"])
    ).first()
    if not product:
        flash("Wrong reseller product id", "danger")
        return redirect(url_for("main.resellers"))
    form = ResellerProductForm(
        id=product.id,
        product_id=product.product_id,
        reseller_id=product.reseller_id,
        months=product.months,
        init_price=product.init_price,
        ext_price=product.ext_price,
    )
    form.products = Product.query.filter(Product.deleted == False)  # noqa E712
    form.save_route = url_for("reseller_product.save")
    form.close_button = url_for("reseller.edit", id=product.reseller_id)
    return render_template("reseller_product.html", form=form)


@reseller_product_blueprint.route("/reseller_product_save", methods=["POST"])
@login_required
def save():
    log(log.INFO, "/reseller_product_save")
    form = ResellerProductForm(request.form)
    if not form.validate_on_submit():
        flash("Form validation error", "danger")
        log(log.WARNING, "Form validation error %s", form.errors)
        return redirect(url_for("reseller.edit", id=form.reseller_id.data))
    product = ResellerProduct.query.filter(ResellerProduct.id == form.id.data).first()
    if product:
        product.reseller_id = form.reseller_id.data
        product.product_id = form.product_id.data
        product.months = form.months.data
        product.init_price = form.init_price.data
        product.ext_price = form.ext_price.data
        # change
        update_reseller_product_history(form, product)
        product.save()
    else:
        product = (
            ResellerProduct.query.filter(
                ResellerProduct.reseller_id == form.reseller_id.data
            )
            .filter(ResellerProduct.product_id == form.product_id.data)
            .filter(ResellerProduct.months == form.months.data)
            .first()
        )
        if product:
            flash("Reseller already have this product", "danger")
            return redirect(url_for("reseller.edit", id=form.reseller_id.data))
        product = ResellerProduct(
            reseller_id=form.reseller_id.data,
            product_id=form.product_id.data,
            months=form.months.data,
            init_price=form.init_price.data,
            ext_price=form.ext_price.data,
        ).save()
        HistoryChange(
            change_type=HistoryChange.EditType.creation_reseller_product,
            item_id=product.id,
        ).save()

    return redirect(url_for("reseller.edit", id=form.reseller_id.data))
