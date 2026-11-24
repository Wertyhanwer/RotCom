"""Два процесса api (как две реплики за балансировщиком) должны доставлять события друг другу."""
import json

from tests.test_ws import send_message, ws_connect


def _ws_url(base_url):
    return base_url.replace("http://", "ws://") + "/ws/"


def test_message_reaches_user_connected_to_another_instance(server, second_server, make_user):
    alice, alice_token = make_user("alice")
    bob, bob_token = make_user("bob")
    with ws_connect(_ws_url(server), alice_token) as alice_ws, \
            ws_connect(_ws_url(second_server), bob_token) as bob_ws:
        send_message(alice_ws, bob["id_"], "через другую реплику")
        event = json.loads(bob_ws.recv(timeout=5))
    assert event["content"] == "через другую реплику"


def test_tabs_on_different_instances_all_receive(server, second_server, make_user):
    alice, alice_token = make_user("alice")
    bob, bob_token = make_user("bob")
    with ws_connect(_ws_url(server), bob_token) as tab_a, \
            ws_connect(_ws_url(second_server), bob_token) as tab_b, \
            ws_connect(_ws_url(second_server), alice_token) as alice_ws:
        send_message(alice_ws, bob["id_"], "всем вкладкам")
        assert json.loads(tab_a.recv(timeout=5))["content"] == "всем вкладкам"
        assert json.loads(tab_b.recv(timeout=5))["content"] == "всем вкладкам"
