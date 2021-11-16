from datetime import datetime
import os
from dotenv import load_dotenv
import pytest
from flask import url_for
from app import db, create_app
from .test_auth import register, login
from app.models import Product, Reseller, HistoryChange, Phone
from app.scheduler import sync_scheduler

load_dotenv()
NINJA_TOKEN = os.environ.get("NINJA_API_TOKEN", "")
TEST_PRODUCT_NAME = "TEST PRODUCT NAME"
TEST_SUBSCRIPTION_COST = 100.05
TEST_EXTENTION_COST = 99.9
TEST_RESELLER_NAME = "TEST RESELLER NAME"


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        create_default_db()
        register("sam")
        login(client, "sam")
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def create_default_db():
    Phone(name="None").save()


def create_reseller(client):
    response = client.post(
        "/reseller_save",
        data=dict(
            id=-1,
            name=TEST_RESELLER_NAME,
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200
    history = HistoryChange.query.all()
    assert len(history) == 1
    assert history[0].change_type == HistoryChange.EditType.creation_reseller


def create_product(client):
    response = client.post(
        "/product_save",
        data=dict(id=-1, name=TEST_PRODUCT_NAME, status="active"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    history = HistoryChange.query.all()
    assert len(history) == 2
    assert history[1].change_type == HistoryChange.EditType.creation_product


def create_reseller_product(client):
    create_reseller(client)
    create_product(client)
    reseller = Reseller.query.first()
    product = Product.query.first()
    response = client.post(
        url_for("reseller_product.save"),
        data=dict(
            id=-1,
            product_id=product.id,
            reseller_id=reseller.id,
            months=3,
            init_price=TEST_SUBSCRIPTION_COST,
            ext_price=TEST_EXTENTION_COST,
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200


@pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
def test_creation_reseller_product(client):
    create_reseller_product(client)
    history = HistoryChange.query.all()
    assert len(history) == 3
    assert history[2].change_type == HistoryChange.EditType.creation_reseller_product
    history = HistoryChange.query.filter(
        HistoryChange.synced == False  # noqa E712
    ).all()
    assert len(history) == 3
    sync_scheduler()
    history = HistoryChange.query.filter(
        HistoryChange.synced == True  # noqa E712
    ).all()
    assert len(history) == 3


@pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
def test_create_account(client):
    create_reseller_product(client)

    URL_SAVE_ACC = "/account_save"
    response = client.post(
        URL_SAVE_ACC,
        data=dict(
            id=-1,
            name="George",
            phone_id=1,
            sim_cost="yes",
            months=3,
            activation_date=datetime.now().date(),
            sim="12312312123",
            product_id=1,
            reseller_id=1,
            submit="Save",
            comment="",
        ),
        follow_redirects=True,
    )
    assert response

    history = HistoryChange.query.filter(
        HistoryChange.change_type == HistoryChange.EditType.creation_account
    ).all()

    assert len(history) == 1
    sync_scheduler()
    history = HistoryChange.query.filter(
        HistoryChange.synced == False  # noqa E712
    ).all()
    assert not history
