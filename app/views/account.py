from flask import render_template, Blueprint, request, flash, redirect, url_for

from app.models import Account, Product, Reseller
from app.forms import AccountForm
from app.logger import log

account_blueprint = Blueprint('account', __name__)


@account_blueprint.route("/account_details")
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
            reseller_id=account.reseller_id,
            sim=account.sim,
            comment=account.comment,
            activation_date=account.activation_date,
            months=account.months
            )
        form.products = Product.query.all()
        form.resellers = Reseller.query.all()
        form.is_edit = True
        form.save_route = url_for('account.save')
        return render_template(
                "account_details.html",
                form=form
            )
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
    log(log.INFO, "/account_save")
    form = AccountForm(request.form)
    if form.validate_on_submit():
        account = Account.query.filter(Account.id == form.id.data).first()
        for k in request.form.keys():
            account.__setattr__(k, form.__getattribute__(k).data)
        account.save()
        log(log.INFO, "Account data was saved")
        return redirect(url_for('main.accounts'))
    else:
        flash('Form validation error', 'danger')
        log(log.ERROR, "Form validation error")
    return redirect(url_for('account.edit', id=form.id.data))
