from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Reseller, HistoryChange
from app.forms import ResellerForm, ResellerProductForm
from app.logger import log


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
        log(log.DEBUG, "Id: [%d]", id)
        reseller = Reseller.query.get(id)
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
            reseller = Reseller.query.get(form.id.data)
            if reseller is None:
                flash("Wrong reseller id.", "danger")
                return redirect(url_for("main.resellers"))
            HistoryChange(
                change_type=HistoryChange.EditType.changes_reseller,
                item_id=reseller.id,
                value_name="name",
                before_value_str=reseller.name,
                after_value_str=form.name.data,
            ).save()
            reseller.name = form.name.data
            reseller.save()
        else:
            # Check uniqueness of Reseller name
            if Reseller.query.filter(Reseller.name == form.name.data).first():
                flash("This name is already taken!Try again", "danger")
                return redirect(url_for("reseller.edit", id=0))
            reseller = Reseller(
                name=form.name.data,
                status=form.status.data,
                comments=form.comments.data,
            ).save()
            HistoryChange(
                change_type=HistoryChange.EditType.creation_reseller,
                item_id=reseller.id,
            ).save()
        log(log.INFO, "Reseller was saved")
        if form.id.data > 0:
            if request.form["submit"] == "save_and_edit":
                return redirect(url_for("reseller.edit", id=reseller.id))
            return redirect(url_for("main.resellers", id=reseller.id))
        return redirect(url_for("reseller.edit", id=reseller.id))
    else:
        flash("Form validation error", "danger")
        log(log.ERROR, "Form validation error [%s]", form.errors)

    return redirect(url_for("reseller.edit", id=form.id.data))


@reseller_blueprint.route("/reseller_delete", methods=["GET"])
@login_required
def delete():
    if "id" in request.args:
        reseller_id = int(request.args["id"])
        reseller = Reseller.query.get(reseller_id)
        reseller.deleted = True
        reseller.save()
        HistoryChange(
            change_type=HistoryChange.EditType.deletion_reseller,
            item_id=reseller.id,
        ).save()

        return redirect(url_for("main.resellers"))
    flash("Wrong request", "danger")
    return redirect(url_for("main.resellers"))
