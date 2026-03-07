from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register():
    response = client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code in (200, 400)  # 400 if already exists

def test_login():
    client.post("/register", json={"username": "testuser2", "password": "testpass"})
    response = client.post("/login", data={"username": "testuser2", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()