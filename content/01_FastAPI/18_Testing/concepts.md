## `TestClient`

`TestClient` runs the FastAPI app in-process and exposes a `requests`-style API for making requests against it. No real server, no network — just direct function calls under a HTTP-shaped interface.

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True}
```

It's the standard way to test FastAPI: fast, accurate (real route resolution, real dependencies, real Pydantic validation), and works inside any test runner. `httpx.AsyncClient(app=app, base_url="http://test")` is the async-native equivalent when you need to exercise async code paths.

## pytest fundamentals

pytest is the de-facto Python test runner; FastAPI examples (and most modern Python projects) assume you're using it.

```python
# test_books.py
def test_create_book(client):
    r = client.post("/books", json={"title": "x", "author": "y"})
    assert r.status_code == 201
```

```bash
pytest                          # run everything
pytest test_books.py            # run one file
pytest test_books.py::test_create_book  # run one test
pytest -v                       # verbose: show each test name
pytest -s                       # don't capture stdout (for print debugging)
pytest -k "create or update"    # filter by name expression
```

Exit codes: `0` all passed, `1` failures, `2` interrupted, `5` no tests collected. CI relies on these.

## Fixtures

`@pytest.fixture` decorates a function that produces a value (or yields one with setup/teardown). Tests declare the fixture by name in their parameters and pytest injects it.

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
```

Scope controls how often the fixture runs:

- `function` (default) — once per test; safest, slowest.
- `module` — once per file.
- `session` — once per `pytest` invocation; fastest.

Use the narrowest scope you can get away with. Sharing a fixture across tests is great until two tests stomp on each other's state.

## Parametrize

`@pytest.mark.parametrize` runs the same test body with many inputs. Each parameter set is a separate test case in the output, so a failure points to a specific input.

```python
@pytest.mark.parametrize(
    "username,password,expected_status",
    [
        ("alice", "hunter2", 200),
        ("alice", "wrong", 401),
        ("unknown", "anything", 401),
    ],
)
def test_login(client, username, password, expected_status):
    r = client.post("/token", data={"username": username, "password": password})
    assert r.status_code == expected_status
```

This is how you cover the boring permutations (empty values, edge cases, off-by-one boundaries) without copy-pasting whole test functions.

## Test database isolation

Three common strategies, in order of speed and complexity:

1. **In-memory SQLite per test session** — fast, no cleanup, but limited to SQLite's feature set (no Postgres JSONB, no `array` types).
2. **Real Postgres + transaction-per-test** — open a transaction before each test, run the test in it, roll back at the end. Realistic and fast.
3. **Real Postgres + truncate-per-test** — `TRUNCATE` every table between tests. Slower, but works when your code itself uses transactions.

```python
@pytest.fixture
def db():
    """Each test gets a clean SQLite database in memory."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Whatever you pick, the rule is: **never share state between tests**. A test that depends on another test's leftover data is a flaky test waiting to happen.

## Dependency overrides for tests

The single most useful tool for testing a FastAPI app: `app.dependency_overrides[real] = fake` swaps a dependency at the application level. Use it to replace the real database, current user, settings, or any external service with a test double.

```python
from app.config import get_settings
from app.deps import get_current_user

@pytest.fixture
def admin_client():
    app.dependency_overrides[get_current_user] = lambda: User(id=1, is_admin=True)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

Now every test using `admin_client` is authenticated as an admin without needing to log in. Clear the overrides in teardown so tests don't leak.

## Monkeypatching

For things that aren't injected via `Depends` — module-level functions, environment variables, time, randomness — use pytest's `monkeypatch` fixture. It restores the original value when the test ends.

```python
def test_external_call(monkeypatch, client):
    monkeypatch.setattr("app.services.weather.fetch", lambda city: {"temp": 20})
    monkeypatch.setenv("APP_DEBUG", "true")
    r = client.get("/weather/austin")
    assert r.json() == {"temp": 20}
```

`monkeypatch.setattr`, `monkeypatch.setenv`, `monkeypatch.delenv`, `monkeypatch.delattr` cover most cases. For mocking specific methods on real objects, `unittest.mock.patch` works too — but `monkeypatch` integrates with pytest's lifecycle.

## Unit vs integration vs system vs functional

Definitions vary by team, but a workable taxonomy:

- **Unit** — exercise a single function or class in isolation; collaborators are mocked. Fast, low-fidelity.
- **Integration** — exercise multiple modules together with real collaborators (real DB, real cache); slower, higher-fidelity.
- **System** — exercise the running, deployed app from the outside (HTTP request → real worker → real DB).
- **Functional / acceptance** — exercise a user-facing behavior end to end ("a logged-in user can create and delete a book"); usually expressed in user terms.

FastAPI's `TestClient` straddles integration and system: real router, real Pydantic, real dependencies, fake transport. Most FastAPI tests live there. Pure unit tests are for the non-routing logic (validators, repositories, business rules) that live below the route handlers.

## Async tests

If your code path is `async def`, you need `pytest-asyncio` to await it inside a test. Mark the test (or the whole module) with `@pytest.mark.asyncio`.

```python
import pytest

@pytest.mark.asyncio
async def test_async_route():
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200
```

`TestClient` runs an event loop internally so it works from sync tests too; switch to `AsyncClient` only when you need to await something in the test body itself.
