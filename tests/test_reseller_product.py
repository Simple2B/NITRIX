import pytest
from app import db, create_app
from app.models import ResellerProduct, Product
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


def test_edit_reseller(client):
    TEST_PROD_ID = 3
    reseller_product = ResellerProduct(product_id=TEST_PROD_ID)
    reseller_product.save()
    response = client.get(f'/reseller_product_edit?id={reseller_product.id}')
    assert response.status_code == 200
    assert b'3' in response.data