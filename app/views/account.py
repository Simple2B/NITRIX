import os

from datetime import datetime
from flask import render_template, Blueprint, request, flash, redirect, url_for, session
from flask_login import login_required

from app.models import (
    Account,
    Product,
    Reseller,
    AccountExtension,
    AccountChanges,
    Phone,
    ResellerProduct
)
from app.forms import AccountForm
# from ..database import db
from app.logger import log
from app.ninja import NinjaInvoice
from app.utils import ninja_product_name, organize_list_starting_with_value
from app.ninja import api as ninja


account_blueprint = Blueprint("account", __name__)

SIM_COST_DISCOUNT = float(os.environ.get('SIM_COST_DISCOUNT', 10)) * (-1.0)
SIM_COST_ACCOUNT_COMMENT = os.environ.get('SIM_COST_ACCOUNT_COMMENT', 'IMPORTANT! Sim cost discounted.')


def all_phones():
    phones = Phone.query.filter(Phone.deleted == False, Phone.status == Phone.Status.active).order_by(Phone.name)  # noqa E712
    all_phones = phones.all()
    all_phones = organize_list_starting_with_value(all_phones, 'None')
    return all_phones


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
        form.history = AccountChanges.get_history(account)
        return render_template("account_details.html", form=form)
    else:
        prev_product = None
        prev_reseller = None
        if 'prev_reseller' in request.args and 'prev_product' in request.args:
            prev_product = request.args['prev_product']
            prev_reseller = request.args['prev_reseller']
        form = AccountForm()
        form.products = organize_list_starting_with_value(
            Product
            .query
            .filter(Product.deleted == False)  # noqa E712
            .order_by(Product.name)
            .all(),
            prev_product) if prev_product else Product.query.all()
        form.resellers = organize_list_starting_with_value(
            Reseller.query.order_by(Reseller.name).all(),
            prev_reseller if prev_reseller else 'NITRIX')
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
    invoice_date = account.activation_date.date().replace(day=1).strftime("%Y-%m-%d")
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
        added_item = current_invoice.add_item(
            ninja_product_name(account.product.name, account.months),
            f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}',
            cost=reseller_product.init_price if reseller_product else 0,
        )
        if not added_item:
            log(log.ERROR, 'Could not add item to invoice in invoice Ninja!')
            return None
        if is_new:
            if account.phone.name != "None":
                phone_name = f"Phone-{account.phone.name}"
                added_item = current_invoice.add_item(
                    phone_name,
                    f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}',
                    cost=account.phone.price)
                if not added_item:
                    log(log.ERROR, 'Could not add item to invoice in invoice Ninja!')
                    return None
            if SIM_COST_ACCOUNT_COMMENT in account.comment:
                added_item = current_invoice.add_item(
                    'SIM Cost',
                    f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}',
                    SIM_COST_DISCOUNT)
                if not added_item:
                    log(log.ERROR, 'Could not add item to invoice in invoice Ninja!')
                    return None
        log(log.INFO, 'Invoice into Invoice Ninja added successfully')
        return True
    else:
        log(log.ERROR, 'Could not add invoice to Invoice Ninja!')
        return None


