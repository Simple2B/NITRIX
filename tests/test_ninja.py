import pytest

from app.ninja import NinjaApp

TEST_CLIENT_NAME = 'TEST CLIENT'
TEST_PRODUCT_NAME = 'TEST PRODUCT'
TEST_PRODUCT_NOTES = 'TEST PRODUCT NOTES'
TEST_PRODUCT_COST = 55.55


def cleanup(app):
    for client in app.clients:
        if TEST_CLIENT_NAME == client.name:
            app.delete_client(client.id)
    for product in app.products:
        if TEST_PRODUCT_NAME == product.product_key:
            app.delete_product(product.id, product_key=TEST_PRODUCT_NAME)


@pytest.fixture
def app():
    app = NinjaApp()
    yield app
    cleanup(app)


def test_clients(app):
    client = app.add_client(TEST_CLIENT_NAME)
    clients = app.clients
    assert clients
    client = clients[0]
    client_id = client.id
    client = app.get_client(client_id)
    assert client


def test_add_delete_client(app):
    client = app.add_client(TEST_CLIENT_NAME)
    assert client and client.name == TEST_CLIENT_NAME
    assert app.delete_client(client.id)


def test_products(app):
    product = app.add_product(product_key=TEST_PRODUCT_NAME, notes=TEST_PRODUCT_NOTES, cost=TEST_PRODUCT_COST)
    products = app.products
    assert products
    product = products[0]
    product_id = product.id
    product = app.get_product(product_id)
    assert product


def test_add_delete_product(app):
    product = app.add_product(product_key=TEST_PRODUCT_NAME, notes=TEST_PRODUCT_NOTES, cost=TEST_PRODUCT_COST)
    assert product
    assert product.product_key == TEST_PRODUCT_NAME
    assert product.notes == TEST_PRODUCT_NOTES
    assert product.cost == TEST_PRODUCT_COST
    assert app.delete_product(product.id, product_key=TEST_PRODUCT_NAME)
