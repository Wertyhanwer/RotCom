from tests.conftest import PASSWORD, auth


def test_login_with_form_body(client, make_user):
    make_user("alice")
    response = client.post("/login/", data={"username": "alice", "password": PASSWORD})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert client.get("/users/me", headers=auth(token)).status_code == 200


def test_login_by_email(client, make_user):
    make_user("alice")
    response = client.post("/login/", data={"username": "alice@example.com", "password": PASSWORD})
    assert response.status_code == 200


def test_login_wrong_password(client, make_user):
    make_user("alice")
    response = client.post("/login/", data={"username": "alice", "password": "wrong"})
    assert response.status_code == 401


def test_password_in_query_string_is_rejected(client, make_user):
    make_user("alice")
    response = client.post("/login/", params={"login": "alice", "password": PASSWORD})
    assert response.status_code == 422


def test_concurrent_registration_same_login_gives_409_not_500(server):
    import threading
    import httpx

    statuses = []
    barrier = threading.Barrier(6)

    def register_once(i):
        barrier.wait()
        response = httpx.post(f"{server}/registration/", timeout=30, json={
            "username": "Dup", "login": "dup", "email": f"dup{i}@example.com", "password": PASSWORD})
        statuses.append(response.status_code)

    threads = [threading.Thread(target=register_once, args=(i,)) for i in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(statuses) == [200, 409, 409, 409, 409, 409]
