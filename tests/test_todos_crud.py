from fastapi.testclient import TestClient

from conftest import auth_headers, login_user, register_user


def _create_todo(client: TestClient, token: str, title: str, description: str, completed: bool = False) -> dict:
    response = client.post(
        "/todos",
        json={"title": title, "description": description, "completed": completed},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    return response.json()


def test_create_todo_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/todos",
        json={"title": "Task", "description": "No auth", "completed": False},
    )

    assert response.status_code == 401


def test_create_todo_success(client: TestClient) -> None:
    register_user(client, "todo-owner", "password")
    token = login_user(client, "todo-owner", "password")

    response = client.post(
        "/todos",
        json={"title": "First task", "description": "Write tests", "completed": False},
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "First task"
    assert body["description"] == "Write tests"
    assert body["completed"] is False
    assert isinstance(body["id"], int)
    assert isinstance(body["owner_id"], int)


def test_get_todos_returns_only_authenticated_users_todos(client: TestClient) -> None:
    register_user(client, "reader", "password")
    token = login_user(client, "reader", "password")
    _create_todo(client, token, "A", "Desc A")
    _create_todo(client, token, "B", "Desc B", completed=True)

    response = client.get("/todos", headers=auth_headers(token))

    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 2
    titles = {item["title"] for item in todos}
    assert titles == {"A", "B"}


def test_get_todo_by_id_success(client: TestClient) -> None:
    register_user(client, "fetch-one", "password")
    token = login_user(client, "fetch-one", "password")
    created = _create_todo(client, token, "Single", "Get by id")

    response = client.get(f"/todos/{created['id']}", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_todo_by_id_not_found_for_missing_todo(client: TestClient) -> None:
    register_user(client, "missing-reader", "password")
    token = login_user(client, "missing-reader", "password")

    response = client.get("/todos/9999", headers=auth_headers(token))

    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


def test_update_todo_success(client: TestClient) -> None:
    register_user(client, "updater", "password")
    token = login_user(client, "updater", "password")
    created = _create_todo(client, token, "Before", "Old description")

    response = client.put(
        f"/todos/{created['id']}",
        json={"title": "After", "description": "New description", "completed": True},
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["title"] == "After"
    assert body["description"] == "New description"
    assert body["completed"] is True


def test_update_todo_not_found_returns_404(client: TestClient) -> None:
    register_user(client, "missing-updater", "password")
    token = login_user(client, "missing-updater", "password")

    response = client.put(
        "/todos/9999",
        json={"title": "Nope", "description": "Missing", "completed": False},
        headers=auth_headers(token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


def test_delete_todo_success(client: TestClient) -> None:
    register_user(client, "deleter", "password")
    token = login_user(client, "deleter", "password")
    created = _create_todo(client, token, "Delete me", "To be removed")

    delete_response = client.delete(f"/todos/{created['id']}", headers=auth_headers(token))
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Todo deleted successfully"

    get_response = client.get(f"/todos/{created['id']}", headers=auth_headers(token))
    assert get_response.status_code == 404


def test_delete_todo_not_found_returns_404(client: TestClient) -> None:
    register_user(client, "missing-deleter", "password")
    token = login_user(client, "missing-deleter", "password")

    response = client.delete("/todos/9999", headers=auth_headers(token))

    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"