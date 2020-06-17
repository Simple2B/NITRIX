import pytest
from flask import url_for
from app import create_app, db
from app.models import AccountExtension, Account, Product, Phone, Reseller
from datetime import datetime
from .test_auth import register, login, logout

CORRECT_ID = '1'
NOT_NUMBER_ID = 'tid'
CORRECT_MONTHS = 12
WRONG_MONTHS = 13
LOGIN = 'sam'
UNKNOWN_ID = 'Unknown id'
MONTHS_ERROR = 'Months must be in 1-12'
VALIDATION_ERROR = 'Form validation error'


@pytest.fixture
def client():
    app = create_app(environment='testing')
    app.config['TESTING'] = True  # why do we need the here?
    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.create_all()
        register(LOGIN)  # register a test user.
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_add(client):
    check_not_auth(client, 'account_extension.add')
    login(client, LOGIN)
    check_id(client, 'account_extension.add')
    # what if correct id
    response = client.get(url_for('account_extension.add', id=CORRECT_ID))
    assert response.status_code == 200


def test_edit(client):
    check_not_auth('account_extension.edit')
    login(client, LOGIN)
    check_id('account_extension.edit')
    # what if id is correct, but an account_extension is not found
    response = client.get(url_for('account_extension.edit', id=CORRECT_ID))
    assert response.status_code == 302  # to the main.accounts
    assert UNKNOWN_ID.encode() in response.data
    # what if id is correct, but an account_extension exists
    extension = AccountExtension()
    extension.save()
    ext_id = extension.id
    response = client.get(url_for('account_extension.edit', id=CORRECT_ID))
    assert response.status_code == 200
    assert response.form.get('id') == str(ext_id)


def test_save_new(client):
    check_not_auth('account_extension.save_new')
    login(client, LOGIN)
    check_id_post(client, 'account_extension.save_new')
    # what if no account by an account_id
    response = client.post(
        url_for('account_extension.save_new'),
        data=dict(
            id=CORRECT_ID,
            reseller_id=CORRECT_ID,
            extension_date=datetime.now,
            product_id=CORRECT_ID, months=CORRECT_MONTHS
        )
    )
    assert response.status_code == 302  # to the main.accounts
    assert UNKNOWN_ID.encode() in response.data
    # what if pass on reseller id
    ids = set_data()
    response = client.post(
        url_for('account_extension.save_new'),
        data=dict(
            id=ids['account_id'],
            extension_date=datetime.now,
            product_id=ids['product_id'],
            months=CORRECT_MONTHS
        )
    )
    assert response.status_code == 302  # to the account.edit
    assert VALIDATION_ERROR.encode() in response.data
    # what if pass on extension_date
    response = client.post(
        url_for('account_extension.save_new'),
        data=dict(
            id=ids['account_id'],
            reseller_id=ids['reseller_id'],
            product_id=ids['product_id'],
            months=CORRECT_MONTHS
        )
    )
    assert response.status_code == 302  # to the account.edit
    assert VALIDATION_ERROR.encode() in response.data
    # what if pass on product_id
    response = client.post(
        url_for('account_extension.save_new'),
        data=dict(
            id=ids['account_id'],
            reseller_id=ids['reseller_id'],
            extension_date=datetime.now,
            months=CORRECT_MONTHS
        )
    )
    assert response.status_code == 302  # to the account.edit
    assert VALIDATION_ERROR.encode() in response.data
    # what if pass on months
    response = client.post(
        url_for('account_extension.save_new'),
        data=dict(
            id=ids['account_id'],
            reseller_id=ids['reseller_id'],
            extension_date=datetime.now,
            product_id=ids['product_id'])
    )
    assert response.status_code == 302  # to the account.edit
    assert VALIDATION_ERROR.encode() in response.data
    # what if wrong months
    response = client.post(
        url_for('account_extension.save_new'),
        data=dict(
            id=ids['account_id'],
            reseller_id=ids['reseller_id'],
            extension_date=datetime.now,
            product_id=ids['product_id'],
            months=WRONG_MONTHS)
    )
    assert response.status_code == 302  # to the account.edit
    assert MONTHS_ERROR.encode in response.data
    # what if OK
    response = client.post(
        url_for('account_extension.save_new'),
        data=dict(
            id=ids['account_id'],
            reseller_id=ids['reseller_id'],
            extension_date=datetime.now,
            product_id=ids['product_id'],
            months=CORRECT_MONTHS
        )
    )
    extensions = AccountExtension.query.filter(AccountExtension.account_id == ids['account_id']).all()
    assert response.status_code == 200
    assert extensions


