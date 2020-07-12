import pytest
from flask import url_for
from app import create_app, db
from app.models import AccountExtension, Account, Product, Phone, Reseller
from datetime import datetime
from .test_auth import register, login, logout
from .mock_db import create_mock_db

CORRECT_ID = '1'
EMPTY_ID = ''
NOT_NUMBER_ID = 'tid'
CORRECT_MONTHS = 12
WRONG_MONTHS = 13
EXTENSION_DATE = datetime.now
LOGIN = 'sam'
UNKNOWN_ID = 'Unknown id'
MONTHS_ERROR = 'Months must be in 1-12'
VALIDATION_ERROR = 'Form validation error'

app = create_app(environment='testing')
app.config['TESTING'] = True  # why do we need the here?


@pytest.fixture
def client():
    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        create_mock_db()
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
    check_not_auth(client, 'account_extension.edit')
    login(client, LOGIN)
    check_id(client, 'account_extension.edit')
    # what if id is correct, but an account_extension is not found
    redirect = client.get(url_for('account_extension.edit', id=CORRECT_ID))
    assert redirect.status_code == 302  # to the main.accounts
    response = client.get(redirect.location)
    assert UNKNOWN_ID.encode() in response.data
    # what if id is correct, but an account_extension exists
    ids = set_data()
    extension = AccountExtension(
        account_id=ids['account_id'],
        product_id=ids['product_id'],
        months=CORRECT_MONTHS,
        reseller_id=ids['reseller_id'],
    )
    extension.save()
    ext_id = extension.id
    response = client.get(url_for('account_extension.edit', id=ext_id))
    assert response.status_code == 200


def test_delete(client):
    check_not_auth(client, 'account_extension.delete')
    login(client, LOGIN)
    check_id(client, 'account_extension.delete')
    # what if delete an extension which is not existed
    redirect = client.get(url_for('account_extension.delete', id=CORRECT_ID))
    assert redirect.status_code == 302  # to the main.accounts
    response = client.get(redirect.location)
    assert UNKNOWN_ID.encode() in response.data
    # what if delete existed extension
    ids = set_data()
    acc_ext_id = AccountExtension(
        account_id=ids['account_id'],
        product_id=ids['product_id'],
        months=CORRECT_MONTHS,
        reseller_id=ids['reseller_id'],
    ).save().id
    response = client.get(url_for('account_extension.delete', id=acc_ext_id))
    assert response.status_code == 302


def test_save_new(client):
    check_not_auth_post(client, 'account_extension.save_new')
    login(client, LOGIN)
    check_id_post(client, 'account_extension.save_new')
    # what if no account by an account_id
    redirect = client.post(
        url_for('account_extension.save_new'),
        data=dict(
            id=CORRECT_ID,
            reseller_id=CORRECT_ID,
            product_id=CORRECT_ID,
            months=CORRECT_MONTHS
        )
    )
    assert redirect.status_code == 302  # to the main.accounts
    response = client.get(redirect.location)
    assert UNKNOWN_ID.encode() in response.data

    check_partial_data(client, 'account_extension.save_new')
    # what if wrong months
    ids = set_data()
    redirect = client.post(
        url_for('account_extension.save_new'),
        data=dict(
            id=CORRECT_ID,
            reseller_id=CORRECT_ID,
            product_id=CORRECT_ID,
            months=WRONG_MONTHS)
    )
    assert redirect.status_code == 302  # to the account.edit
    response = client.get(redirect.location)
    assert MONTHS_ERROR.encode() in response.data
    remove_data(ids)
    # what if OK
    ids = set_data()
    response = client.post(
        url_for('account_extension.save_new'),
        data=dict(
            id=ids['account_id'],
            reseller_id=ids['reseller_id'],
            product_id=ids['product_id'],
            months=CORRECT_MONTHS
        )
    )
    extensions = AccountExtension.query.filter(AccountExtension.account_id == ids['account_id']).all()
    assert response.status_code == 302
    assert extensions
    remove_data(ids)


def test_save_update(client):
    check_not_auth_post(client, 'account_extension.save_update')
    login(client, LOGIN)
    check_id_post(client, 'account_extension.save_update')
    # what if pass not all data
    # what if wrong data
    # # what if no account by an account_id


