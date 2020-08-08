import pytest
from flask import url_for
from app import create_app, db
from app.models import AccountExtension, Account, Product, Phone, Reseller
from datetime import datetime
from .test_auth import register, login, logout
from .mock_db import create_mock_db

app = create_app(environment="testing")
app.config["TESTING"] = True  # why do we need the here?

@pytest.fixture
def client():
    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        create_mock_db()
        register(LOGIN)  # register a test user.
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()