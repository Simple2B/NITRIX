import time
import timecop
from flask import url_for
import pytest
from onetimepass import get_hotp, get_totp
from app import db, create_app
from app.models import User


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def register(user_name, password="password", user_type=User.Type.super_admin):
    # noinspection PyArgumentList
    user = User(name=user_name, password=password, user_type=user_type)
    user.save()
    return user.id


def login(client, user_name, password="password"):
    secret = b"MFRGGZDFMZTWQ2LK"
    with timecop.freeze(time.time()):
        user = User.query.filter(User.name == user_name).first()
        assert user
        user.otp_secret = secret
        user.otp_active = True
        hotp = get_hotp(
            secret=secret,
            intervals_no=int(time.time()) // 30,
        )
        totp = get_totp(secret=secret)
        assert hotp == totp
        res = client.post(
            "/login",
            data=dict(user_name=user_name, password=password),
            follow_redirects=True,
        )
        assert res.status_code == 200
        if b"Wrong user name or password." in res.data:
            return res
        return client.post(
            url_for("auth.otp_verify"),
            data=dict(token=f"{totp:06d}"),
            follow_redirects=True,
        )


def logout(client):
    return client.get("/logout", follow_redirects=True)


def test_index_page(client):
    # register test user.
    register("sam")
    # Login by test user
    response = login(client, "sam")
    assert b"Login successful." in response.data
    response = client.get("/accounts")
    assert response.status_code == 200


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_login_and_logout(client):
    # Access to logout view before login should fail.
    response = logout(client)
    assert b"Please log in to access this page." in response.data
    # register test user.
    register("sam")
    # Login by test user
    response = login(client, "sam")
    assert b"Login successful." in response.data
    # Should successfully logout the currently logged in user.
    response = logout(client)
    assert b"You were logged out." in response.data
    # Incorrect login credentials should fail.
    response = login(client, "sam", "wrongpassword")
    assert b"Wrong user name or password." in response.data
    # Correct credentials should login
    response = login(client, "sam")
    assert b"Login successful." in response.data
