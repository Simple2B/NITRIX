from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Reseller
from app.forms import ResellerForm, ResellerProductForm
from app.logger import log
from app.ninja import api as ninja


reseller_blueprint = Blueprint("reseller", __name__)


def all_reseller_forms(reseller: Reseller):
    return [
        ResellerProductForm(
            id=product.id,
            product_id=product.product_id,
            product_name=product.product.name,
            reseller_id=product.reseller_id,
            months=product.months,
            init_price=product.init_price,
            ext_price=product.ext_price,
        )
        for product in reseller.products
    ]


@reseller_blueprint.route("/reseller_edit")
@login_required
def edit():
    log(log.INFO, "/reseller_edit")
    if "id" in request.args:
        id = int(request.args["id"])
        reseller = Reseller.query.filter(Reseller.id == id).first()
        if reseller is None:
            flash("Wrong account id.", "danger")
            return redirect(url_for("main.resellers"))
        form = ResellerForm(
            id=reseller.id,
            name=reseller.name,
            status=reseller.status.name,
            comments=reseller.comments,
        )
        form.is_edit = True
        form.save_route = url_for("reseller.save")
        form.delete_route = url_for("reseller.delete")
        form.close_button = url_for("main.resellers")
        form.product_forms = all_reseller_forms(reseller)
        log(log.DEBUG, "products: %d", len(form.product_forms))
        return render_template("reseller_add_edit.html", form=form)
    else:
        form = ResellerForm()
        form.is_edit = False
        form.save_route = url_for("reseller.save")
        form.delete_route = url_for("reseller.delete")
        form.close_button = url_for("main.resellers")
        return render_template("reseller_add_edit.html", form=form)


@reseller_blueprint.route("/reseller_save", methods=["POST"])
@login_required
def save():
    log(log.INFO, "/reseller_save")
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
            reseller = Reseller(
                name=form.name.data,
                status=form.status.data,
                comments=form.comments.data,
            )
            # Check uniqueness of Reseller name
            if Reseller.query.filter(Reseller.name == reseller.name).first():
                flash("This name is already taken!Try again", "danger")
                return redirect(url_for("reseller.edit", id=reseller.id))
            ninja_client = (
                ninja.add_client(name=form.name.data) if ninja.configured else None
            )
            ninja_client_id = ninja_client.id if ninja_client else 0
            reseller = Reseller(
                name=form.name.data,
                status=form.status.data,
                comments=form.comments.data,
                ninja_client_id=ninja_client_id,
            )
        reseller.save()
        log(log.INFO, "Reseller was saved")
        if form.id.data > 0:
            if request.form["submit"] == "save_and_edit":
                return redirect(url_for("reseller.edit", id=reseller.id))
            return redirect(url_for("main.resellers", id=reseller.id))
        return redirect(url_for("reseller.edit", id=reseller.id))
    else:
        flash("Form validation error", "danger")
        log(log.ERROR, "Form validation error")
    return redirect(url_for("reseller.edit", id=form.id.data))


@reseller_blueprint.route("/reseller_delete", methods=["GET"])
@login_required
def delete():
    if "id" in request.args:
        reseller_id = int(request.args["id"])
        reseller = Reseller.query.filter(Reseller.id == reseller_id).first()
        reseller.deleted = True
        reseller.save()
        ninja.delete_client(client_id=reseller.ninja_client_id)
        return redirect(url_for("main.resellers"))
    flash("Wrong request", "danger")
    return redirect(url_for("main.resellers"))
