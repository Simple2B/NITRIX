from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Product, ResellerProduct
from app.forms import ResellerProductForm
from app.logger import log
# from app.ninja import api as ninja
# from app.utils import ninja_product_name


reseller_product_blueprint = Blueprint('reseller_product', __name__)


@reseller_product_blueprint.route("/reseller_product_add")
@login_required
def add():
    reseller_id = int(request.args['reseller_id'])

    form = ResellerProductForm(
        reseller_id=reseller_id
        )
    form.is_edit = False
    form.save_route = url_for('reseller_product.save')
    form.products = Product.query.filter(Product.deleted == False)  # noqa E712
    # form.delete_route = url_for('reseller_product.delete')
    form.products = Product.query.filter(Product.deleted == False)  # noqa E712
    return render_template(
            "reseller_product.html",
            form=form
        )


@reseller_product_blueprint.route("/reseller_product_edit", methods=["POST"])
@login_required
def edit():
    log(log.INFO, '/reseller_product_edit')
    form = ResellerProductForm(request.form)
    if not form.validate_on_submit():
        flash('Form validation error', 'danger')
        log(log.WARNING, "Form validation error")
        return redirect(url_for('reseller.edit', id=form.reseller_id))
    return render_template(
            "reseller_add_product.html",
            form=form
        )


@reseller_product_blueprint.route("/reseller_product_save", methods=["POST"])
@login_required
def save():
    log(log.INFO, '/reseller_product_save')
    form = ResellerProductForm(request.form)
    if not form.validate_on_submit():
        flash('Form validation error', 'danger')
        log(log.WARNING, "Form validation error %s", form.errors)
        return redirect(url_for('reseller.edit', id=form.reseller_id.data))
        # TODO: need check if same product already exists (with same product_id and months)
    ResellerProduct(
        reseller_id=form.product_id.data,
        product_id=form.product_id.data,
        months=form.months.data,
        init_price=form.init_price.data,
        ext_price=form.ext_price.data).save()
    return redirect(url_for('reseller.edit', id=form.reseller_id.data))
