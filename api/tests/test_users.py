from tests.conftest import PASSWORD, auth


def test_create_user_endpoint(client):
    response = client.post("/users/", json={
        "username": "Carol", "login": "carol", "email": "carol@example.com", "password": PASSWORD,
    })
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["login"] == "carol"
    assert body["email"] == "carol@example.com"


def test_create_user_duplicate_login_is_conflict(client, make_user):
    make_user("carol")
    response = client.post("/users/", json={
        "username": "Carol2", "login": "carol", "email": "other@example.com", "password": PASSWORD,
    })
    assert response.status_code == 409
