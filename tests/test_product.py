import pytest

from app import db, create_app
from app.models import Product, HistoryChange
from .test_auth import register, login


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        # register test user.
        register("sam")
        # Login by test user
        login(client, "sam")
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_edit_product(client):
    response = client.get("/products")
    assert response.status_code == 200
    product = Product(name="TEST PRODUCT NAME")
    product.save()
    response = client.get(f"/product_details?id={product.id}")
    assert response.status_code == 200
    assert b"TEST PRODUCT NAME" in response.data


def test_save_product(client):
    # add new product
    response = client.post(
        "/product_save",
        data=dict(id=-1, name="TEST PRODUCT NAME", status="active"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"TEST PRODUCT NAME" in response.data
    history = HistoryChange.query.filter(HistoryChange.item_id == 1).all()
    assert len(history) == 1
    assert history[0].change_type == HistoryChange.EditType.creation_product
    # edit exists product
    response = client.post(
        "/product_save",
        data=dict(id=1, name="ANOTHER PRODUCT NAME", status="not_active"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"TEST PRODUCT NAME" not in response.data
    assert b"ANOTHER PRODUCT NAME" in response.data
    history = HistoryChange.query.filter(HistoryChange.item_id == 1).all()
    assert len(history) == 2
    assert history[1].before_value_str == "TEST PRODUCT NAME"
    assert history[1].after_value_str == "ANOTHER PRODUCT NAME"
    assert history[1].change_type == HistoryChange.EditType.changes_product

    # save product with wrong id
    response = client.post(
        "/product_save",
        data=dict(id=2, name="BAD PRODUCT NAME", status="not_active"),
        follow_redirects=True,
    )
    assert b"Wrong product id." in response.data
    # send wrong form data
    response = client.post("/product_save", data=dict(id=2), follow_redirects=True)
    assert b"Form validation error" in response.data


def test_delete_product(client):
    # delete certain product
    response = client.post(
        "/product_save",
        data=dict(id=-1, name="TEST PRODUCT NAME", status="active"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"TEST PRODUCT NAME" in response.data
    history = HistoryChange.query.filter(HistoryChange.item_id == 1).all()
    assert len(history) == 1
    assert history[0].change_type == HistoryChange.EditType.creation_product
    product = Product.query.first()
    assert product
    product_id = product.id
    response = client.get(f"/product_delete?id={product_id}")
    assert response.status_code == 302
    assert product.deleted
    history = HistoryChange.query.filter(HistoryChange.item_id == 1).all()
    assert len(history) == 2
    assert history[1].change_type == HistoryChange.EditType.deletion_product
