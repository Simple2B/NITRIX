from flask import render_template, Blueprint, request, flash, redirect, url_for

from app.models import Account, Product, Reseller, AccountExtension
from app.forms import AccountForm, AccountExtensionForm


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
        form.products = Product.query.all()
        form.resellers = Reseller.query.all()
        form.extensions = AccountExtension.query.filter(AccountExtension.account_id == form.id.data)
        form.is_edit = True
        form.save_route = url_for('account.save')
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
        return render_template(
                "account_details.html",
                form=form
            )


@account_blueprint.route("/account_save", methods=["POST"])
def save():
    form = AccountForm(request.form)
    if form.validate_on_submit():
        if form.id.data > 0:
            account = Account.query.filter(Account.id == form.id.data).first()
            for k in request.form.keys():
                account.__setattr__(k, form.__getattribute__(k).data)
        else:
            account = Account(name=form.name.data,
                                product_id=form.product_id.data,
                                reseller_id=form.reseller_id.data,
                                sim=form.sim.data, 
                                comment=form.comment.data, 
                                activation_date=form.activation_date.data, 
                                months=form.months.data )
        account.save()
        return redirect(url_for('main.accounts'))
    else:
        flash('Form validation error', 'danger')
    return redirect(url_for('account.edit', id=form.id.data))


@account_blueprint.route("/account_ext_add", methods=["POST"])
def ext_add():
    form = AccountExtensionForm(request.form)
    if form.validate_on_submit():
        account_ext = AccountExtension()
        account_ext.account_id = form.id.data
        account_ext.reseller_id = form.reseller_id.data
        account_ext.months = form.months.data
        account_ext.extension_date = form.extension_date.data
        account_ext.save()
        return redirect(url_for('account.edit', id=form.id.data))
    else:
        flash('Form validation error', 'danger')
    return redirect(url_for('account.edit', id=form.id.data))
