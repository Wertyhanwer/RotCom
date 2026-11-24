import time

import jwt

from tests.conftest import PASSWORD, auth

JWT_SECRET = "test-secret-key-that-is-long-enough-for-hs256"


def login(client, login_name="alice"):
    response = client.post("/login/", data={"username": login_name, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return response.json()


def test_login_returns_access_and_refresh(client, make_user):
    make_user("alice")
    tokens = login(client)
    assert tokens["access_token"] and tokens["refresh_token"]
    assert jwt.decode(tokens["refresh_token"], JWT_SECRET, algorithms=["HS256"])["type"] == "refresh"


def test_refresh_rotates_tokens(client, make_user):
    make_user("alice")
    tokens = login(client)
    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200, response.text
    new = response.json()
    assert new["refresh_token"] != tokens["refresh_token"]
    assert client.get("/users/me", headers=auth(new["access_token"])).status_code == 200


def test_reused_refresh_token_revokes_the_whole_family(client, make_user):
    make_user("alice")
    old = login(client)["refresh_token"]
    new = client.post("/auth/refresh", json={"refresh_token": old}).json()["refresh_token"]
    # повторное использование уже обменянного токена — признак кражи
    assert client.post("/auth/refresh", json={"refresh_token": old}).status_code == 401
    assert client.post("/auth/refresh", json={"refresh_token": new}).status_code == 401


def test_logout_revokes_refresh_token(client, make_user):
    make_user("alice")
    tokens = login(client)
    assert client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]}).status_code == 204
    assert client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401


def test_token_types_are_not_interchangeable(client, make_user):
    make_user("alice")
    tokens = login(client)
    assert client.get("/users/me", headers=auth(tokens["refresh_token"])).status_code == 401
    assert client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]}).status_code == 401


def test_deleted_user_cannot_refresh(client, make_user):
    user, _ = make_user("alice")
    tokens = login(client)
    client.delete(f"/users/{user['id_']}", headers=auth(tokens["access_token"]))
    assert client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401


def test_forged_refresh_token_is_rejected(client, make_user):
    user, _ = make_user("alice")
    forged = jwt.encode({"sub": str(user["id_"]), "type": "refresh", "exp": int(time.time()) + 600,
                         "jti": "not-in-database"}, JWT_SECRET, algorithm="HS256")
    assert client.post("/auth/refresh", json={"refresh_token": forged}).status_code == 401
