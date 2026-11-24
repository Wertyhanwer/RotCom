"""Согласованность события в Mongo и превью чата в Postgres (last_message / last_event_at)."""
import json
import time
from datetime import datetime, timedelta, timezone

from tests.conftest import _mongo_db, auth, pg_execute, pg_fetch
from tests.test_ws import send_message, ws_connect


def _make_chat(client, ws_url, make_user):
    alice, alice_token = make_user("alice")
    bob, bob_token = make_user("bob")
    with ws_connect(ws_url, alice_token) as a, ws_connect(ws_url, bob_token) as b:
        send_message(a, bob["id_"], "первое")
        event = json.loads(b.recv(timeout=5))
    return alice, bob, bob_token, event["chat_id"]


def _chat_preview(chat_id):
    row = pg_fetch("SELECT last_message, last_event_at FROM private_chats WHERE id = $1", chat_id)[0]
    return row["last_message"], row["last_event_at"]


def _wait_for(predicate, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.2)
    return False


def test_sent_event_is_fully_projected(client, ws_url, make_user):
    _, _, _, chat_id = _make_chat(client, ws_url, make_user)
    assert _chat_preview(chat_id)[0] == "первое"
    mongo, db = _mongo_db()
    pending = db.chat_events.count_documents({"outbox": {"$exists": True}})
    mongo.close()
    assert pending == 0


def test_preview_is_repaired_after_crash_between_mongo_and_postgres(client, ws_url, make_user):
    """Процесс успел записать событие в Mongo и умер до обновления превью в Postgres."""
    alice, _, bob_token, chat_id = _make_chat(client, ws_url, make_user)
    now = datetime.now(timezone.utc)
    mongo, db = _mongo_db()
    db.chat_events.insert_one({
        "event_type": "message", "content": "осиротевшее", "chat_id": chat_id,
        "sender_id": alice["id_"], "created_at": now, "outbox": {"preview": "осиротевшее"},
    })

    assert _wait_for(lambda: _chat_preview(chat_id)[0] == "осиротевшее"), _chat_preview(chat_id)
    assert _wait_for(lambda: db.chat_events.count_documents({"outbox": {"$exists": True}}) == 0)
    mongo.close()
    chats = client.get("/chats/private/", headers=auth(bob_token)).json()
    assert chats[0]["last_message"] == "осиротевшее"


def test_late_projection_does_not_overwrite_newer_preview(client, ws_url, make_user):
    """Отложенная досинхронизация старого события не должна затереть более свежее превью."""
    alice, _, _, chat_id = _make_chat(client, ws_url, make_user)
    _, newer_time = _chat_preview(chat_id)
    old = (newer_time - timedelta(minutes=5)).replace(tzinfo=timezone.utc)
    mongo, db = _mongo_db()
    db.chat_events.insert_one({
        "event_type": "message", "content": "старое", "chat_id": chat_id,
        "sender_id": alice["id_"], "created_at": old, "outbox": {"preview": "старое"},
    })
    assert _wait_for(lambda: db.chat_events.count_documents({"outbox": {"$exists": True}}) == 0)
    mongo.close()
    assert _chat_preview(chat_id)[0] == "первое"


def test_postgres_failure_does_not_lose_the_message(client, ws_url, make_user):
    """Если обновить превью не удалось, сообщение всё равно сохранено и доставлено,
    а превью догоняется позже. Раньше событие в этом случае удалялось из Mongo."""
    alice, bob, bob_token, chat_id = _make_chat(client, ws_url, make_user)
    # временно ломаем UPDATE превью триггером
    pg_execute("""
        CREATE FUNCTION fail_preview() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION 'preview update is broken'; END $$ LANGUAGE plpgsql;
        CREATE TRIGGER fail_preview BEFORE UPDATE ON private_chats FOR EACH ROW EXECUTE FUNCTION fail_preview();
    """)
    try:
        with ws_connect(ws_url, client.post("/login/", data={"username": "alice", "password": "Str0ng-pass!"})
                        .json()["access_token"]) as a, ws_connect(ws_url, bob_token) as b:
            send_message(a, bob["id_"], "при сломанном Postgres")
            assert json.loads(b.recv(timeout=5))["content"] == "при сломанном Postgres"
    finally:
        pg_execute("DROP TRIGGER fail_preview ON private_chats; DROP FUNCTION fail_preview();")

    history = client.get(f"/chats/private/{chat_id}/history", headers=auth(bob_token)).json()
    assert history[0]["content"] == "при сломанном Postgres"
    assert _wait_for(lambda: _chat_preview(chat_id)[0] == "при сломанном Postgres")
