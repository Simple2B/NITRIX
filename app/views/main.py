from flask import render_template, Blueprint, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Product, Account, Reseller
from ..logger import log

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
@login_required
def index():
    if current_user.user_type in ('super_user', 'admin'):
        return redirect(url_for("main.users"))
    return redirect(url_for("main.accounts"))


@main_blueprint.route('/accounts')
@login_required
def accounts():
    log(log.DEBUG, '/accounts')
    return render_template(
        'index.html',
        main_content='Accounts',
        table_data=[acc.to_dict() for acc in Account.query.all()],
        columns=Account.columns(),
        edit_href=url_for('account.edit'))


@main_blueprint.route('/users')
@login_required
def users():
    log(log.DEBUG, '/users')
    return render_template(
        'index.html',
        main_content='Users',
        table_data=[u.to_dict() for u in User.query.all()],
        columns=User.columns(),
        edit_href=url_for('user.edit'))


@main_blueprint.route('/resellers')
@login_required
def resellers():
    log(log.DEBUG, '/resellers')
    return render_template(
        'index.html',
        main_content='Resellers',
        table_data=[i.to_dict() for i in Reseller.query.all()],
        columns=Reseller.columns(),
        edit_href=url_for('reseller.edit'))


@main_blueprint.route('/products')
@login_required
def products():
    return render_template(
        'index.html',
        main_content='Products',
        table_data=[p.to_dict() for p in Product.query.all()],
        columns=Product.columns(),
        edit_href=url_for('product.edit'))
