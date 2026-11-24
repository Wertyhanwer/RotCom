import json

from tests.conftest import PASSWORD, auth, register
from tests.test_ws import send_message, ws_connect


def _chat(client, ws_url, make_user):
    alice, alice_token = make_user("alice")
    bob, bob_token = make_user("bob")
    with ws_connect(ws_url, alice_token) as a, ws_connect(ws_url, bob_token) as b:
        send_message(a, bob["id_"], "до удаления")
        b.recv(timeout=5)
    return alice, alice_token, bob, bob_token


def test_user_with_chats_can_delete_account(client, ws_url, make_user):
    alice, alice_token, bob, bob_token = _chat(client, ws_url, make_user)

    response = client.delete(f"/users/{alice['id_']}", headers=auth(alice_token))
    assert response.status_code == 200, response.text

    # у собеседника чат и история остались, но вместо Алисы — анонимный аккаунт
    chats = client.get("/chats/private/", headers=auth(bob_token)).json()
    assert len(chats) == 1
    assert chats[0]["other_user"]["username"] == "Удалённый пользователь"
    assert "alice" not in chats[0]["other_user"]["login"]
    history = client.get(f"/chats/private/{chats[0]['id_']}/history", headers=auth(bob_token)).json()
    assert [item["content"] for item in history] == ["до удаления"]


def test_deleted_account_cannot_be_used(client, ws_url, make_user):
    alice, alice_token, bob, bob_token = _chat(client, ws_url, make_user)
    client.delete(f"/users/{alice['id_']}", headers=auth(alice_token))

    assert client.get("/users/me", headers=auth(alice_token)).status_code == 401
    assert client.post("/login/", data={"username": "alice", "password": PASSWORD}).status_code == 401
    assert client.get("/users/search", params={"login": "alice"}, headers=auth(bob_token)).status_code == 404
    # и написать удалённому пользователю нельзя
    with ws_connect(ws_url, bob_token) as b:
        send_message(b, alice["id_"])
        assert json.loads(b.recv(timeout=5)) == {"error": "user not found"}


def test_login_and_email_are_freed_after_deletion(client, ws_url, make_user):
    alice, alice_token, _, _ = _chat(client, ws_url, make_user)
    client.delete(f"/users/{alice['id_']}", headers=auth(alice_token))
    new_alice = register(client, "alice")
    assert new_alice["id_"] != alice["id_"]
