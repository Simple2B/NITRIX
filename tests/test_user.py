import pytest
from app import db, create_app
from app.models import User
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


def test_edit_user(client):
    response = client.get('/users')
    assert response.status_code == 200
    user = User(name='TEST USER NAME')
    user.password = "12345"
    user.save()
    response = client.get(f'/user_edit?id={user.id}')
    assert response.status_code == 200
    assert b'TEST USER NAME' in response.data


def test_save_user(client):
    # add new USER
    response = client.post(
        '/user_save',
        data=dict(id=-1, name='TEST USER NAME', password="12345"),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'TEST USER NAME' in response.data

    # edit exists user
    response = client.post(
        '/user_save',
        data=dict(id=2, name='ANOTHER USER NAME', password="12345"),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'TEST USER NAME' not in response.data
    assert b'ANOTHER USER NAME' in response.data
    # save user with wrong id
    response = client.post(
        '/user_save',
        data=dict(id=3, name='BAD USER NAME', password="12345"),
        follow_redirects=True
    )
    assert b'Wrong user id.' in response.data

    # send wrong form data
    response = client.post(
        '/user_save',
        data=dict(id=2, name='BAD USER NAME'),
        follow_redirects=True
    )
    assert b'Form validation error' in response.data
