import json

import pytest
from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect

from tests.conftest import auth


def ws_connect(ws_url, token):
    return connect(f"{ws_url}?token={token}", open_timeout=5, close_timeout=2)


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
    with ws_connect(ws_url, token) as ws:
        with pytest.raises(ConnectionClosed) as exc:
            ws.recv(timeout=5)
    assert exc.value.rcvd.code == 1008


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