def document_changes_if_exist(account, form):
    if account.name != form.name.data:
        # Changed account name
        change = AccountChanges(account=account)
        change.user_id = session.get('_user_id')
        change.change_type = AccountChanges.ChangeType.name
        change.value_str = account.name
        change.new_value_str = form.name.data
        change.save()
        flash(f'In account {account.name} name changed to {form.name.data}', 'info')
    if account.sim != form.sim.data:
        # Changed account SIM
        change = AccountChanges(account=account)
        change.user_id = session.get('_user_id')
        change.change_type = AccountChanges.ChangeType.sim
        change.new_value_str = form.sim.data
        change.value_str = account.sim if account.sim else 'Empty'
        change.save()
        flash(f'In account {account.name} sim changed to {form.sim.data}', 'info')
    if account.product_id != form.product_id.data:
        # Changed account product
        new_product = Product.query.get(form.product_id.data).name
        change = AccountChanges(account=account)
        change.user_id = session.get('_user_id')
        change.change_type = AccountChanges.ChangeType.product
        change.new_value_str = new_product
        change.value_str = account.product.name
        change.save()
        flash(f'In account {account.name} product changed to {new_product}', 'info')
    if account.phone_id != form.phone_id.data:
        # Changed account phone
        new_phone = Phone.query.get(form.phone_id.data).name
        change = AccountChanges(account=account)
        change.user_id = session.get('_user_id')
        change.change_type = AccountChanges.ChangeType.phone
        change.new_value_str = new_phone
        change.value_str = account.phone.name if account.phone.name else 'Empty'
        change.save()
        flash(f'In account {account.name} phone changed to {new_phone}', 'info')
    if account.reseller_id != form.reseller_id.data:
        # Changed account reseller
        new_reseller = Reseller.query.get(form.reseller_id.data).name
        change = AccountChanges(account=account)
        change.user_id = session.get('_user_id')
        change.change_type = AccountChanges.ChangeType.reseller
        change.new_value_str = new_reseller
        change.value_str = account.reseller.name
        change.save()
        flash(f'In account {account.name} reseller changed to {new_reseller}', 'info')
    if account.activation_date.strftime("%Y-%m-%d") != form.activation_date.data.strftime("%Y-%m-%d"):
        # Changed account activation date
        change = AccountChanges(account=account)
        change.user_id = session.get('_user_id')
        change.change_type = AccountChanges.ChangeType.activation_date
        change.new_value_str = form.activation_date.data.strftime("%Y-%m-%d")
        change.value_str = account.activation_date.strftime("%Y-%m-%d")
        change.save()
        flash(
            f'In account {account.name} activation date changed to {form.activation_date.strftime("%Y-%m-%d")}',
            'info')
    if account.months != form.months.data:
        # Changed account months
        change = AccountChanges(account=account)
        change.user_id = session.get('_user_id')
        change.change_type = AccountChanges.ChangeType.months
        change.new_value_str = form.months
        change.value_str = account.months
        change.save()
        flash(f'In account {account.name} months changed to {form.months}', 'info')


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
            document_changes_if_exist(account, form)
            for k in request.form.keys():
                account.__setattr__(k, form.__getattribute__(k).data)
        else:
            # Add a new account
            if Account.query.filter(Account.name == form.name.data, Account.product_id == form.product_id.data).first():
                log(log.WARNING, "Attempt to register account with existing credentials")
                flash('Such account already exists', 'danger')
                return redirect(url_for("account.edit"))
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
        if new_account:
            change = AccountChanges(account=account)
            change.user_id = session.get('_user_id')
            change.change_type = AccountChanges.ChangeType.created
            change.new_value_str = 'Created'
            change.value_str = 'None'
            change.save()
            if ninja.configured:
                nina_api_result = add_ninja_invoice(account, new_account, 'Activated')
                if not nina_api_result:
                    log(log.ERROR, "Could not register account as invoice in Invoice Ninja!")
                    flash("WARNING! Account registration in Ninja failed!", "danger")
        # Change Resellers last activity
        reseller = Reseller.query.filter(Reseller.id == account.reseller_id).first()
        reseller.last_activity = datetime.now()
        reseller.save()

        log(log.INFO, "Account data was saved")
        if request.form["submit"] == "save_and_add":
            return redirect(
                url_for(
                    "account.edit",
                    prev_reseller=account.reseller.name,
                    prev_product=account.product.name
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
    if "id" in request.args:
        account_id = int(request.args["id"])
        account = Account.query.filter(Account.id == account_id).first()
        change = AccountChanges(account=account)
        change.user_id = session.get('_user_id')
        change.change_type = AccountChanges.ChangeType.deleted
        change.new_value_str = 'None'
        change.value_str = 'Deleted'
        change.save()
        account.delete()
        return redirect(url_for("main.accounts"))
    flash("Wrong request", "danger")
    return redirect(url_for("main.accounts"))


# @account_blueprint.route("/account_change_delete", methods=["GET"])
# @login_required
# def delete_change():
#     log(log.INFO, "%s /account_change_delete", request.method)
#     if "id" not in request.args:
#         flash("Unknown Change id", "danger")
#         return redirect(url_for("main.accounts"))
#     account_change = AccountChanges.query.filter(
#         AccountChanges.id == int(request.args["id"])
#     ).first()
#     account_id = account_change.account_id
#     account_change.delete()
#     return redirect(url_for("account.edit", id=account_id))
