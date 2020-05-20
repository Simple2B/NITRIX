import pytest
from app import db, create_app
from app.models import User


@pytest.fixture
def client():
    app = create_app(environment='testing')
    app.config['TESTING'] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def register(user_name, password='password'):
    # noinspection PyArgumentList
    user = User(name=user_name, password=password)
    user.save()


def login(client, user_name, password='password'):
    return client.post(
        '/login', data=dict(user_name=user_name, password=password),
        follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_index_page(client):
    # register test user.
    register('sam')
    # Login by test user
    response = login(client, 'sam')
    assert b'Login successful.' in response.data
    response = client.get('/accounts')
    assert response.status_code == 200


def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200


def test_login_and_logout(client):
    # Access to logout view before login should fail.
    response = logout(client)
    assert b'Please log in to access this page.' in response.data
    # register test user.
    register('sam')
    # Login by test user
    response = login(client, 'sam')
    assert b'Login successful.' in response.data
    # Should successfully logout the currently logged in user.
    response = logout(client)
    assert b'You were logged out.' in response.data
    # Incorrect login credentials should fail.
    response = login(client, 'sam', 'wrongpassword')
    assert b'Wrong user name or password.' in response.data
    # Correct credentials should login
    response = login(client, 'sam')
    assert b'Login successful.' in response.data
