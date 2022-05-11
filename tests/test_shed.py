from datetime import datetime
import os
from dotenv import load_dotenv
import pytest
from flask import url_for
from app import db, create_app
from tests.utils import mocking_get_current_invoice
from .test_auth import register, login
from app.models import Product, Reseller, HistoryChange, Phone, Account
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


def create_reseller(client, reseller_name):
    response = client.post(
        "/reseller_save",
        data=dict(
            id=-1,
            name=reseller_name,
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200
    history = HistoryChange.query.all()
    assert history[0].change_type == HistoryChange.EditType.creation_reseller


def create_product(client, product_name):
    response = client.post(
        "/product_save",
        data=dict(id=-1, name=product_name, status="active"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    history = HistoryChange.query.all()
    assert history[1].change_type == HistoryChange.EditType.creation_product


def create_reseller_product(client, prod_name: str, month: int, res_name: str):
    """We can create different resellers and products and in the end reseller products

    Args:
        client (_type_): _description_
        prod_name (str):product name
        month (int): amount of moths
        res_name (str): reseller name

    Returns:
        int: returning id off created PRODUCT, so it can be used further in test
    """
    create_reseller(client, res_name)
    create_product(client, prod_name)
    reseller: Reseller = Reseller.query.filter(Reseller.name == res_name).first()
    product: Product = Product.query.filter(Product.name == prod_name).first()
    response = client.post(
        url_for("reseller_product.save"),
        data=dict(
            id=-1,
            product_id=product.id,
            reseller_id=reseller.id,
            months=month,
            init_price=TEST_SUBSCRIPTION_COST,
            ext_price=TEST_EXTENTION_COST,
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200
    return product.id


@pytest.mark.skipif(not NINJA_TOKEN, reason="unknown NINJA_TOKEN")
def test_creation_reseller_product(client):
    create_reseller_product(client, TEST_PRODUCT_NAME, 3, TEST_RESELLER_NAME)
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


def test_create_account(client, monkeypatch):
    product_id = create_reseller_product(
        client, TEST_PRODUCT_NAME, 3, TEST_RESELLER_NAME
    )

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
            product_id=product_id,
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

    # get all changes except creation_account type and marking synced True
    # as we wanna test only sync on creation_account account
    history_all = HistoryChange.query.filter(
        HistoryChange.change_type != HistoryChange.EditType.creation_account
    ).all()
    assert history_all
    for event in history_all:
        event: HistoryChange = event
        event.synced = True
        event.save()

    mocking_get_current_invoice(monkeypatch)

    sync_scheduler()

    history = HistoryChange.query.filter(
        HistoryChange.synced == False  # noqa E712
    ).all()
    assert not history

    # creating another reseller product for different reseller
    product_id = create_reseller_product(client, "TEST NAME 2", 3, "TEST_RESELLER_2")

    # creating account with reseller product that reseller don't have
    URL_SAVE_ACC = "/account_save"
    response = client.post(
        URL_SAVE_ACC,
        data=dict(
            id=-1,
            name="TEST",
            phone_id=1,
            sim_cost="yes",
            months=3,
            activation_date=datetime.now().date(),
            sim="12312312123",
            product_id=product_id,
            reseller_id=1,
            submit="Save",
            comment="",
        ),
        follow_redirects=True,
    )
    assert response

    # get all changes except creation_account type and marking synced True
    # as we wanna test only sync on creation_account account
    history_all = HistoryChange.query.filter(
        HistoryChange.change_type != HistoryChange.EditType.creation_account
    ).all()
    assert history_all
    for event in history_all:
        event: HistoryChange = event
        event.synced = True
        event.save()

    # simulate sync
    sync_scheduler()

    # expecting sync was successfull and we create account with zero cost
    history = HistoryChange.query.filter(
        HistoryChange.synced == False  # noqa E712
    ).all()
    assert not history


def test_sync_deleted_account(client):
    create_reseller_product(client, TEST_PRODUCT_NAME, 3, TEST_RESELLER_NAME)

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

    # get all changes except creation_account type and marking synced True
    # as we wanna test only sync on deleted account
    history_all = HistoryChange.query.filter(
        HistoryChange.change_type != HistoryChange.EditType.creation_account
    ).all()
    assert history_all
    for event in history_all:
        event: HistoryChange = event
        event.synced = True
        event.save()

    # getting account and simulating deletion
    account: Account = Account.query.first()
    assert account
    account.deleted = True
    account.save()

    # running sync and excpecting to all HistoryChanges are synced
    sync_scheduler()
    history = HistoryChange.query.filter(
        HistoryChange.synced == False  # noqa E712
    ).all()
    assert not history
