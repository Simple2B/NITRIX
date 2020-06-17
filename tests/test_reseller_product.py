from flask import url_for
import pytest
from app import db, create_app
from app.models import ResellerProduct, Product, Reseller
from .test_auth import register, login

INIT_PRICE = 55555.00
EXT_PRICE = 333.33
NEW_INIT_PRICE = 88888.00
NEW_EXT_PRICE = 4444.44


@pytest.fixture
def client():
    app = create_app(environment='testing')
    app.config['TESTING'] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        # register test user.
        register('sam')
        # Login by test user
        login(client, 'sam')
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_edit_reseller(client):
    TEST_PROD_ID = 3
    reseller_product = ResellerProduct(product_id=TEST_PROD_ID)
    reseller_product.save()
    url = url_for('reseller_product.edit', id=reseller_product.id)
    response = client.get(url)
    assert response.status_code == 200
    assert f'{TEST_PROD_ID}'.encode('utf-8') in response.data


def test_save_delete_reseller(client):
    # add new reseller
    reseller = Reseller(name='Dima')
    reseller.save()
    product = Product(name="Gold")
    product.save()
    response = client.post(
        url_for('reseller_product.save'),
        data=dict(
            id=-1, product_id=product.id, reseller_id=reseller.id, months=3, init_price=INIT_PRICE, ext_price=EXT_PRICE),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'55555' in response.data
    # edit exists resellers product
    response = client.post(
         url_for('reseller_product.save'),
         data=dict(
             id=1, product_id=product.id, reseller_id=reseller.id, months=3, init_price=NEW_INIT_PRICE, ext_price=NEW_EXT_PRICE),
         follow_redirects=True
     )
    assert response.status_code == 200
    assert b'55555' not in response.data
    assert b'88888' in response.data
    # send wrong form data
    response = client.post(
         url_for('reseller_product.save'),
         data=dict(
             id=1, product_id=product.id, reseller_id=reseller.id, months="Mohths", init_price=888.00, ext_price="25"),
         follow_redirects=True
     )
    assert b'Form validation error' in response.data
    # delete
    reseller_product = ResellerProduct(product_id=product.id, reseller_id=reseller.id, months=6,
                                            init_price=INIT_PRICE, ext_price=EXT_PRICE)
    reseller_product.save()
    response = client.get(url_for('reseller_product.delete', id=reseller_product.id))
    assert response.status_code == 302
    assert b"55555" not in response.data


def test_save_exist_product(client):
    # add new product
    reseller = Reseller(name='Dima')
    reseller.save()
    product = Product(name="Gold")
    product.save()
    response = client.post(
        url_for('reseller_product.save'),
        data=dict(
            id=-1, product_id=product.id, reseller_id=reseller.id, months=3, init_price=INIT_PRICE, ext_price=EXT_PRICE),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'55555' in response.data
    # add the same product
    response = client.post(
        url_for('reseller_product.save'),
        data=dict(
            id=-1, product_id=product.id, reseller_id=reseller.id, months=3, init_price=INIT_PRICE,
            ext_price=EXT_PRICE),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Reseller already have this product' in response.data