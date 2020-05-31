from flask import render_template, Blueprint, request, flash, redirect, url_for
from app.models import Reseller, Product, ResellerProduct
from app.forms import ResellerForm, ResellerProductForm
from app.logger import log
from app.ninja import api as ninja


reseller_blueprint = Blueprint('reseller', __name__)


def all_reseller_forms(reseller: Reseller):
    result = []
    for product in reseller.products:
        form = ResellerProductForm(
            id=product.id,
            product_id=product.product_id,
            reseller_id=product.reseller_id,
            months=product.months,
            price=product.price
            )
        result += [form]
    return result


@reseller_blueprint.route("/reseller_edit")
def edit():
    log(log.INFO, '/reseller_edit')
    if 'id' in request.args:
        id = int(request.args['id'])
        reseller = Reseller.query.filter(Reseller.id == id).first()
        if reseller is None:
            flash("Wrong account id.", "danger")
            return redirect(url_for('main.resellers'))
        form = ResellerForm(
            id=reseller.id,
            name=reseller.name,
            status=reseller.status.name,
            comments=reseller.comments
            )
        form.is_edit = True
        form.save_route = url_for('reseller.save')
        form.delete_route = url_for('reseller.delete')
        form.product_forms = all_reseller_forms(reseller)
        form.products = Product.query.filter(Product.deleted == False)  # noqa E712
        return render_template(
                "reseller_add_edit.html",
                form=form
            )
    else:
        form = ResellerForm()
        form.is_edit = False
        form.save_route = url_for('reseller.save')
        form.delete_route = url_for('reseller.delete')
        return render_template(
                "reseller_add_edit.html",
                form=form
            )


@reseller_blueprint.route("/reseller_save", methods=["POST"])
def save():
    log(log.INFO, '/reseller_save')
    form = ResellerForm(request.form)
    if form.validate_on_submit():
        if form.id.data > 0:
            reseller = Reseller.query.filter(Reseller.id == form.id.data).first()
            if reseller is None:
                flash("Wrong reseller id.", "danger")
                return redirect(url_for("main.resellers"))
            for k in request.form.keys():
                reseller.__setattr__(k, form.__getattribute__(k).data)
        else:
            ninja_client = ninja.add_client(name=form.name.data)
            ninja_client_id = ninja_client.id if ninja_client else 0
            reseller = Reseller(
                name=form.name.data,
                status=form.status.data,
                comments=form.comments.data,
                ninja_client_id=ninja_client_id)
        reseller.save()
        log(log.INFO, "Reseller was saved")
        if form.id.data > 0:
            return redirect(url_for('main.resellers'))
        return redirect(url_for('reseller.edit', id=reseller.id))
    else:
        flash('Form validation error', 'danger')
        log(log.ERROR, "Form validation error")
    return redirect(url_for('reseller.edit', id=form.id.data))


@reseller_blueprint.route("/reseller_delete", methods=["GET"])
def delete():
    if 'id' in request.args:
        reseller_id = int(request.args['id'])
        reseller = Reseller.query.filter(Reseller.id == reseller_id).first()
        reseller.deleted = True
        reseller.save()
        ninja.delete_client(client_id=reseller.ninja_client_id)
        return redirect(url_for('main.resellers'))
    flash('Wrong request', 'danger')
    return redirect(url_for('main.resellers'))


def ninja_product_name(product_name: str, months: int):
    return f'{product_name} {months} Months'


@reseller_blueprint.route("/save_reseller_product", methods=["POST"])
def save_product():
    log(log.INFO, '/save_reseller_product')
    form = ResellerProductForm(request.form)
    if form.validate_on_submit():
        if form.id.data < 0:
            # new reseller product
            log(log.INFO, 'new reseller product')
            product = ResellerProduct()
            product.reseller_id = form.reseller_id.data
        else:
            product = ResellerProduct.query.filter(ResellerProduct.id == form.id.data).first()
            if product is None:
                flash("Wrong reseller product id.", "danger")
                log(log.ERROR, "Wrong reseller product id=%d", form.id.data)
                return redirect(url_for('reseller.edit', id=form.reseller_id.data))
        product.product_id = form.product_id.data
        product.months = form.months.data
        product.price = form.price.data
        product.save()
        # Update Invoice Ninja
        product_key = ninja_product_name(product.product.name, product.months)
        if form.id.data < 0:
            ninja_product = ninja.add_product(product_key=product_key, notes=product.reseller.name, cost=product.price)
            if ninja_product:
                product.ninja_product_id = ninja_product.id
                product.save()
        else:
            ninja_product = ninja.get_product(product.ninja_product_id)
            if ninja_product:
                ninja.update_product(
                    ninja_product.id,
                    product_key=product_key,
                    notes=product.reseller.name,
                    cost=product.price)
    else:
        flash('Form validation error', 'danger')
        log(log.ERROR, "Form validation error on /save_reseller_product")
    return redirect(url_for('reseller.edit', id=form.reseller_id.data))
