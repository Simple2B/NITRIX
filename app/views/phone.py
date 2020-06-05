from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Phone
from app.forms import PhoneForm
from app.logger import log
from app.ninja import api as ninja


phone_blueprint = Blueprint('phone', __name__)


@phone_blueprint.route("/phone_details")
@login_required
def edit():
    log(log.INFO, '/phone_details')
    if 'id' in request.args:
        id = int(request.args['id'])
        phone = Phone.query.filter(Phone.id == id).first()
        if phone is None:
            flash("Wrong phone id.", "danger")
            log(log.WARNING, "Invalid id")
            return redirect(url_for('main.phones'))
        form = PhoneForm(
            id=phone.id,
            name=phone.name,
            price=phone.price,
            status=phone.status.name
            )

        form.is_edit = True
        form.save_route = url_for('phone.save')
        form.delete_route = url_for('phone.delete')
        return render_template(
                "phone_add_edit.html",
                form=form
            )
    else:
        form = PhoneForm()
        form.is_edit = False
        form.save_route = url_for('phone.save')
        form.delete_route = url_for('phone.delete')
        return render_template(
                "phone_add_edit.html",
                form=form
            )


@phone_blueprint.route("/phone_save", methods=["POST"])
@login_required
def save():
    log(log.INFO, '/phone_save')
    form = PhoneForm(request.form)
    if form.validate_on_submit():
        # If we have this name in database
        if Phone.query.filter(Phone.name == form.name.data).first():
            phone = Phone.query.filter(Phone.name == form.name.data).first()
            phone.delete = False

        if form.id.data > 0:
            phone = Phone.query.filter(Phone.id == form.id.data).first()
            if phone is None:
                flash("Wrong phone id.", "danger")
                return redirect(url_for('main.phones'))
            for k in request.form.keys():
                phone.__setattr__(k, form.__getattribute__(k).data)
        else:
            phone = Phone(name=form.name.data, price=form.price.data, status=form.status.data)
            # Check uniqueness Phone name
            if Phone.query.filter(Phone.name == phone.name).first():
                flash('This name is already taken!Try again', 'danger')
                return redirect(url_for('phone.edit', id=phone.id))
        phone.save()
        # Update Invoice Ninja
        product_key = f"Phone-{phone.name}"  # noqa E999
        if form.id.data < 0:
            ninja_product = ninja.add_product(product_key=product_key, notes="Phone", cost=phone.price)
            if ninja_product:
                phone.ninja_product_id = ninja_product.id
                phone.save()
        else:
            ninja_product = ninja.get_product(phone.ninja_product_id)
            if ninja_product:
                ninja.update_product(
                    ninja_product.id,
                    product_key=product_key,
                    notes="Price",
                    cost=phone.price)
        log(log.INFO, "Phone-{} was saved".format(phone.id))
        return redirect(url_for('main.phones'))
    else:
        flash('Form validation error', 'danger')
        log(log.WARNING, "Form validation error")
    return redirect(url_for('phone.edit', id=form.id.data))


@phone_blueprint.route("/phone_delete", methods=["GET"])
@login_required
def delete():
    if 'id' in request.args:
        phone_id = int(request.args['id'])
        phone = Phone.query.filter(Phone.id == phone_id).first()
        phone.deleted = True
        phone.save()
        # Delete in Invoice Ninja
        ninja_product = ninja.get_product(phone.ninja_product_id)
        ninja.delete_product(ninja_product.id, ninja_product.product_key)
        phone.delete()
        return redirect(url_for('main.phones'))
    flash('Wrong request', 'danger')
    return redirect(url_for('main.phones'))
