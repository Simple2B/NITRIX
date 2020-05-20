from flask import render_template, Blueprint, request, flash, redirect, url_for
from app.models import Product
from app.forms import ProductForm


product_blueprint = Blueprint('product', __name__)


@product_blueprint.route("/product_details")
def edit():
    if 'id' in request.args:
        id = int(request.args['id'])
        product = Product.query.filter(Product.id == id).first()
        if product is None:
            flash("Wrong account id.", "danger")
            return redirect(url_for('main.products'))
        form = ProductForm(
            id=product.id,
            name=product.name,
            months=product.months,
            status=product.status.name
            )

        form.is_edit = True
        form.save_route = url_for('product.save')
        return render_template(
                "product_add_edit.html",
                form=form
           )
    else:
        form = ProductForm()
        form.is_edit = False
        form.save_route = url_for('product.save')
        return render_template(
                "product_add_edit.html",
                form=form
            )


@product_blueprint.route("/product_save", methods=["POST"])
def save():
    form = ProductForm(request.form)
    if form.validate_on_submit():
        if form.id.data > 0:
            product = Product.query.filter(Product.id == form.id.data).first()
            for k in request.form.keys():
                product.__setattr__(k, form.__getattribute__(k).data)
        else:
            product = Product(name=form.name.data, months=form.months.data, status=form.status.data)
        product.save()
        return redirect(url_for('main.products'))
    else:
        flash('Form validation error', 'danger')
    return redirect(url_for('product.edit', id=form.id.data))
