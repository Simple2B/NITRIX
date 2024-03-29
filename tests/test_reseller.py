import pytest
from app import db, create_app
from app.models import Reseller, HistoryChange
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


def test_edit_reseller(client):
    response = client.get("/resellers")
    assert response.status_code == 200
    reseller = Reseller(name="TEST RESELLER NAME")
    reseller.save()
    response = client.get(f"/reseller_edit?id={reseller.id}")
    assert response.status_code == 200
    assert b"TEST RESELLER NAME" in response.data


def test_save_reseller(client):
    # add new reseller
    response = client.post(
        "/reseller_save",
        data=dict(id=-1, name="TEST RESELLER NAME", status="not_active"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"TEST RESELLER NAME" in response.data
    # edit exists reseller
    response = client.post(
        "/reseller_save",
        data=dict(
            id=1, name="ANOTHER RESELLER NAME", status="not_active", submit="save"
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"TEST RESELLER NAME" not in response.data
    assert b"ANOTHER RESELLER NAME" in response.data
    history = HistoryChange.query.filter(HistoryChange.item_id == 1).all()
    assert len(history) == 2
    assert history[1].before_value_str == "TEST RESELLER NAME"
    assert history[1].after_value_str == "ANOTHER RESELLER NAME"
    assert history[1].change_type == HistoryChange.EditType.changes_reseller
    # save reseller with wrong id
    response = client.post(
        "/reseller_save",
        data=dict(id=2, name="BAD RESELLER NAME", status="not_active"),
        follow_redirects=True,
    )
    assert b"Wrong reseller id." in response.data
    history = HistoryChange.query.filter(HistoryChange.item_id == 1).all()
    assert len(history) == 2
    # send wrong form data
    response = client.post(
        "/reseller_save",
        data=dict(id=1, name="BAD RESELLER NAME", status=123),
        follow_redirects=True,
    )
    assert b"Form validation error" in response.data


def test_save_reseller_with_same_name(client):
    # add new reseller
    response = client.post(
        "/reseller_save",
        data=dict(id=-1, name="TEST RESELLER NAME", status="not_active"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"TEST RESELLER NAME" in response.data
    history = HistoryChange.query.filter(HistoryChange.item_id == 1).all()
    assert len(history) == 1
    assert history[0].change_type == HistoryChange.EditType.creation_reseller
    # add reseller with the same name
    response = client.post(
        "/reseller_save",
        data=dict(id=-1, name="TEST RESELLER NAME", status="not_active"),
        follow_redirects=True,
    )
    assert b"This name is already taken" in response.data
    history = HistoryChange.query.filter(HistoryChange.item_id == 1).all()
    assert len(history) == 1


def test_delete_reseller(client):
    # delete certain reseller
    response = client.post(
        "/reseller_save",
        data=dict(id=-1, name="TEST RESELLER NAME", status="active"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    reseller = Reseller.query.first()
    assert reseller
    reseller_id = reseller.id
    response = client.get(f"/reseller_delete?id={reseller_id}")
    assert response.status_code == 302
    assert reseller.deleted
    history = HistoryChange.query.filter(HistoryChange.item_id == 1).all()
    assert len(history) == 2
    assert history[1].change_type == HistoryChange.EditType.deletion_reseller
