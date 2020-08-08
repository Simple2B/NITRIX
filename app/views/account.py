from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required

from app.forms import AccountForm

from app.logger import log

from app.controller.account import AccountController


account_blueprint = Blueprint("account", __name__)


@account_blueprint.route("/account_details")
@login_required
def edit():
    log(log.INFO, "/account_details")
    controller = AccountController(request.args.get('id'))
    if controller.account:
        form = controller.account_form_edit()
        return render_template("account_details.html", form=form)
    else:
        form = controller.account_form_new(request.args.get('prev_product'), request.args.get('prev_reseller'))
        return render_template("account_details.html", form=form)


@account_blueprint.route("/account_save", methods=["POST"])
@login_required
def save():
    form = AccountForm(request.form)
    if form.validate_on_submit():
        controller = AccountController(form.id.data)
        account = controller.save(form)
        if not account:
            return redirect(url_for("account.edit", id=controller.account.id))
        if request.form["submit"] == "save_and_add":
            return redirect(
                url_for(
                    "account.edit",
                    prev_reseller=account.reseller.name,
                    prev_product=account.product.name,
                )
            )
        if request.form["submit"] == "save_and_edit":
            return redirect(url_for("account.edit", id=account.id))
        return redirect(url_for("main.accounts", id=account.id))
    else:
        flash("Form validation error", "danger")
        log(log.ERROR, "Form validation error")
    return redirect(url_for("account.edit", id=form.id.data))


@account_blueprint.route("/account_delete", methods=["GET"])
@login_required
def delete():
    controller = AccountController(request.args.get('id'))
    if controller.account:
        controller.delete()
    return redirect(url_for("main.accounts"))


@account_blueprint.route("/account_import", methods=["POST"])
@login_required
def account_import():
    ''' Provides validation for imported CSV file '''

    if request.method == "POST":
        if "csv-file" not in request.files:
            log(log.WARNING, "No file submitted in request")
            flash("File was not submitted. Please try again.", 'danger')
            return redirect(url_for("main.accounts"))
        validator = AccountController(file_object=request.files['csv-file'])
        if not validator.verify_file_integrity():
            return redirect(url_for("main.accounts"))
        if not validator.import_data_from_file():
            return redirect(url_for("main.accounts"))
    return redirect(url_for("main.accounts"))
