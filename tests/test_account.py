import os
import pytest
from app import create_app, db
from dotenv import load_dotenv
from .mock_db import create_mock_db

from app.ninja import NinjaApi, NinjaInvoice
from app.controller.account import AccountController

app = create_app(environment="testing")
app.config["TESTING"] = True

TEST_CSV_FILE = 'nitrix_import_test.csv'

TEST_CLIENT_NAME = "TEST RESELLER NAME"
TEST_PRODUCT_NAME = "TEST PRODUCT"
TEST_PRODUCT_NOTES = "TEST PRODUCT NOTES"
TEST_PRODUCT_COST = 55.55
TEST_INVOICE_DATE = "1980-02-01"
TEST_INVOICE_DUE_DATE = "1980-02-29"

load_dotenv()
NINJA_TOKEN = os.environ.get("NINJA_API_TOKEN", "")


def cleanup(api):
    for client in api.clients:
        if TEST_CLIENT_NAME == client.name:
            api.delete_client(client.id)
    for product in api.products:
        if TEST_PRODUCT_NAME == product.product_key:
            api.delete_product(product.id, product_key=TEST_PRODUCT_NAME)
    for invoice in NinjaInvoice.all():
        if TEST_INVOICE_DATE == invoice.invoice_date:
            invoice.delete()


@pytest.fixture
def api():
    app_ctx = app.app_context()
    app_ctx.push()
    create_mock_db()
    api = NinjaApi()
    yield api
    cleanup(api)
    db.session.remove()
    db.drop_all()
    app_ctx.pop()


def test_import(api):
    with open(TEST_CSV_FILE, 'rb') as f:
        controller = AccountController(file_object=f)
        controller.import_data_from_file()
