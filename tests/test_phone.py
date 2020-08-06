import pytest

from app import db, create_app
from app.models import Phone
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


def test_edit_phone(client):
    response = client.get("/phones")
    assert response.status_code == 200
    phone = Phone(name="TEST PHONE NAME", price=10.00)
    phone.save()
    response = client.get(f"/phone_details?id={phone.id}")
    assert response.status_code == 200
    assert b"TEST PHONE NAME" in response.data


def test_save_phone(client):
    # add new phone
    response = client.post(
        "/phone_save",
        data=dict(id=-1, name="TEST PHONE NAME", price=10.00, status="active"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"TEST PHONE NAME" in response.data
    # edit exists phone
    response = client.post(
        "/phone_save",
        data=dict(id=1, name="ANOTHER PHONE NAME", price=5.00, status="not_active"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"TEST PHONE NAME" not in response.data
    assert b"ANOTHER PHONE NAME" in response.data
    # save phone with wrong id
    response = client.post(
        "/phone_save",
        data=dict(id=2, name="BAD PHONE NAME", status="not_active"),
        follow_redirects=True,
    )
    assert b"Wrong phone id." in response.data
    # send wrong form data
    response = client.post("/phone_save", data=dict(id=2), follow_redirects=True)
    assert b"Form validation error" in response.data
