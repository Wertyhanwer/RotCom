from tests.conftest import auth


def test_register_login_and_me(client, make_user):
    user, token = make_user("alice")
    response = client.get("/users/me", headers=auth(token))
    assert response.status_code == 200
    assert response.json()["id_"] == user["id_"]


def test_chat_history_roundtrip_over_rest(client, make_user):
    alice, alice_token = make_user("alice")
    bob, _ = make_user("bob")
    # чат создаётся при первом WS-событии, для REST-проверки создаём его напрямую
    from tests.conftest import pg_execute
    pg_execute(f"INSERT INTO private_chats (user1_id, user2_id) VALUES ({alice['id_']}, {bob['id_']})")

    chats = client.get("/chats/private/", headers=auth(alice_token)).json()
    assert len(chats) == 1
    chat_id = chats[0]["id_"]

    created = client.post(f"/chats/private/{chat_id}/calls", params={"status": "missed", "duration": 0},
                          headers=auth(alice_token))
    assert created.status_code == 200, created.text

    history = client.get(f"/chats/private/{chat_id}/history", headers=auth(alice_token))
    assert history.status_code == 200, history.text
    assert [item["event_type"] for item in history.json()] == ["call"]
