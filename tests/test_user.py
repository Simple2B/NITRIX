import pytest
from flask import url_for
from app import db, create_app
from app.models import User
from .test_auth import register, login, logout


TEST_USER_NAME = 'Test-User'
TEST_USER_TYPE = User.Type.super_admin


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
        register('admin')
        # Login by test user
        login(client, 'admin')
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_edit_user(client):
    response = client.get(url_for('main.users'))
    assert response.status_code == 200
    user = User(name='TEST USER NAME')
    user.password = "12345"
    user.save()
    response = client.get(url_for('user.edit', id=user.id))
    assert response.status_code == 200
    assert b'TEST USER NAME' in response.data


def test_save_user(client):
    # add new USER
    response = client.post(
        url_for('user.save'),
        data=dict(id=-1, name='TEST USER NAME', password="12345"),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'TEST USER NAME' in response.data

    # edit exists user
    response = client.post(
        url_for('user.save'),
        data=dict(id=2, name='ANOTHER USER NAME', password="12345"),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'TEST USER NAME' not in response.data
    assert b'ANOTHER USER NAME' in response.data
    # save user with wrong id
    response = client.post(
        url_for('user.save'),
        data=dict(id=3, name='BAD USER NAME', password="12345"),
        follow_redirects=True
    )
    assert b'Wrong user id.' in response.data

    # send wrong form data
    response = client.post(
        url_for('user.save'),
        data=dict(id=2, name='BAD USER NAME'),
        follow_redirects=True
    )
    assert b'Form validation error' in response.data


def test_delete_user(client):
    user_id = register(TEST_USER_NAME)
    res = client.get(url_for('main.users'))
    assert res.status_code == 200
    assert f'{TEST_USER_NAME}'.encode() in res.data
    res = client.get(url_for('user.delete', id=user_id))
    assert res.status_code == 302  # redirected to main.users
    assert f'{TEST_USER_NAME}'.encode() not in res.data
    # try delete user w/o authorization
    user_id = register(TEST_USER_NAME)
    logout(client)
    res = client.get(url_for('user.delete', id=user_id))
    assert res.status_code == 302  # redirected to main.users
    login(client, 'admin')
    res = client.get(url_for('main.users'))
    assert f'{TEST_USER_NAME}'.encode() in res.data
