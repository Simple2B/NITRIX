from flask import render_template, Blueprint, request, flash, redirect, url_for

from app.models import Account, Product, Reseller, AccountExtension, AccountChanges
from app.forms import AccountForm, AccountExtensionForm
from ..database import db


account_blueprint = Blueprint('account', __name__)


@account_blueprint.route("/account_details")
def edit():
    if 'id' in request.args:
        id = int(request.args['id'])
        account = Account.query.filter(Account.id == id).first()
        if account is None:
            flash("Wrong account id.", "danger")
            return redirect(url_for('main.accounts'))
        form = AccountForm(
            id=account.id,
            name=account.name,
            product_id=account.product_id,
            reseller_id=account.reseller_id,
            sim=account.sim,
            comment=account.comment,
            activation_date=account.activation_date,
            months=account.months
            )
        form.products = Product.query.filter(Product.deleted == False)
        form.resellers = Reseller.query.filter(Reseller.deleted == False)
        form.extensions = AccountExtension.query.filter(AccountExtension.account_id == form.id.data)
        form.name_changes = AccountChanges.query.filter(
            AccountChanges.account_id == form.id.data).filter(AccountChanges.change_type == AccountChanges.ChangeType.name)
        form.sim_changes = AccountChanges.query.filter(
            AccountChanges.account_id == form.id.data).filter(AccountChanges.change_type == AccountChanges.ChangeType.sim)
        form.is_edit = True
        form.save_route = url_for('account.save')
        form.delete_route = url_for('account.delete')
        form.reseller_name = account.reseller.name
        return render_template(
                "account_details.html",
                form=form
            )
    else:
        form = AccountForm()
        form.products = Product.query.all()
        form.resellers = Reseller.query.all()
        form.is_edit = False
        form.save_route = url_for('account.save')
        form.delete_route = url_for('account.delete')
        return render_template(
                "account_details.html",
                form=form
            )


@account_blueprint.route("/account_save", methods=["POST"])
def save():
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
                              sim=form.sim.data,
                              comment=form.comment.data,
                              activation_date=form.activation_date.data,
                              months=form.months.data)
        account.save()
        if request.form['submit'] == 'save_and_add':
            return redirect(url_for('account.edit'))
        if request.form['submit'] == 'save_and_edit':
            return redirect(url_for('account.edit', id=account.id))
        return redirect(url_for('main.accounts'))
    else:
        flash('Form validation error', 'danger')
    return redirect(url_for('account.edit', id=form.id.data))


@account_blueprint.route("/account_ext_add", methods=["POST"])
def ext_add():
    form = AccountExtensionForm(request.form)
    if form.validate_on_submit():
        account = Account.query.filter(Account.id == form.id.data).first()
        account_ext = AccountExtension()
        account_ext.account_id = account.id
        account_ext.reseller_id = account.reseller_id
        account_ext.months = account.months
        account_ext.extension_date = account.activation_date
        account_ext.save()
        account.reseller_id = form.reseller_id.data
        account.months = form.months.data
        account.activation_date = form.extension_date.data
        account.save()
        return redirect(url_for('account.edit', id=form.id.data))
    else:
        flash('Form validation error', 'danger')
    return redirect(url_for('account.edit', id=form.id.data))


@account_blueprint.route("/account_delete", methods=["GET"])
def delete():
    if 'id' in request.args:
        account_id = int(request.args['id'])
        Account.query.filter(Account.id == account_id).delete()
        db.session.commit()
        return redirect(url_for('main.accounts'))
    flash('Wrong request', 'danger')
    return redirect(url_for('main.accounts'))
