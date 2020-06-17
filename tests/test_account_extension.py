import pytest
from flask import url_for
from app import create_app, db
from app.models import AccountExtension, Account
from datetime import datetime
from .test_auth import register, login

OK = 200
REDIRECTED = 302
NOT_NUMBER_ID = 'text_id'
CORRECT_ID = '1'
ENCODING = 'utf-8'
LOGIN = 'sam'
PASSW = '1234'
EXTENSION_ADD = 'account_extension.add'
EXTENSION_EDIT = 'account_extension.edit'
EXTENSION_SAVE_NEW = 'account_extension.save_new'
EXTENSION_DELETE = 'account_extension.delete'
UNKNOWN_ID = 'Unknown id'
VALIDATION_ERROR = 'Form validation error'
WRONG_MONTHS = 'Months must be in 1-12'


@pytest.fixture
def client():
    app = create_app(environment='testing')
    app.config['TESTING'] = True  # why do we need the here?
    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.create_all()
        register(LOGIN, PASSW)  # register a test user.
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_add(client):
    # what if not authorised
    response = client.get(url_for(EXTENSION_ADD))
    assert response.status_code == REDIRECTED  # to the login page
    assert bytes(UNKNOWN_ID, encoding=ENCODING) in response.data

    login(client, LOGIN, PASSW)
    # what if id is empty
    response = client.get(url_for(EXTENSION_ADD, id=''))
    assert response.status_code == REDIRECTED  # to the main.accounts
    assert bytes(UNKNOWN_ID, encoding=ENCODING) in response.data
    # what if id is not into a request
    response = client.get(url_for(EXTENSION_ADD))
    assert response.status_code == REDIRECTED  # to the main.accounts
    assert bytes(UNKNOWN_ID, encoding=ENCODING) in response.data
    # what if id is not a number
    response = client.get(url_for(EXTENSION_ADD))
    assert response.status_code == REDIRECTED  # to the main.accounts
    assert bytes(UNKNOWN_ID, encoding=ENCODING) in response.data
    # what if correct id
    response = client.get(url_for(EXTENSION_ADD, id=CORRECT_ID))
    assert response.status_code == OK


def test_edit():
    # what if not authorised
    response = client.get(url_for(EXTENSION_EDIT))
    assert response.status_code == REDIRECTED  # to the login page

    login(client, LOGIN, PASSW)
    # what if id is empty
    response = client.get(url_for(EXTENSION_EDIT, id=''))
    assert response.status_code == REDIRECTED  # to the main.accounts
    assert bytes(UNKNOWN_ID, encoding=ENCODING) in response.data
    # what if id is not into a request
    response = client.get(url_for(EXTENSION_EDIT))
    assert response.status_code == REDIRECTED  # to the main.accounts
    assert bytes(UNKNOWN_ID, encoding=ENCODING) in response.data
    # what if id is not a number
    response = client.get(url_for(EXTENSION_EDIT))
    assert response.status_code == REDIRECTED  # to the main.accounts
    assert bytes(UNKNOWN_ID, encoding=ENCODING) in response.data
    # what if id is correct, but an account_extension is not found
    response = client.get(url_for(EXTENSION_EDIT, id=CORRECT_ID))
    assert response.status_code == REDIRECTED  # to the main.accounts
    assert bytes(UNKNOWN_ID, encoding=ENCODING) in response.data
    # what if id is correct, but an account_extension exists
    extension = AccountExtension(id=1)
    extension.save()
    response = client.get(url_for(EXTENSION_EDIT, id=CORRECT_ID))
    assert response.status_code == 200
    assert response.form.get('id') == '1'


def test_save_new():
    # what if not authorised
    response = client.get(url_for(EXTENSION_SAVE_NEW))
    assert response.status_code == REDIRECTED  # to the login page

    login(client, LOGIN, PASSW)
    # what if account_id is empty
    response = client.post(url_for(EXTENSION_EDIT), data=dict(id=''))
    assert response.status_code == REDIRECTED  # to the main.accounts
    assert bytes(UNKNOWN_ID, encoding=ENCODING) in response.data
    # what if account_id isn't a number
    response = client.post(
        url_for(EXTENSION_EDIT),
        data=dict(id=NOT_NUMBER_ID)
    )
    assert response.status_code == REDIRECTED  # to the main.accounts
    assert bytes(UNKNOWN_ID, encoding=ENCODING) in response.data
    # what if no account by an account_id
    response = client.post(
        url_for(EXTENSION_EDIT),
        data=dict(
            id=CORRECT_ID,
            reseller_id='1',
            extension_date=datetime.now,
            product_id='1', months=1
        )
    )
    assert response.status_code == REDIRECTED  # to the main.accounts
    assert bytes(UNKNOWN_ID, encoding=ENCODING) in response.data

    account = Account(
        id=CORRECT_ID,
        name='TEST_ACCOUNT',
        product_id=1,
        phone_id=1,
        reseller_id=1,
        sim='TEST_SIM',
        imei='TEST_IMEI',
        comment='TEST_COMMENT'
    )
    account.save()
    # what if pass on reseller_id
    response = client.post(
        url_for(EXTENSION_EDIT),
        data=dict(id=UNKNOWN_ID, extension_date=datetime.now, product_id='1', months=1)
    )
    assert response.status_code == REDIRECTED  # to the account.edit
    assert bytes(VALIDATION_ERROR, encoding=ENCODING) in response.data
    # what if pass on extension_date
    response = client.post(
        url_for(EXTENSION_EDIT),
        data=dict(id=CORRECT_ID, reseller_id='1', product_id='1', months=1)
    )
    assert response.status_code == REDIRECTED  # to the account.edit
    assert bytes(VALIDATION_ERROR, encoding=ENCODING) in response.data
    # what if pass on product_id
    response = client.post(
        url_for(EXTENSION_EDIT),
        data=dict(id=CORRECT_ID, reseller_id='1', extension_date=datetime.now, months=1)
    )
    assert response.status_code == REDIRECTED  # to the account.edit
    assert bytes(VALIDATION_ERROR, encoding=ENCODING) in response.data
    # what if pass on months
    response = client.post(
        url_for(EXTENSION_EDIT),
        data=dict(id=CORRECT_ID, reseller_id='1', extension_date=datetime.now, product_id='1')
    )
    assert response.status_code == REDIRECTED  # to the account.edit
    assert bytes(VALIDATION_ERROR, encoding=ENCODING) in response.data
    # Wrong months
    response = client.post(
        url_for(EXTENSION_EDIT),
        data=dict(id=CORRECT_ID, reseller_id='1', extension_date=datetime.now, product_id='1', months=13)
    )
    assert response.status_code == REDIRECTED  # to the account.edit
    assert bytes(WRONG_MONTHS, encoding=ENCODING) in response.data
    # what if OK
    current_dt = datetime.now
    response = client.post(
        url_for(EXTENSION_EDIT),
        data=dict(
            id=CORRECT_ID, reseller_id='2',
            extension_date=current_dt, product_id='2', months=1)
    )
    extensions = AccountExtension.query.filter(AccountExtension.account_id == CORRECT_ID).all()
    assert response.status_code == OK
    assert extensions


def test_save_update():
    # what if id is not a number

    # what if not authorised

    # what if pass not all data

    # what if wrong data

    # what if no account by an account_id
    pass


def test_delete():
    # what if not authorised
    response = client.get(url_for(EXTENSION_SAVE_NEW))
    assert response.status_code == REDIRECTED  # to the login page
    # try delete without id

    # what if id is not a number

    # try delete an extension which is not existed
    pass
