"""CORS: фронтенд ходит в api через nginx с того же origin, чужим сайтам доступ не нужен."""

PREFLIGHT = {"Access-Control-Request-Method": "GET", "Access-Control-Request-Headers": "authorization"}


def test_unknown_origin_is_not_allowed(client):
    response = client.options("/users/me", headers={"Origin": "https://evil.example", **PREFLIGHT})
    assert "access-control-allow-origin" not in response.headers
    response = client.get("/users/me", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in response.headers


def test_configured_origin_is_allowed_without_credentials(client):
    response = client.options("/users/me", headers={"Origin": "http://allowed.example", **PREFLIGHT})
    assert response.headers.get("access-control-allow-origin") == "http://allowed.example"
    # авторизация через заголовок Authorization, куки не используются
    assert "access-control-allow-credentials" not in response.headers
