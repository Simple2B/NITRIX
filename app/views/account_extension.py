from flask import Blueprint, request, flash, redirect, url_for
from flask_login import login_required

from app.models import Account, AccountExtension
from app.forms import AccountExtensionForm
# from views.account import add_ninja_invoice


account_extension_blueprint = Blueprint('account_extension', __name__)


# For account extesion views
@account_extension_blueprint.route("/account_ext_add", methods=["POST"])
@login_required
def ext_save():
    form = AccountExtensionForm(request.form)
    if form.validate_on_submit():
        account = Account.query.filter(Account.id == request.form['account_id']).first()
        # add new Account Extension
        if form.id.data < 0:
            account_ext = AccountExtension()
            account_ext.account_id = account.id
            account_ext.reseller_id = account.reseller_id
            account_ext.months = account.months
            account_ext.extension_date = account.activation_date
            account_ext.save()
            account.reseller_id = form.reseller_id.data
            account.months = form.months.data
            # Check that months must be in 1-12
            if not 0 < account.months <= 12:
                flash('Mohths must be in 1-12', 'danger')
                return redirect(url_for('account.edit', id=account.id))
            account.activation_date = form.extension_date.data
            account.save()
            # Register product in Invoice Ninja
            # add_ninja_invoice(account)
        else:
            account_ext = AccountExtension.query.filter(AccountExtension.id == form.id.data).first()
            if request.form['action'] == 'delete':  # delete AccountExtension
                account_ext.delete()
            else:
                #  Update AccountExtension
                account_ext.reseller_id = form.reseller_id.data
                account_ext.months = form.months.data
                account_ext.extension_date = form.extension_date.data
                # Check that months must be in 1-12
                if not 0 < account_ext.months <= 12:
                    flash('Mohths must be in 1-12', 'danger')
                    return redirect(url_for('account.edit', id=account.id))
                account_ext.save()

        return redirect(url_for('account.edit', id=request.form['account_id']))
    else:
        flash('Form validation error', 'danger')
    return redirect(url_for('account.edit', id=request.form['account_id']))
