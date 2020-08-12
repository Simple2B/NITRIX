from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask import current_app as app
from flask_login import login_required
from dateutil.relativedelta import relativedelta

from app.models import Account, AccountExtension, Product, Reseller
from app.forms import AccountExtensionForm
from app.logger import log
from app.ninja import api as ninja
from app.utils import organize_list_starting_with_value
from app.controller.account import add_ninja_invoice

account_extension_blueprint = Blueprint("account_extension", __name__)

UNKNOWN_ID = "Unknown id"
VALIDATION_ERROR = "Form validation error"


@account_extension_blueprint.route("/account_extension_add")
@login_required
def add():
    log(log.INFO, "%s /account_extension_add", request.method)
    log(log.DEBUG, "args: %s", request.args)
    if not has_valid_id(request):
        flash(UNKNOWN_ID, "danger")
        return redirect(url_for("main.accounts"))
    account_id = int(request.args["id"])
    account = Account.query.filter(Account.id == account_id).first()
    form = AccountExtensionForm(
        id=account_id,
        reseller_id=account.reseller_id,
        product_id=account.product.id,
        product=account.product.name
    )
    form.products = (
        Product.query.filter(Product.deleted == False)  # noqa E712
        .order_by(Product.name)
        .all()
    )
    form.resellers = organize_list_starting_with_value(
        Reseller.query.order_by(Reseller.name).all(), "NITRIX"
    )
    form.is_edit = False
    form.save_route = url_for("account_extension.save_new")
    form.close_button = url_for("account.edit", id=account_id)
    return render_template("account_extension.html", form=form)


@account_extension_blueprint.route("/account_extension_edit")
@login_required
def edit():
    log(log.INFO, "%s /account_extension_edit", request.method)
    log(log.DEBUG, "args: %s", request.args)
    if not has_valid_id(request):
        flash(UNKNOWN_ID, "danger")
        return redirect(url_for("main.accounts"))
    extension = AccountExtension.query.filter(
        AccountExtension.id == int(request.args["id"])
    ).first()
    if not extension:
        flash(UNKNOWN_ID, "danger")
        return redirect(url_for("main.accounts"))
    form = AccountExtensionForm(
        id=extension.id,
        product_id=extension.product_id,
        reseller_id=extension.reseller_id,
        months=extension.months,
        extension_date=extension.extension_date,
    )
    form.is_edit = True
    form.products = Product.query.filter(Product.deleted == False).all()  # noqa E712
    form.resellers = Reseller.query.filter(Reseller.deleted == False).all()  # noqa E712
    form.close_button = url_for("account.edit", id=extension.id)
    form.save_route = url_for("account_extension.save_update")
    form.delete_route = url_for("account_extension.delete")
    return render_template("account_extension.html", form=form)


@account_extension_blueprint.route("/account_ext_save_new", methods=["POST"])
@login_required
def save_new():
    log(log.INFO, "%s /account_ext_save_new", request.method)
    form = AccountExtensionForm(request.form)
    if not form.validate_on_submit():
        flash(VALIDATION_ERROR, "danger")
        log(log.WARNING, VALIDATION_ERROR, form.errors)
        return redirect(url_for("account.edit", id=form.id.data))
    account = Account.query.filter(Account.id == form.id.data).first()
    if not account:
        flash(UNKNOWN_ID, "danger")
        return redirect(url_for("main.accounts"))
    # Check that months must be in 1-12
    if not 0 < form.months.data <= 12:
        flash("Months must be in 1-12", "danger")
        return redirect(url_for("account.edit", id=account.id))
    account_ext = AccountExtension()
    account_ext.account_id = account.id
    account_ext.reseller_id = account.reseller_id
    account_ext.product_id = account.product_id
    account_ext.months = account.months
    account_ext.extension_date = account.activation_date
    m = account_ext.months if account_ext.months else 0
    account_ext.end_date = account_ext.extension_date + relativedelta(months=m)
    account_ext.save()
    account.product_id = form.product_id.data
    account.reseller_id = form.reseller_id.data
    account.months = form.months.data
    account.activation_date = form.extension_date.data
    account.save()
    account.is_new = False
    # Register product in Invoice Ninja
    if ninja.configured and not app.config["TESTING"]:
        add_ninja_invoice(account, False, "Extended")
    return redirect(url_for("account.edit", id=form.id.data))


@account_extension_blueprint.route("/account_ext_save_update", methods=["POST"])
@login_required
def save_update():
    log(log.INFO, "%s /account_ext_save_update", request.method)
    form = AccountExtensionForm(request.form)
    if not form.validate_on_submit():
        flash(VALIDATION_ERROR, "danger")
        log(log.WARNING, VALIDATION_ERROR, form.errors)
        return redirect(url_for("account.edit", id=form.id.data))
    extension = AccountExtension.query.filter(
        AccountExtension.id == form.id.data
    ).first()
    extension.reseller_id = form.reseller_id.data
    extension.product_id = form.product_id.data
    extension.months = form.months.data
    extension.extension_date = form.extension_date.data
    extension.end_date = extension.extension_date + relativedelta(
        months=extension.months
    )
    account_id = extension.account_id
    extension.save()
    return redirect(url_for("account.edit", id=account_id))


@account_extension_blueprint.route("/account_ext_delete")
@login_required
def delete():
    log(log.INFO, "%s /account_ext_delete", request.method)
    if not has_valid_id(request):
        flash(UNKNOWN_ID, "danger")
        return redirect(url_for("main.accounts"))
    extension = AccountExtension.query.filter(
        AccountExtension.id == int(request.args["id"])
    ).first()
    if not extension:
        flash(UNKNOWN_ID, "danger")
        return redirect(url_for("main.accounts"))
    account_id = extension.account_id
    extension.delete()
    return redirect(url_for("account.edit", id=account_id))


def has_valid_id(obj):
    return "id" in obj.args and obj.args.get("id").isnumeric()
