# Currently not supported #

from datetime import datetime
import os
import pytest
from app import create_app, db
from dotenv import load_dotenv
from .mock_db import create_mock_db
from datetime import datetime
from flask import url_for, current_app
from app.models import Account

from app.ninja import NinjaApi, NinjaInvoice
from app.controller.account import AccountController
from .test_auth import register, login

# app = create_app(environment="testing")
# app.config["TESTING"] = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_CSV_FILE = os.path.join(BASE_DIR, "nitrix_import_test.csv")

TEST_INVOICE_DATE_1 = "2020-07-01"
TEST_INVOICE_DATE_2 = "2020-08-01"

load_dotenv()
NINJA_TOKEN = os.environ.get("NINJA_API_TOKEN", "")


def cleanup(api):
    for invoice in NinjaInvoice.all():
        if invoice.invoice_date in (TEST_INVOICE_DATE_1, TEST_INVOICE_DATE_2):
            invoice.delete()


# @pytest.fixture
# def api():
#     app_ctx = app.app_context()
#     app_ctx.push()
#     create_mock_db()
#     api = NinjaApi()
#     cleanup(api)
#     yield api
#     cleanup(api)
#     db.session.remove()
#     db.drop_all()
#     app_ctx.pop()


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        create_mock_db()
        # register test user.
        register("administrator")
        # Login by test user
        login(client, "administrator")
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


# @pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
# def test_import(api):
#     with open(TEST_CSV_FILE, "rb") as f:
#         controller = AccountController(file_object=f)
#         controller.import_data_from_file()
#     invoices = [i for i in NinjaInvoice.all() if not i.is_deleted]
#     assert len(invoices) == 2
#     invoices = [i for i in invoices if i.invoice_date == "2020-07-01"]
#     assert len(invoices) == 1
#     items = invoices[0].items
#     assert len(items) == 5


def test_create_account(client):
    URL_CREATE_ACCOUNT = "/account_details"
    URL_SAVE_ACC = "/account_save"
    response = client.get(
        URL_CREATE_ACCOUNT
    )
    assert response.status_code == 200
    response = client.post(
        URL_SAVE_ACC,
        data=dict(
            id=-1,
            name='Georg',
            phone_id=1,
            sim_cost='yes',
            months=6,
            activation_date=datetime.now().date(),
            sim='12312312123',
            product_id=1,
            reseller_id=1,
            submit='save_and_add'
        ),
        # follow_redirects=True
    )
    # assert b'Login' in response.data

    assert response.status_code == 302
    users = Account.query.all()
    user = users[-1]
    assert user.name == 'Georg'
    response = client.post(
        URL_SAVE_ACC,
        data=dict(
            id=-1,
            name='Georgiv',
            phone_id=1,
            sim_cost='yes',
            months=6,
            activation_date=datetime.now().date(),
            sim='12312312123',
            product_id=1,
            reseller_id=1,
            submit='save_and_edit'
        ),
        # follow_redirects=True
    )
    # assert b'Login' in response.data

    assert response.status_code == 302
    users = Account.query.all()
    user = users[-1]
    assert user.name == 'Georgiv'


def test_delete_account(client):
    URL_DELETE_ACCOUNT = "/account_delete"
    account = Account(
        name='Georg',
        phone_id=1,
        months=6,
        imei='123213',
        activation_date=datetime.now().date(),
        sim='12312312123',
        product_id=1,
        reseller_id=1,
        comment=''
    )
    account.save()
    test_acc = Account.query.filter(Account.name == 'Georg').first()
    assert test_acc
    response = client.get(
        f'{URL_DELETE_ACCOUNT}?id={test_acc.id}',
        )
    assert response.status_code == 302
    test_acc = Account.query.filter(Account.name == 'Georg').first()
    assert not test_acc


def test_edit_account(client):
    URL_SAVE_ACC = '/account_save'
    account = Account(
        name='Georg',
        phone_id=1,
        months=6,
        imei='123213',
        activation_date=datetime.now().date(),
        sim='12312312123',
        product_id=1,
        reseller_id=1,
        comment=''
    )
    account.save()
    response = client.post(
        URL_SAVE_ACC,
        data=dict(
            id=-1,
            name='Georgws',
            phone_id=1,
            sim_cost='yes',
            months=6,
            activation_date=datetime.now().date(),
            sim='13333333',
            product_id=2,
            reseller_id=1,
            submit='save_and_add'
        ),
    )
    assert response.status_code == 302
    users = Account.query.all()
    user = users[-1]
    assert user.name == 'Georgws' and user.product_id == 2 and user.sim == '13333333'