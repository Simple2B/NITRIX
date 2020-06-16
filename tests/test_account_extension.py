import pytest
from app import create_app


# fixture functions run before every test funcs
@pytest.fixture
def client():
    app = create_app(environment='testing')
    app.config['TESTING'] = True  # why do we need the here?


def test_add():
    # what if id is empty

    # what if id is not a number

    # what if not authorised
    pass


def test_edit():
    # what if id is empty

    # what if id is not a number

    # what if not authorised
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
