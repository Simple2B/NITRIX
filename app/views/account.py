from datetime import datetime
from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required

from app.models import Account, Product, Reseller, AccountExtension, AccountChanges, Phone
from app.models import ResellerProduct
from app.forms import AccountForm
from ..database import db
from app.logger import log
from app.ninja import NinjaInvoice
from app.utils import ninja_product_name


account_blueprint = Blueprint('account', __name__)


def all_phones():
    phones = Phone.query.filter(Phone.deleted == False)  # noqa E712
    phones = phones.filter(Phone.status == Phone.Status.active)  # noqa E712
    return phones


@account_blueprint.route("/account_details")
@login_required
def edit():
    log(log.INFO, '/account_details')
    if 'id' in request.args:
        id = int(request.args['id'])
        account = Account.query.filter(Account.id == id).first()
        if account is None:
            flash("Wrong account id.", "danger")
            log(log.ERROR, 'Wrong account id.')
            return redirect(url_for('main.accounts'))
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
            months=account.months
            )
        form.products = Product.query.filter(Product.deleted == False)  # noqa E712
        form.resellers = Reseller.query.filter(Reseller.deleted == False)  # noqa E712
        form.phones = all_phones()
        form.extensions = AccountExtension.query.filter(AccountExtension.account_id == form.id.data).all()
        form.name_changes = AccountChanges.query.filter(AccountChanges.account_id == form.id.data).filter(
                AccountChanges.change_type == AccountChanges.ChangeType.name).all()
        form.sim_changes = AccountChanges.query.filter(
            AccountChanges.account_id == form.id.data).filter(
                AccountChanges.change_type == AccountChanges.ChangeType.sim).all()
        form.is_edit = True
        form.save_route = url_for('account.save')
        form.delete_route = url_for('account.delete')
        form.close_button = url_for('main.accounts')
        form.reseller_name = account.reseller.name
        return render_template(
                "account_details.html",
                form=form
            )
    else:
        form = AccountForm()
        form.products = Product.query.all()
        form.resellers = Reseller.query.all()
        form.phones = Phone.query.filter(Phone.deleted == False).filter(Phone.status == Phone.Status.active).all()  # noqa E712
        form.is_edit = False
        form.save_route = url_for('account.save')
        form.delete_route = url_for('account.delete')
        form.close_button = url_for('main.accounts')
        return render_template(
                "account_details.html",
                form=form
            )


def add_ninja_invoice(account: Account): # noqa E999
    reseller_product = ResellerProduct.query.filter(
        ResellerProduct.reseller_id == account.reseller_id
        ).filter(
            ResellerProduct.product_id == account.product_id
        ).filter(
            ResellerProduct.months == account.months
        ).first()
    if not reseller_product:
        # Locking for this product in NITRIX reseller
        reseller_product = ResellerProduct.query.filter(
            ResellerProduct.reseller_id == 1
        ).filter(
            ResellerProduct.product_id == account.product_id
        ).filter(
            ResellerProduct.months == account.months
        ).first()
    # First day of month
    invoice_date = datetime(datetime.now().year, datetime.now().month, 1)
    invoice_date = invoice_date.strftime('%Y-%m-%d')
    current_invoice = None
    for invoice in NinjaInvoice.all():
        if invoice.invoice_date == invoice_date and invoice.client_id == account.reseller.ninja_client_id:
            # found invoice
            current_invoice = invoice
            break
    else:
        # need a new invoice
        current_invoice = NinjaInvoice.add(account.reseller.ninja_client_id, invoice_date)
    if current_invoice:
        current_invoice.add_item(
            ninja_product_name(account.product.name, account.months),
            account.name,
            cost=reseller_product.init_price if reseller_product else 0)
    if account.phone.name != "None":
        phone_name = f"Phone-{account.phone.name}"
        if current_invoice:
            current_invoice.add_item(
                phone_name,
                account.name,
                cost=account.phone.price)


@account_blueprint.route("/account_save", methods=["POST"])
@login_required
def save():
    log(log.INFO, "/account_save")
    form = AccountForm(request.form)
    if form.validate_on_submit():
        form.name.data = form.name.data.strip()
        form.sim.data = form.sim.data.strip()
        if form.id.data > 0:
            # Edit exists account
            account = Account.query.filter(Account.id == form.id.data).first()
            if account.name != form.name.data:
                # Changed account name
                change = AccountChanges(account=account)
                change.change_type = AccountChanges.ChangeType.name
                change.value_str = account.name
                change.save()
            if account.sim != form.sim.data:
                # Changed account SIM
                change = AccountChanges(account=account)
                change.change_type = AccountChanges.ChangeType.sim
                change.value_str = account.sim
                change.save()

            for k in request.form.keys():
                account.__setattr__(k, form.__getattribute__(k).data)
        else:
            # Add a new account
            account = Account(name=form.name.data, product_id=form.product_id.data,
                              reseller_id=form.reseller_id.data,
                              phone_id=form.phone_id.data,
                              sim=form.sim.data,
                              imei=form.imei.data,
                              comment=form.comment.data,
                              activation_date=form.activation_date.data,
                              months=form.months.data)
        # Check that months must be in 1-12
        if not 0 < account.months <= 12:
            flash('Mohths must be in 1-12', 'danger')
            return redirect(url_for('account.edit', id=account.id))
        account.save()
        add_ninja_invoice(account)
        # Сhange Resellers last activity
        reseller = Reseller.query.filter(Reseller.id == account.reseller_id).first()
        reseller.last_activity = datetime.now()
        reseller.save()

        log(log.INFO, "Account data was saved")
        if request.form['submit'] == 'save_and_add':
            return redirect(url_for('account.edit'))
        if request.form['submit'] == 'save_and_edit':
            return redirect(url_for('account.edit', id=account.id))
        return redirect(url_for('main.accounts'))
    else:
        flash('Form validation error', 'danger')
        log(log.ERROR, "Form validation error")
    return redirect(url_for('account.edit', id=form.id.data))


@account_blueprint.route("/account_delete", methods=["GET"])
@login_required
def delete():
    if 'id' in request.args:
        account_id = int(request.args['id'])
        Account.query.filter(Account.id == account_id).delete()
        db.session.commit()
        return redirect(url_for('main.accounts'))
    flash('Wrong request', 'danger')
    return redirect(url_for('main.accounts'))
