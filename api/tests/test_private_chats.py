import json
import threading

import asyncpg
import pytest

from tests.conftest import auth, pg_execute, pg_fetch
from tests.test_ws import send_message, ws_connect


def test_concurrent_first_messages_create_single_chat(client, ws_url, make_user):
    """Несколько вкладок одновременно пишут первое сообщение — чат должен получиться один."""
    alice, alice_token = make_user("alice")
    bob, bob_token = make_user("bob")
    sockets = [ws_connect(ws_url, alice_token) for _ in range(4)] + \
              [ws_connect(ws_url, bob_token) for _ in range(4)]
    barrier = threading.Barrier(len(sockets))

    def fire(ws, to_user_id):
        barrier.wait()
        send_message(ws, to_user_id, "race")

    threads = [threading.Thread(target=fire, args=(ws, bob["id_"] if i < 4 else alice["id_"]))
               for i, ws in enumerate(sockets)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # каждая вкладка получит 4 события от собеседника; ошибок быть не должно
    for ws in sockets:
        for _ in range(4):
            assert "error" not in json.loads(ws.recv(timeout=10))
        ws.close()

    rows = pg_fetch("SELECT count(*) AS n FROM private_chats")
    assert rows[0]["n"] == 1
    chat_id = client.get("/chats/private/", headers=auth(alice_token)).json()[0]["id_"]
    history = client.get(f"/chats/private/{chat_id}/history", headers=auth(bob_token)).json()
    assert len(history) == 8


def test_duplicate_pair_is_rejected_by_database(make_user):
    alice, _ = make_user("alice")
    bob, _ = make_user("bob")
    pg_execute(f"INSERT INTO private_chats (user1_id, user2_id) VALUES ({alice['id_']}, {bob['id_']})")
    with pytest.raises(asyncpg.UniqueViolationError):
        pg_execute(f"INSERT INTO private_chats (user1_id, user2_id) VALUES ({alice['id_']}, {bob['id_']})")


def test_chat_lookup_indexes_exist():
    indexes = {row["indexname"] for row in pg_fetch(
        "SELECT indexname FROM pg_indexes WHERE tablename = 'private_chats'")}
    assert "uq_private_chats_users" in indexes
    assert "ix_private_chats_user2_id" in indexes
