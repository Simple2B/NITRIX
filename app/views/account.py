from datetime import datetime
from flask import render_template, Blueprint, request, flash, redirect, url_for

from app.models import Account, Product, Reseller


account_blueprint = Blueprint('account', __name__)


@account_blueprint.route("/account_details")
def edit():
    if 'id' in request.args:
        id = int(request.args['id'])
        account = Account.query.filter(Account.id == id).first()
        if account is None:
            flash("Wrong account id.", "danger")
            return redirect(url_for('main.accounts'))
        return render_template(
                "account_details.html",
                product=Product,
                reseller=Reseller,
                account=account,
                is_edit=True
            )
        # return render_template(
        #         "account_details.html",
        #         product=Product,
        #         reseller=Reseller,
        #         today=datetime.now(),
        #         is_edit=False
        #     )
    flash("Need account id.", "danger")
    return redirect(url_for('main.accounts'))
