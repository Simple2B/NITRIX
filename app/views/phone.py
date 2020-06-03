from flask import render_template, Blueprint, request, flash, redirect, url_for
from app.models import Phone
from app.forms import PhoneForm
from app.logger import log

phone_blueprint = Blueprint('phone', __name__)


@phone_blueprint.route("/phone_details")
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
def save():
    log(log.INFO, '/phone_save')
    form = PhoneForm(request.form)
    if form.validate_on_submit():
        if form.id.data > 0:
            phone = Phone.query.filter(Phone.id == form.id.data).first()
            if phone is None:
                flash("Wrong phone id.", "danger")
                return redirect(url_for('main.phones'))
            for k in request.form.keys():
                phone.__setattr__(k, form.__getattribute__(k).data)
        else:
            phone = Phone(name=form.name.data, price=form.price.data, status=form.status.data)
        phone.save()
        log(log.INFO, "Phone-{} was saved".format(phone.id))
        return redirect(url_for('main.phones'))
    else:
        flash('Form validation error', 'danger')
        log(log.WARNING, "Form validation error")
    return redirect(url_for('phone.edit', id=form.id.data))


@phone_blueprint.route("/phone_delete", methods=["GET"])
def delete():
    if 'id' in request.args:
        phone_id = int(request.args['id'])
        phone = Phone.query.filter(Phone.id == phone_id).first()
        phone.deleted = True
        phone.save()
        return redirect(url_for('main.phones'))
    flash('Wrong request', 'danger')
    return redirect(url_for('main.phones'))
