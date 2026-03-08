import os
import time
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Ensure app imports use the SQLite test database instead of local/dev Postgres.
TEST_DB_PATH = Path(__file__).resolve().parent / "test_app.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

from app.database import Base, get_db
from app.main import app

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_database_file() -> Generator[None, None, None]:
    yield
    engine.dispose()
    if TEST_DB_PATH.exists():
        for _ in range(5):
            try:
                TEST_DB_PATH.unlink()
                break
            except PermissionError:
                time.sleep(0.1)


def register_user(client: TestClient, username: str, password: str) -> dict:
    response = client.post("/register", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()


def login_user(client: TestClient, username: str, password: str) -> str:
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token
    return token


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}