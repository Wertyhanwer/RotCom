from tests.conftest import PASSWORD, auth


def test_login_with_form_body(client, make_user):
    make_user("alice")
    response = client.post("/login/", data={"username": "alice", "password": PASSWORD})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert client.get("/users/me", headers=auth(token)).status_code == 200


def test_login_by_email(client, make_user):
    make_user("alice")
    response = client.post("/login/", data={"username": "alice@example.com", "password": PASSWORD})
    assert response.status_code == 200


def test_login_wrong_password(client, make_user):
    make_user("alice")
    response = client.post("/login/", data={"username": "alice", "password": "wrong"})
    assert response.status_code == 401


def test_password_in_query_string_is_rejected(client, make_user):
    make_user("alice")
    response = client.post("/login/", params={"login": "alice", "password": PASSWORD})
    assert response.status_code == 422
