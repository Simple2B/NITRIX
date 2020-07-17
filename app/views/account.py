import os

from datetime import datetime
from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required

from app.models import (
    Account,
    Product,
    Reseller,
    AccountExtension,
    AccountChanges,
    Phone,
)
from app.models import ResellerProduct
from app.forms import AccountForm
from ..database import db
from app.logger import log
from app.ninja import NinjaInvoice
from app.utils import ninja_product_name
from app.ninja import api as ninja


account_blueprint = Blueprint("account", __name__)

SIM_COST_DISCOUNT = float(os.environ.get('SIM_COST_DISCOUNT', 10)) * (-1.0)
SIM_COST_ACCOUNT_COMMENT = os.environ.get('SIM_COST_ACCOUNT_COMMENT', 'IMPORTANT! Sim cost discounted.')


def all_phones():
    phones = Phone.query.filter(Phone.deleted == False, Phone.status == Phone.Status.active).order_by(Phone.name)  # noqa E712
    all_phones = phones.all()
    all_phones = organize_list_starting_with_value(all_phones, 'None')
    return all_phones


def organize_list_starting_with_value(input_list, value):
    try:
        default_phone_value_index = input_list.index([item for item in input_list if item.name == value][0])
    except ValueError:
        return input_list
    default_value = input_list.pop(default_phone_value_index)
    input_list.insert(0, default_value)
    return input_list


@account_blueprint.route("/account_details")
@login_required
def edit():
    log(log.INFO, "/account_details")
    if "id" in request.args:
        id = int(request.args["id"])
        account = Account.query.filter(Account.id == id).first()
        if account is None:
            flash("Wrong account id.", "danger")
            log(log.ERROR, "Wrong account id.")
            return redirect(url_for("main.accounts"))
        form = AccountForm(
            id=account.id,
            name=account.name,
            product_id=account.product_id,
            phone_id=account.phone_id,
            reseller_id=account.reseller_id,
            sim=account.sim,
            imei=account.imei,
            comment=account.comment,
            activation_date=account.activation_date,
            months=account.months,
        )
        form.products = Product.query.filter(Product.deleted == False)  # noqa E712
        form.resellers = Reseller.query.filter(Reseller.deleted == False)  # noqa E712
        form.phones = all_phones()
        form.extensions = AccountExtension.query.filter(
            AccountExtension.account_id == form.id.data
        ).all()
        form.name_changes = (
            AccountChanges.query.filter(AccountChanges.account_id == form.id.data)
            .filter(AccountChanges.change_type == AccountChanges.ChangeType.name)
            .all()
        )
        form.sim_changes = (
            AccountChanges.query.filter(AccountChanges.account_id == form.id.data)
            .filter(AccountChanges.change_type == AccountChanges.ChangeType.sim)
            .all()
        )
        form.is_edit = True
        form.save_route = url_for("account.save")
        form.delete_route = url_for("account.delete")
        form.close_button = url_for("main.accounts")
        form.reseller_name = account.reseller.name
        return render_template("account_details.html", form=form)
    else:
        form = AccountForm()
        form.products = Product.query.all()
        form.resellers = organize_list_starting_with_value(Reseller.query.order_by(Reseller.name).all(), 'NITRIX')
        form.phones = all_phones()
        form.is_edit = False
        form.save_route = url_for("account.save")
        form.delete_route = url_for("account.delete")
        form.close_button = url_for("main.accounts")
        return render_template("account_details.html", form=form)


