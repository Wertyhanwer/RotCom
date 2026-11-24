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


def test_user_endpoints_require_auth(client, make_user):
    alice, _ = make_user("alice")
    uid = alice["id_"]
    assert client.get(f"/users/{uid}").status_code == 401
    assert client.patch(f"/users/{uid}", json={"username": "hacked"}).status_code == 401
    assert client.delete(f"/users/{uid}").status_code == 401


def test_cannot_modify_other_user(client, make_user):
    alice, _ = make_user("alice")
    _, bob_token = make_user("bob")
    uid = alice["id_"]
    assert client.patch(f"/users/{uid}", json={"username": "hacked"}, headers=auth(bob_token)).status_code == 403
    assert client.delete(f"/users/{uid}", headers=auth(bob_token)).status_code == 403
    # данные Алисы не изменились
    assert client.get(f"/users/{uid}", headers=auth(bob_token)).json()["username"] == "Alice"


def test_can_modify_self(client, make_user):
    alice, token = make_user("alice")
    uid = alice["id_"]
    response = client.patch(f"/users/{uid}", json={"username": "Alice Cooper"}, headers=auth(token))
    assert response.status_code == 200
    assert response.json()["username"] == "Alice Cooper"
    assert client.delete(f"/users/{uid}", headers=auth(token)).status_code == 200
