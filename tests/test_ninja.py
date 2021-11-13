import os
import pytest
from dotenv import load_dotenv
from app.ninja import NinjaApi, NinjaInvoice

TEST_CLIENT_NAME = "TEST RESELLER NAME"
TEST_PRODUCT_NAME = "TEST PRODUCT"
TEST_PRODUCT_NOTES = "TEST PRODUCT NOTES"
TEST_PRODUCT_COST = 55.55
TEST_INVOICE_DATE = "1980-02-01"
TEST_INVOICE_DUE_DATE = "1980-02-29"

load_dotenv()
NINJA_TOKEN = os.environ.get("NINJA_API_TOKEN", "")


def cleanup(api: NinjaApi):
    for client in api.clients:
        if client.is_deleted:
            continue
        if TEST_CLIENT_NAME == client.name:
            api.delete_client(client.id)
    for product in api.products:
        if product.is_deleted:
            continue
        if TEST_PRODUCT_NAME == product.product_key:
            api.delete_product(product.id)
    for invoice in NinjaInvoice.all():
        if invoice.is_deleted:
            continue
        if TEST_INVOICE_DATE == invoice.date:
            invoice.delete()


@pytest.fixture
def api():
    api = NinjaApi()
    yield api
    cleanup(api)


@pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
def test_clients(api: NinjaApi):
    client = api.add_client(TEST_CLIENT_NAME)
    clients = api.clients
    assert clients
    client = clients[0]
    client_id = client.id
    client = api.get_client(client_id)
    assert client


@pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
def test_add_delete_client(api: NinjaApi):
    client = api.add_client(TEST_CLIENT_NAME)
    assert client and client.name == TEST_CLIENT_NAME
    assert api.delete_client(client.id)


@pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
def test_products(api: NinjaApi):
    product = api.add_product(
        product_key=TEST_PRODUCT_NAME, notes=TEST_PRODUCT_NOTES, cost=TEST_PRODUCT_COST
    )
    products = api.products
    assert products
    product = products[0]
    product_id = product.id
    product = api.get_product(product_id)
    assert product


@pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
def test_add_delete_product(api: NinjaApi):
    product = api.add_product(
        product_key=TEST_PRODUCT_NAME, notes=TEST_PRODUCT_NOTES, cost=TEST_PRODUCT_COST
    )
    assert product
    assert product.product_key == TEST_PRODUCT_NAME
    assert product.notes == TEST_PRODUCT_NOTES
    assert product.cost == TEST_PRODUCT_COST
    assert api.delete_product(product.id)


@pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
def test_add_update_product(api: NinjaApi):
    product = api.add_product(
        product_key=TEST_PRODUCT_NAME, notes=TEST_PRODUCT_NOTES, cost=TEST_PRODUCT_COST
    )
    assert product
    assert product.product_key == TEST_PRODUCT_NAME
    assert product.notes == TEST_PRODUCT_NOTES
    assert product.cost == TEST_PRODUCT_COST
    res = api.update_product(
        product.id,
        product_key=TEST_PRODUCT_NAME * 2,
        notes=TEST_PRODUCT_NOTES * 2,
        cost=TEST_PRODUCT_COST * 2,
    )
    assert res
    # reload product form server
    product = api.get_product(product.id)
    assert product.product_key == TEST_PRODUCT_NAME * 2
    assert product.notes == TEST_PRODUCT_NOTES * 2
    assert product.cost == TEST_PRODUCT_COST * 2
    assert api.delete_product(product.id)


@pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
def test_invoice(api: NinjaApi):
    client = api.add_client(TEST_CLIENT_NAME)
    assert client and client.name == TEST_CLIENT_NAME
    invoice = NinjaInvoice.add(client.id, TEST_INVOICE_DATE, TEST_INVOICE_DUE_DATE)
    assert invoice
    assert invoice.add_item(
        product_key=TEST_PRODUCT_NAME, notes="Account bubu", cost=TEST_PRODUCT_COST
    )
    invoices = NinjaInvoice.all()
    assert invoices
    invoice = invoices[0]
    items = invoice.line_items
    assert items
    item = items[0]
    assert item
    client = api.add_client(TEST_CLIENT_NAME)
    assert client
    product = api.add_product(
        product_key=TEST_PRODUCT_NAME, notes=TEST_PRODUCT_NOTES, cost=TEST_PRODUCT_COST
    )
    assert product
    assert invoice.add_item(
        product_key=TEST_PRODUCT_NAME, notes="Account bubu", cost=TEST_PRODUCT_COST
    )
    invoice = NinjaInvoice.get(invoice.id)
    assert invoice


@pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
def test_invoice_create_delete(api: NinjaApi):
    client = api.add_client(TEST_CLIENT_NAME)
    assert client and client.name == TEST_CLIENT_NAME
    invoice = NinjaInvoice.add(client.id, TEST_INVOICE_DATE, TEST_INVOICE_DUE_DATE)
    assert invoice
    assert invoice.delete()