def add_ninja_invoice(account: Account, is_new: bool, mode: str):
    reseller_product = (
        ResellerProduct.query.filter(ResellerProduct.reseller_id == account.reseller_id)
        .filter(ResellerProduct.product_id == account.product_id)
        .filter(ResellerProduct.months == account.months)
        .first()
    )
    if not reseller_product:
        # Locking for this product in NITRIX reseller
        reseller_product = (
            ResellerProduct.query.filter(ResellerProduct.reseller_id == 1)
            .filter(ResellerProduct.product_id == account.product_id)
            .filter(ResellerProduct.months == account.months)
            .first()
        )
    # First day of month
    invoice_date = datetime(datetime.now().year, datetime.now().month, 1)
    invoice_date = invoice_date.strftime("%Y-%m-%d")
    current_invoice = None
    for invoice in NinjaInvoice.all():
        if (
            invoice.invoice_date == invoice_date
            and invoice.client_id == account.reseller.ninja_client_id
        ):
            # found invoice
            current_invoice = invoice
            break
    else:
        # need a new invoice
        current_invoice = NinjaInvoice.add(
            account.reseller.ninja_client_id, invoice_date
        )
    if current_invoice:
        current_invoice.add_item(
            ninja_product_name(account.product.name, account.months),
            f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}',
            cost=reseller_product.init_price if reseller_product else 0,
        )
        if is_new:
            if account.phone.name != "None":
                phone_name = f"Phone-{account.phone.name}"
                current_invoice.add_item(
                    phone_name,
                    f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}',
                    cost=account.phone.price)
            if SIM_COST_ACCOUNT_COMMENT in account.comment:
                current_invoice.add_item(
                    'SIM Cost',
                    f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}',
                    SIM_COST_DISCOUNT)


@account_blueprint.route("/account_save", methods=["POST"])
@login_required
def save():
    log(log.INFO, "/account_save")
    form = AccountForm(request.form)
    if form.validate_on_submit():
        form.name.data = form.name.data.strip()
        form.sim.data = form.sim.data.strip()
        new_account = False
        if form.id.data > 0:
            # Edit exists account
            account = Account.query.filter(Account.id == form.id.data).first()
            if account.name != form.name.data:
                # Changed account name
                change = AccountChanges(account=account)
                change.change_type = AccountChanges.ChangeType.name
                change.value_str = account.name
                change.save()
                flash(f'In account {account.name} name changed to {form.name.data}', 'info')
            if account.sim != form.sim.data:
                # Changed account SIM
                change = AccountChanges(account=account)
                change.change_type = AccountChanges.ChangeType.sim
                change.value_str = account.sim
                change.save()
                flash(f'In account {account.name} sim changed to {form.sim.data}', 'info')

            for k in request.form.keys():
                account.__setattr__(k, form.__getattribute__(k).data)
        else:
            # Add a new account
            new_account = True
            if form.sim_cost.data == 'yes':
                form.comment.data += f'\r\n\r\n{SIM_COST_ACCOUNT_COMMENT}'

            account = Account(
                name=form.name.data,
                product_id=form.product_id.data,
                reseller_id=form.reseller_id.data,
                phone_id=form.phone_id.data,
                sim=form.sim.data,
                imei=form.imei.data,
                comment=form.comment.data,
                activation_date=form.activation_date.data,
                months=form.months.data,
            )
            flash(f'Account {account.name} added', "info")
        # Check that months must be in 1-12
        if not 0 < account.months <= 12:
            flash("Months must be in 1-12", "danger")
            return redirect(url_for("account.edit", id=account.id))
        account.save()
        if new_account and ninja.configured:
            add_ninja_invoice(account, new_account, 'Activated')
        # Change Resellers last activity
        reseller = Reseller.query.filter(Reseller.id == account.reseller_id).first()
        reseller.last_activity = datetime.now()
        reseller.save()

        log(log.INFO, "Account data was saved")
        if request.form["submit"] == "save_and_add":
            return redirect(url_for("account.edit"))
        if request.form["submit"] == "save_and_edit":
            return redirect(url_for("account.edit", id=account.id))
        return redirect(url_for("main.accounts"))
    else:
        flash("Form validation error", "danger")
        log(log.ERROR, "Form validation error")
    return redirect(url_for("account.edit", id=form.id.data))


@account_blueprint.route("/account_delete", methods=["GET"])
@login_required
def delete():
    if "id" in request.args:
        account_id = int(request.args["id"])
        Account.query.filter(Account.id == account_id).delete()
        db.session.commit()
        return redirect(url_for("main.accounts"))
    flash("Wrong request", "danger")
    return redirect(url_for("main.accounts"))


@account_blueprint.route("/account_change_delete", methods=["GET"])
@login_required
def delete_change():
    log(log.INFO, "%s /account_change_delete", request.method)
    if "id" not in request.args:
        flash("Unknown Change id", "danger")
        return redirect(url_for("main.accounts"))
    account_change = AccountChanges.query.filter(
        AccountChanges.id == int(request.args["id"])
    ).first()
    account_id = account_change.account_id
    account_change.delete()
    return redirect(url_for("account.edit", id=account_id))