def check_partial_data(client, blueprint):
    # what if pass on reseller id
    ids = set_data()
    redirect = client.post(
        url_for(blueprint),
        data=dict(
            id=ids['account_id'],
            extension_date=EXTENSION_DATE,
            product_id=ids['product_id'],
            months=CORRECT_MONTHS
        )
    )
    assert redirect.status_code == 302  # to the account.edit
    response = client.get(redirect.location)
    assert VALIDATION_ERROR.encode() in response.data
    # what if pass on extension_date
    redirect = client.post(
        url_for(blueprint),
        data=dict(
            id=ids['account_id'],
            reseller_id=ids['reseller_id'],
            product_id=ids['product_id'],
            months=CORRECT_MONTHS
        )
    )
    assert redirect.status_code == 302  # to the account.edit
    # what if pass on product_id
    redirect = client.post(
        url_for(blueprint),
        data=dict(
            id=ids['account_id'],
            reseller_id=ids['reseller_id'],
            months=CORRECT_MONTHS
        )
    )
    assert redirect.status_code == 302  # to the account.edit
    response = client.get(redirect.location)
    assert VALIDATION_ERROR.encode() in response.data
    # what if pass on months
    redirect = client.post(
        url_for('account_extension.save_new'),
        data=dict(
            id=ids['account_id'],
            reseller_id=ids['reseller_id'],
            product_id=ids['product_id'])
    )
    assert redirect.status_code == 302  # to the account.edit
    response = client.get(redirect.location)
    assert VALIDATION_ERROR.encode() in response.data
    remove_data(ids)


def check_id(client, blueprint):
    ''' verify different ID values behavior '''
    # what if id is empty
    redirect = client.get(url_for(blueprint, id=EMPTY_ID))
    assert redirect.status_code == 302  # to the main.accounts
    response = client.get(redirect.location)
    assert UNKNOWN_ID.encode() in response.data
    # what if id is not into a request
    redirect = client.get(url_for(blueprint))
    assert redirect.status_code == 302  # to the main.accounts
    response = client.get(redirect.location)
    assert UNKNOWN_ID.encode() in response.data
    # what if id is not a number
    redirect = client.get(url_for(blueprint, id=NOT_NUMBER_ID))
    assert redirect.status_code == 302  # to the main.accounts
    response = client.get(redirect.location)
    assert UNKNOWN_ID.encode() in response.data


def check_id_post(client, blueprint):
    # what if account_id is empty
    redirect = client.post(
        url_for(blueprint),
        data=dict(id=EMPTY_ID)
    )
    assert redirect.status_code == 302  # to the main.accounts
    response = client.get(redirect.location)
    assert VALIDATION_ERROR.encode() in response.data
    # what if id is not into request
    redirect = client.post(
        url_for(blueprint)
    )
    assert redirect.status_code == 302  # to the main.accounts
    response = client.get(redirect.location)
    assert VALIDATION_ERROR.encode() in response.data
    # what if account_id isn't a number
    redirect = client.post(
        url_for(blueprint),
        data=dict(id=NOT_NUMBER_ID)
    )
    assert redirect.status_code == 302  # to the main.accounts
    response = client.get(redirect.location)
    assert VALIDATION_ERROR.encode() in response.data


def check_not_auth(client, blueprint):
    # what if not authorised
    logout(client)
    response = client.get(url_for(blueprint))
    assert response.status_code == 302  # to the login page


def check_not_auth_post(client, blueprint):
    # what if not authorised
    logout(client)
    response = client.post(url_for(blueprint))
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
        comment='TEST_COMMENT',
        months=CORRECT_MONTHS
    ).save().id
    return {
        'product_id': prod_id,
        'phone_id': phone_id,
        'reseller_id': res_id,
        'account_id': acc_id
    }


def remove_data(ids):
    Product.query.filter(Product.id == ids['product_id']).first().delete()
    Phone.query.filter(Phone.id == ids['phone_id']).first().delete()
    Reseller.query.filter(Reseller.id == ids['reseller_id']).first().delete()
    Account.query.filter(Account.id == ids['account_id']).first().delete()
