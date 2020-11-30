# Currently not supported #

import os
import pytest
from app import create_app, db
from dotenv import load_dotenv
from .mock_db import create_mock_db

from app.ninja import NinjaApi, NinjaInvoice
from app.controller.account import AccountController

app = create_app(environment="testing")
app.config["TESTING"] = True

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


@pytest.fixture
def api():
    app_ctx = app.app_context()
    app_ctx.push()
    create_mock_db()
    api = NinjaApi()
    cleanup(api)
    yield api
    cleanup(api)
    db.session.remove()
    db.drop_all()
    app_ctx.pop()


@pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
def test_import(api):
    with open(TEST_CSV_FILE, "rb") as f:
        controller = AccountController(file_object=f)
        controller.import_data_from_file()
    invoices = [i for i in NinjaInvoice.all() if not i.is_deleted]
    assert len(invoices) == 2
    invoices = [i for i in invoices if i.invoice_date == "2020-07-01"]
    assert len(invoices) == 1
    items = invoices[0].items
    assert len(items) == 5
