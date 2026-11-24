import json

import pytest
from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect

from tests.conftest import auth


def ws_open(ws_url):
    """Соединение без аутентификации."""
    return connect(ws_url, open_timeout=5, close_timeout=2)


def ws_connect(ws_url, token):
    """Соединение + аутентификация первым сообщением (токен не передаётся в URL)."""
    ws = ws_open(ws_url)
    ws.send(json.dumps({"type": "auth", "token": token}))
    reply = json.loads(ws.recv(timeout=5))
    assert reply["type"] == "auth_ok", reply
    return ws


def assert_closed_with_policy_violation(ws):
    with pytest.raises(ConnectionClosed) as exc:
        ws.recv(timeout=5)
    assert exc.value.rcvd.code == 1008


def send_message(ws, to_user_id, content="hi"):
    ws.send(json.dumps({"event_type": "message", "to_user_id": to_user_id, "content": content}))


def test_message_is_delivered_and_saved(client, ws_url, make_user):
    alice, alice_token = make_user("alice")
    bob, bob_token = make_user("bob")
    with ws_connect(ws_url, alice_token) as alice_ws, ws_connect(ws_url, bob_token) as bob_ws:
        send_message(alice_ws, bob["id_"], "привет")
        event = json.loads(bob_ws.recv(timeout=5))
    assert event["event_type"] == "message"
    assert event["content"] == "привет"
    assert event["from_user_id"] == alice["id_"]

    history = client.get(f"/chats/private/{event['chat_id']}/history", headers=auth(bob_token)).json()
    assert [item["content"] for item in history] == ["привет"]


@pytest.mark.parametrize("token", ["garbage", "a.b.c"])
def test_invalid_token_closes_with_policy_violation(ws_url, token):
    with ws_open(ws_url) as ws:
        ws.send(json.dumps({"type": "auth", "token": token}))
        assert_closed_with_policy_violation(ws)


def test_token_in_query_string_is_not_accepted(ws_url, make_user):
    """Токен в URL попадает в логи прокси, поэтому сервер его больше не читает."""
    _, token = make_user("alice")
    with connect(f"{ws_url}?token={token}", open_timeout=5, close_timeout=2) as ws:
        # без auth-сообщения соединение закрывается по таймауту аутентификации
        assert_closed_with_policy_violation(ws)


def test_first_message_must_be_auth(ws_url, make_user):
    bob, _ = make_user("bob")
    with ws_open(ws_url) as ws:
        send_message(ws, bob["id_"])
        assert_closed_with_policy_violation(ws)


def test_refresh_token_is_not_accepted_for_ws(client, ws_url, make_user):
    make_user("alice")
    tokens = client.post("/login/", data={"username": "alice", "password": "Str0ng-pass!"}).json()
    with ws_open(ws_url) as ws:
        ws.send(json.dumps({"type": "auth", "token": tokens["refresh_token"]}))
        assert_closed_with_policy_violation(ws)


def test_cannot_message_yourself(client, ws_url, make_user):
    alice, alice_token = make_user("alice")
    with ws_connect(ws_url, alice_token) as ws:
        send_message(ws, alice["id_"])
        assert "error" in json.loads(ws.recv(timeout=5))
    assert client.get("/chats/private/", headers=auth(alice_token)).json() == []


def test_two_tabs_of_same_user_both_receive(ws_url, make_user):
    alice, alice_token = make_user("alice")
    bob, bob_token = make_user("bob")
    with ws_connect(ws_url, bob_token) as tab1, ws_connect(ws_url, bob_token) as tab2, \
            ws_connect(ws_url, alice_token) as alice_ws:
        send_message(alice_ws, bob["id_"], "one")
        assert json.loads(tab1.recv(timeout=5))["content"] == "one"
        assert json.loads(tab2.recv(timeout=5))["content"] == "one"


def test_closing_old_tab_keeps_new_tab_connected(ws_url, make_user):
    alice, alice_token = make_user("alice")
    bob, bob_token = make_user("bob")
    with ws_connect(ws_url, bob_token) as new_tab, ws_connect(ws_url, alice_token) as alice_ws:
        old_tab = ws_connect(ws_url, bob_token)
        old_tab.close()
        send_message(alice_ws, bob["id_"], "still here?")
        assert json.loads(new_tab.recv(timeout=5))["content"] == "still here?"


def test_client_disconnect_is_not_logged_as_error(server_log, ws_url, make_user):
    import time
    _, token = make_user("alice")
    log_path = server_log
    before = log_path.read_text(encoding="utf-8", errors="replace").count("Exception in ASGI application")
    ws = ws_connect(ws_url, token)
    ws.close()
    time.sleep(0.5)
    after = log_path.read_text(encoding="utf-8", errors="replace").count("Exception in ASGI application")
    assert after == before
