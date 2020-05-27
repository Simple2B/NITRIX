import io
import csv
import datetime
from flask import render_template, Blueprint, redirect, url_for, send_from_directory
from flask import current_app as app, send_file, request
from flask_login import login_required, current_user
from app.models import User, Product, Account, Reseller, Phone
from app.logger import log

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
@login_required
def index():
    if current_user.user_type.name == 'super_admin':
        return redirect(url_for("main.users"))
    return redirect(url_for("main.accounts"))


@main_blueprint.route('/accounts')
@login_required
def accounts():
    log(log.INFO, '/accounts')
    return render_template(
        'index.html',
        main_content='Accounts',
        table_data=[acc.to_dict() for acc in Account.query.all()],
        columns=Account.columns(),
        edit_href=url_for('account.edit'))


@main_blueprint.route('/users')
@login_required
def users():
    log(log.INFO, '/users')
    if current_user.user_type.name != 'super_admin':
        return redirect(url_for("main.index"))
    return render_template(
        'index.html',
        main_content='Users',
        table_data=[u.to_dict() for u in User.query.all()],
        columns=User.columns(),
        edit_href=url_for('user.edit'))


@main_blueprint.route('/resellers')
@login_required
def resellers():
    log(log.INFO, '/resellers')
    if current_user.user_type.name not in ['super_admin', 'admin']:
        return redirect(url_for("main.index"))
    return render_template(
        'index.html',
        main_content='Resellers',
        table_data=[i.to_dict() for i in Reseller.query.filter(Reseller.deleted == False)],  # noqa E712
        columns=Reseller.columns(),
        edit_href=url_for('reseller.edit'))


@main_blueprint.route('/products')
@login_required
def products():
    if current_user.user_type.name not in ['super_admin', 'admin']:
        return redirect(url_for("main.index"))
    return render_template(
        'index.html',
        main_content='Products',
        table_data=[p.to_dict() for p in Product.query.filter(Product.deleted == False)],  # noqa E712
        columns=Product.columns(),
        edit_href=url_for('product.edit'))


@main_blueprint.route('/phones')
@login_required
def phones():
    if current_user.user_type.name not in ['super_admin', 'admin']:
        return redirect(url_for("main.index"))
    return render_template(
        'index.html',
        main_content='Phones',
        table_data=[p.to_dict() for p in Phone.query.filter(Phone.deleted == False)],  # noqa E712
        columns=Phone.columns(),
        edit_href=url_for('phone.edit'))


@main_blueprint.route('/report')
@login_required
def report():
    log(log.INFO, 'report')

    if 'content' not in request.args:
        return

    content = request.args['content']

    Class = {
        'Users': User,
        'Products': Product,
        'Accounts': Account,
        'Phones': Phone,
        'Resellers': Reseller
    }[content]

    entities = Class.query.filter(Class.deleted == False)  # noqa

    if not entities:
        log(log.INFO, 'no entities')
        return

    proxy = io.StringIO()
    writer = csv.writer(proxy)
    row = [v for v in entities[0].to_dict().keys()]
    writer.writerow(row)
    for entity in entities:
        row = [v for v in entity.to_dict().values()]
        writer.writerow(row)

    # Creating the byteIO object from the StringIO Object
    mem = io.BytesIO()
    mem.write(proxy.getvalue().encode('utf-8'))
    mem.seek(0)
    proxy.close()

    now = datetime.datetime.now()
    return send_file(
        mem,
        as_attachment=True,
        attachment_filename='{content}_{now}.csv'.format(content=content, now=now.strftime("%Y-%m-%d-%H-%M-%S")),
        mimetype='text/csv',
        cache_timeout=0,
        last_modified=now
    )


@main_blueprint.route('/css/<path:filename>')
def css(filename):
    return send_from_directory(app.config['CSS_FOLDER'], filename)


@main_blueprint.route('/js/<path:filename>')
def javascript(filename):
    return send_from_directory(app.config['JAVASCRIPT_FOLDER'], filename)


@main_blueprint.route('/images/<path:filename>')
def images(filename):
    return send_from_directory(app.config['IMAGES_FOLDER'], filename)
