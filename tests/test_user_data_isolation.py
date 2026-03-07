from fastapi.testclient import TestClient

from conftest import auth_headers, login_user, register_user


def test_user_only_sees_own_todos(client: TestClient) -> None:
    register_user(client, "alice", "password")
    token_alice = login_user(client, "alice", "password")

    register_user(client, "bob", "password")
    token_bob = login_user(client, "bob", "password")

    create_alice = client.post(
        "/todos",
        json={"title": "Alice task", "description": "private", "completed": False},
        headers=auth_headers(token_alice),
    )
    assert create_alice.status_code == 200

    create_bob = client.post(
        "/todos",
        json={"title": "Bob task", "description": "private", "completed": False},
        headers=auth_headers(token_bob),
    )
    assert create_bob.status_code == 200

    alice_todos = client.get("/todos", headers=auth_headers(token_alice))
    bob_todos = client.get("/todos", headers=auth_headers(token_bob))

    assert alice_todos.status_code == 200
    assert bob_todos.status_code == 200
    assert [todo["title"] for todo in alice_todos.json()] == ["Alice task"]
    assert [todo["title"] for todo in bob_todos.json()] == ["Bob task"]


def test_user_cannot_read_another_users_todo_by_id(client: TestClient) -> None:
    register_user(client, "owner", "password")
    owner_token = login_user(client, "owner", "password")

    register_user(client, "other", "password")
    other_token = login_user(client, "other", "password")

    created = client.post(
        "/todos",
        json={"title": "Owner secret", "description": "hidden", "completed": False},
        headers=auth_headers(owner_token),
    )
    assert created.status_code == 200
    todo_id = created.json()["id"]

    response = client.get(f"/todos/{todo_id}", headers=auth_headers(other_token))

    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


def test_user_cannot_update_another_users_todo(client: TestClient) -> None:
    register_user(client, "owner-update", "password")
    owner_token = login_user(client, "owner-update", "password")

    register_user(client, "other-update", "password")
    other_token = login_user(client, "other-update", "password")

    created = client.post(
        "/todos",
        json={"title": "Immutable", "description": "do not touch", "completed": False},
        headers=auth_headers(owner_token),
    )
    assert created.status_code == 200
    todo_id = created.json()["id"]

    update_attempt = client.put(
        f"/todos/{todo_id}",
        json={"title": "Hacked", "description": "changed", "completed": True},
        headers=auth_headers(other_token),
    )

    assert update_attempt.status_code == 404
    assert update_attempt.json()["detail"] == "Todo not found"

    owner_read = client.get(f"/todos/{todo_id}", headers=auth_headers(owner_token))
    assert owner_read.status_code == 200
    assert owner_read.json()["title"] == "Immutable"


def test_user_cannot_delete_another_users_todo(client: TestClient) -> None:
    register_user(client, "owner-delete", "password")
    owner_token = login_user(client, "owner-delete", "password")

    register_user(client, "other-delete", "password")
    other_token = login_user(client, "other-delete", "password")

    created = client.post(
        "/todos",
        json={"title": "Protected", "description": "cannot delete", "completed": False},
        headers=auth_headers(owner_token),
    )
    assert created.status_code == 200
    todo_id = created.json()["id"]

    delete_attempt = client.delete(f"/todos/{todo_id}", headers=auth_headers(other_token))
    assert delete_attempt.status_code == 404
    assert delete_attempt.json()["detail"] == "Todo not found"

    owner_read = client.get(f"/todos/{todo_id}", headers=auth_headers(owner_token))
    assert owner_read.status_code == 200