import pytest

from app.ninja import NinjaApi

TEST_CLIENT_NAME = 'TEST RESELLER NAME'
TEST_PRODUCT_NAME = 'TEST PRODUCT'
TEST_PRODUCT_NOTES = 'TEST PRODUCT NOTES'
TEST_PRODUCT_COST = 55.55


def cleanup(api):
    for client in api.clients:
        if TEST_CLIENT_NAME == client.name:
            api.delete_client(client.id)
    for product in api.products:
        if TEST_PRODUCT_NAME == product.product_key:
            api.delete_product(product.id, product_key=TEST_PRODUCT_NAME)


@pytest.fixture
def api():
    api = NinjaApi()
    yield api
    cleanup(api)


def test_clients(api):
    client = api.add_client(TEST_CLIENT_NAME)
    clients = api.clients
    assert clients
    client = clients[0]
    client_id = client.id
    client = api.get_client(client_id)
    assert client


def test_add_delete_client(api):
    client = api.add_client(TEST_CLIENT_NAME)
    assert client and client.name == TEST_CLIENT_NAME
    assert api.delete_client(client.id)


def test_products(api):
    product = api.add_product(product_key=TEST_PRODUCT_NAME, notes=TEST_PRODUCT_NOTES, cost=TEST_PRODUCT_COST)
    products = api.products
    assert products
    product = products[0]
    product_id = product.id
    product = api.get_product(product_id)
    assert product


def test_add_delete_product(api):
    product = api.add_product(product_key=TEST_PRODUCT_NAME, notes=TEST_PRODUCT_NOTES, cost=TEST_PRODUCT_COST)
    assert product
    assert product.product_key == TEST_PRODUCT_NAME
    assert product.notes == TEST_PRODUCT_NOTES
    assert product.cost == TEST_PRODUCT_COST
    assert api.delete_product(product.id, product_key=TEST_PRODUCT_NAME)
