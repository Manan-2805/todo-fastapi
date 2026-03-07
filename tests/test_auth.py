from fastapi.testclient import TestClient

from conftest import auth_headers, login_user, register_user


def test_register_success(client: TestClient) -> None:
    payload = {"username": "alice", "password": "alice-password"}

    response = client.post("/register", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == payload["username"]
    assert "id" in body
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_username_returns_400(client: TestClient) -> None:
    register_user(client, "duplicate-user", "secret")

    response = client.post(
        "/register",
        json={"username": "duplicate-user", "password": "another-secret"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_login_success_returns_access_token(client: TestClient) -> None:
    register_user(client, "login-ok", "correct-password")

    response = client.post(
        "/login",
        data={"username": "login-ok", "password": "correct-password"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


def test_login_invalid_password_returns_401(client: TestClient) -> None:
    register_user(client, "login-bad", "correct-password")

    response = client.post(
        "/login",
        data={"username": "login-bad", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_unknown_user_returns_401(client: TestClient) -> None:
    response = client.post(
        "/login",
        data={"username": "missing-user", "password": "does-not-matter"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_me_requires_authentication(client: TestClient) -> None:
    response = client.get("/me")

    assert response.status_code == 401


def test_me_returns_current_user(client: TestClient) -> None:
    register_user(client, "current-user", "password")
    token = login_user(client, "current-user", "password")

    response = client.get("/me", headers=auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "current-user"
    assert "id" in body


def test_logout_behavior_invalid_or_removed_token_cannot_access_protected_route(client: TestClient) -> None:
    # The API has no dedicated /logout endpoint; production clients logout by discarding token.
    # This test validates that invalid/removed token usage cannot access protected routes.
    register_user(client, "logout-user", "password")
    token = login_user(client, "logout-user", "password")

    ok_response = client.get("/me", headers=auth_headers(token))
    assert ok_response.status_code == 200

    invalid_response = client.get("/me", headers=auth_headers(f"{token}corrupted"))
    assert invalid_response.status_code == 401

    no_token_response = client.get("/me")
    assert no_token_response.status_code == 401