def test_save_update(client):
    check_not_auth(client, 'account_extension.save_update')
    login(client, LOGIN)
    check_id_post(client, 'account_extension.save_update')
    # what if pass not all data

    # what if wrong data

    # what if no account by an account_id
    pass


def test_delete():
    check_not_auth(client, 'account_extension.delete')
    login(client, LOGIN)
    check_id(client, 'account_extension.delete')
    # what if delete an extension which is not existed
    ads = set_data()
    response = client.get(url_for('account_extension.delete'), id=CORRECT_ID)
    assert response.status_code == 302  # to the main.accounts
    assert UNKNOWN_ID.encode() in response.data
    # what if delete existed extension
    ads = set_data()
    acc_ext_id = AccountExtension(**ads).save().id
    response = client.get(url_for('account_extension.delete'), id=acc_ext_id)
    assert response.status_code == 302
    assert response.data.get('id') == ads['account_id']


def check_id(client, blueprint):
    # what if id is empty
    redirect = client.get(url_for(blueprint, id=''))
    assert redirect.status_code == 302  # to the main.accounts
    response = client.get(redirect.location)
    assert UNKNOWN_ID.encode() in response.data
    # what if id is not into a request
    redirect = client.get(url_for(blueprint))
    assert redirect.status_code == 302  # to the main.accounts
    response = client.get(redirect.location)
    assert UNKNOWN_ID.encode() in response.data
    # what if id is not a number
    # redirect = client.get(url_for(blueprint), id=NOT_NUMBER_ID)
    # assert redirect.status_code == 302  # to the main.accounts
    # response = client.get(redirect.location)
    # assert UNKNOWN_ID.encode() in response.data


def check_id_post(client, blueprint):
    # what if account_id is empty
    response = client.post(
        url_for(blueprint),
        data=dict(id='')
    )
    assert response.status_code == 302  # to the main.accounts
    assert UNKNOWN_ID.encode() in response.data
    # what if id is not into request
    response = client.post(
        url_for(blueprint)
    )
    assert response.status_code == 302  # to the main.accounts
    assert UNKNOWN_ID.encode() in response.data
    # what if account_id isn't a number
    response = client.post(
        url_for(blueprint),
        data=dict(id=NOT_NUMBER_ID)
    )
    assert response.status_code == 302  # to the main.accounts
    assert UNKNOWN_ID.encode() in response.data


def check_not_auth(client, blueprint):
    # what if not authorised
    logout(client)
    response = client.get(url_for(blueprint))
    assert response.status_code == 302  # to the login page


def set_data():
    prod_id = Product(name="TEST_NAME", status=Product.Status.active).save().id
    phone_id = Phone(name="TEST_NAME", status=Phone.Status.active).save().id
    res_id = Reseller(name="TEST_NAME", status=Reseller.Status.active).save().id
    acc_id = Account(
        name='TEST_NAME',
        product_id=prod_id,
        phone_id=phone_id,
        reseller_id=res_id,
        sim='TEST_SIM',
        imei='TEST_IMEI',
        comment='TEST_COMMENT'
    ).save().id
    return {
        'product_id': prod_id,
        'phone_id': phone_id,
        'reseller_id': res_id,
        'account_id': acc_id
    }
