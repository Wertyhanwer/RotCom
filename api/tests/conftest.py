"""Интеграционные тесты: настоящий uvicorn поверх тестовых Postgres и Mongo.

Перед запуском нужны тестовые базы:
    docker compose --profile test up -d db_test mongo_test redis_test

Параметры подключения берутся из TEST_* переменных окружения (значения по умолчанию
совпадают с test_db/Dockerfile и сервисом mongo_test в docker-compose.yaml).
Схема Postgres пересоздаётся через `alembic upgrade head` — так тесты заодно проверяют миграции.
"""
import asyncio
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import asyncpg
import httpx
import pytest
from pymongo import MongoClient

API_DIR = Path(__file__).resolve().parent.parent

PG = {
    "host": os.getenv("TEST_DB_HOST", "localhost"),
    "port": os.getenv("TEST_DB_PORT", "5434"),
    "database": os.getenv("TEST_DB_NAME", "TEST_rotcom"),
    "user": os.getenv("TEST_DB_USER", "user"),
    "password": os.getenv("TEST_DB_PASSWORD", "12345"),
}
MONGO = {
    "host": os.getenv("TEST_MONGO_HOST", "localhost"),
    "port": os.getenv("TEST_MONGO_PORT", "27019"),
    "db": os.getenv("TEST_MONGO_DB", "rotcom_test"),
    "user": os.getenv("TEST_MONGO_USER", "rotcom"),
    "password": os.getenv("TEST_MONGO_PASSWORD", "12345"),
}
REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6380/0")
PASSWORD = "Str0ng-pass!"


def _server_env() -> dict:
    env = os.environ.copy()
    env.update({
        "DB_HOST": PG["host"], "DB_PORT": PG["port"], "DB_NAME": PG["database"],
        "DB_USER": PG["user"], "DB_PASSWORD": PG["password"],
        "MONGO_HOST": MONGO["host"], "MONGO_PORT": MONGO["port"], "MONGO_DB": MONGO["db"],
        "MONGO_USER": MONGO["user"], "MONGO_PASSWORD": MONGO["password"],
        "JWT_SECRET_KEY": "test-secret-key-that-is-long-enough-for-hs256",
        "PYTHONUTF8": "1",
        # короткий таймаут, чтобы тест «нет auth-сообщения» не ждал 10 секунд
        "WS_AUTH_TIMEOUT": "1",
        "REDIS_URL": REDIS_URL,
    })
    return env


async def _pg_execute(sql: str):
    conn = await asyncpg.connect(**PG)
    try:
        await conn.execute(sql)
    finally:
        await conn.close()


def pg_execute(sql: str):
    asyncio.run(_pg_execute(sql))


async def _pg_fetch(sql: str, *args):
    conn = await asyncpg.connect(**PG)
    try:
        return await conn.fetch(sql, *args)
    finally:
        await conn.close()


def pg_fetch(sql: str, *args):
    return asyncio.run(_pg_fetch(sql, *args))


def _mongo_db():
    client = MongoClient(host=MONGO["host"], port=int(MONGO["port"]),
                         username=MONGO["user"], password=MONGO["password"], authSource="admin")
    return client, client[MONGO["db"]]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def server():
    env = _server_env()

    pg_execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    client, db = _mongo_db()
    client.drop_database(db.name)
    client.close()

    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                   cwd=API_DIR, env=env, check=True, capture_output=True)

    proc, base_url = _start_uvicorn(env)
    yield base_url
    _stop(proc)


@pytest.fixture(scope="session")
def second_server(server):
    """Второй независимый процесс api на тех же базах и том же Redis — как вторая реплика."""
    proc, base_url = _start_uvicorn(_server_env())
    yield base_url
    _stop(proc)


def _start_uvicorn(env: dict):
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=API_DIR, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            if httpx.get(f"{base_url}/openapi.json", timeout=1).status_code == 200:
                return proc, base_url
        except httpx.HTTPError:
            pass
        if proc.poll() is not None:
            raise RuntimeError("uvicorn exited during startup")
        time.sleep(0.2)
    proc.kill()
    raise RuntimeError("uvicorn did not start")


def _stop(proc):
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(autouse=True)
def clean_db(server):
    pg_execute("TRUNCATE users, private_chats RESTART IDENTITY CASCADE")
    client, db = _mongo_db()
    db.chat_events.delete_many({})
    client.close()


@pytest.fixture
def client(server):
    with httpx.Client(base_url=server, timeout=10) as c:
        yield c


@pytest.fixture
def ws_url(server):
    return server.replace("http://", "ws://") + "/ws/"


def register(client: httpx.Client, login: str, password: str = PASSWORD) -> dict:
    response = client.post("/registration/", json={
        "username": login.capitalize(), "login": login,
        "email": f"{login}@example.com", "password": password,
    })
    assert response.status_code == 200, response.text
    return response.json()


def get_token(client: httpx.Client, login: str, password: str = PASSWORD) -> str:
    response = client.post("/login/", data={"username": login, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def make_user(client):
    """Регистрирует пользователя и возвращает (user, token)."""
    def _make(login: str):
        user = register(client, login)
        return user, get_token(client, login)
    return _make
