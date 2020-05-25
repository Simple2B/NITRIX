import pytest

from app import db, create_app
from app.models import Product
from .test_auth import register, login


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


def test_edit_product(client):
    response = client.get('/products')
    assert response.status_code == 200
    product = Product(name='TEST PRODUCT NAME')
    product.save()
    response = client.get(f'/product_details?id={product.id}')
    assert response.status_code == 200
    assert b'TEST PRODUCT NAME' in response.data


def test_save_product(client):
    # add new product
    response = client.post(
        '/product_save',
        data=dict(id=-1, name='TEST PRODUCT NAME', status='active'),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'TEST PRODUCT NAME' in response.data
    # edit exists product
    response = client.post(
        '/product_save',
        data=dict(id=1, name='ANOTHER PRODUCT NAME', status='not_active'),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'TEST PRODUCT NAME' not in response.data
    assert b'ANOTHER PRODUCT NAME' in response.data
    # save product with wrong id
    response = client.post(
        '/product_save',
        data=dict(id=2, name='BAD PRODUCT NAME', status='not_active'),
        follow_redirects=True
    )
    assert b'Wrong product id.' in response.data
    # send wrong form data
    response = client.post(
        '/product_save',
        data=dict(id=2),
        follow_redirects=True
    )
    assert b'Form validation error' in response.data
