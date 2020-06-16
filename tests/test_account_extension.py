import pytest
from flask import url_for
from app import create_app, db
from .test_auth import register, login

REDIRECTED = 302
OK = 200
NOT_NUMBER_ID = 'text_id'
CORRECT_ID = '1'
LOGIN = 'sam'
PASSW = '1234'


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
    response = client.get(url_for('account_extension.add'))
    assert response.status_code == REDIRECTED  # to the login page

    login(client, LOGIN, PASSW)
    # what if id is empty
    response = client.get(url_for('account_extension.add', id=''))
    assert response.status_code == REDIRECTED  # to the main.accounts
    # what if id is not into a request
    response = client.get(url_for('account_extension.add'))
    assert response.status_code == REDIRECTED  # to the main.accounts
    # what if id is not a number
    response = client.get(url_for('account_extension.add'))
    assert response.status_code == REDIRECTED  # to the main.accounts
    # what if correct id
    response = client.get(url_for('account_extension.add', id=CORRECT_ID))
    assert response.status_code == OK  # to the main.accounts


def test_edit():
    # what if not authorised

    # what if id is empty

    # what if id is not a number
    pass


def test_save_new():
    # what if id is empty

    # what if id is not a number

    # what if not authorised

    # what if pass not all data

    # what if wrong data

    # what id already in db

    # what if no account by an account_id
    pass


def test_save_update():
    # what if id is not a number

    # what if not authorised

    # what if pass not all data

    # what if wrong data

    # what if no account by an account_id
    pass


def test_delete():
    # try delete without id

    # what if id is not a number

    # try delete an extension which is not existed
    pass
