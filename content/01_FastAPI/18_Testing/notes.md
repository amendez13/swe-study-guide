# Testing

How to test a FastAPI app efficiently — fast feedback, accurate results, no flakes.

## Key Points

- **`TestClient`** runs the app in-process and gives you a `requests`-style API; the default tool for FastAPI tests.
- **pytest** is the assumed runner; learn `-v`, `-s`, `-k`, and the exit codes for CI.
- **Fixtures** give you injectable setup/teardown with controllable scope (`function`/`module`/`session`).
- **`parametrize`** covers permutations without duplicating test bodies; each parameter set is a distinct test case in the output.
- **DB isolation** — pick in-memory SQLite, transaction-per-test, or truncate-per-test; whichever you pick, never share state.
- **`app.dependency_overrides`** is the canonical way to swap real services (DB, current user, settings) for fakes.
- **`monkeypatch`** handles things outside the DI system: module-level functions, env vars, time.
- **Test pyramid** — unit (isolated function), integration (multiple modules), system (deployed app), functional (user behavior). `TestClient` tests straddle integration and system.
- **Async tests** — `pytest-asyncio` + `httpx.AsyncClient(app=app, ...)` when you need to `await` inside the test.

## Example

A `conftest.py` with reusable fixtures plus a test file showing every pattern in one place:

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import Settings, get_settings
from app.db import Base, get_db
from app.deps import get_current_user
from app.main import app
from app.models import User


@pytest.fixture
def settings():
    return Settings(
        env="test",
        database_url="sqlite:///:memory:",
        jwt_secret="test-secret",
    )


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(settings, db):
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(client):
    app.dependency_overrides[get_current_user] = lambda: User(
        id=1, username="admin", is_admin=True
    )
    yield client
    # The outer client fixture's teardown clears overrides
```

```python
# test_books.py
import pytest


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200


@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"title": "x", "author": "y"}, 201),
        ({"title": "", "author": "y"}, 422),    # title too short
        ({"author": "y"}, 422),                  # title missing
    ],
)
def test_create_book_validation(client, payload, expected_status):
    r = client.post("/books", json=payload)
    assert r.status_code == expected_status


def test_admin_can_delete(admin_client):
    admin_client.post("/books", json={"title": "x", "author": "y"})
    r = admin_client.delete("/books/1")
    assert r.status_code == 204


def test_non_admin_cannot_delete(client):
    r = client.delete("/books/1")    # no current-user override → 401
    assert r.status_code == 401


def test_external_call_is_mocked(monkeypatch, client):
    monkeypatch.setattr(
        "app.services.weather.fetch",
        lambda city: {"city": city, "temp": 20},
    )
    r = client.get("/weather/austin")
    assert r.json() == {"city": "austin", "temp": 20}


@pytest.mark.asyncio
async def test_async_route():
    from httpx import AsyncClient
    from app.main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200
```

`pytest -v` runs the whole file; each parametrize case shows up as its own line, the admin/non-admin tests use different fixtures to swap the current user, and `monkeypatch` keeps `test_external_call_is_mocked` from making real HTTP calls.
