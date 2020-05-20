from flask import render_template, Blueprint, request, flash, redirect, url_for
from app.models import Reseller
from app.forms import ResellerForm


reseller_blueprint = Blueprint('reseller', __name__)


@reseller_blueprint.route("/reseller_edit")
def edit():
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
        return render_template(
                "reseller_add_edit.html",
                form=form
            )
    else:
        form = ResellerForm()
        form.is_edit = False
        form.save_route = url_for('reseller.save')
        return render_template(
                "reseller_add_edit.html",
                form=form
            )


@reseller_blueprint.route("/reseller_save", methods=["POST"])
def save():
    form = ResellerForm(request.form)
    if form.validate_on_submit():
        if form.id.data > 0:
            reseller = Reseller.query.filter(Reseller.id == form.id.data).first()
            for k in request.form.keys():
                reseller.__setattr__(k, form.__getattribute__(k).data)
        else:
            reseller = Reseller(name=form.name.data, status=form.status.data, comments=form.comments.data)
        reseller.save()
        return redirect(url_for('main.resellers'))
    else:
        flash('Form validation error', 'danger')
    return redirect(url_for('reseller.edit', id=form.id.data))
