## `Depends()`

`Depends(callable)` tells FastAPI to call `callable` and pass the result as the parameter's value. The callable can be a function, an async function, or any class instance with `__call__`. FastAPI resolves the dependency graph fresh on every request.

```python
from fastapi import Depends

def pagination(limit: int = 10, offset: int = 0):
    return {"limit": limit, "offset": offset}

@app.get("/books")
async def list_books(page: dict = Depends(pagination)):
    return page
```

The dependency function's own parameters (`limit`, `offset` above) become part of the route's request signature — they show up in Swagger UI as query parameters on the calling route.

## Reusable dependencies

Once a dependency is defined, every route can use it. This is how you avoid copy-pasting boilerplate for cross-cutting concerns like pagination, authentication, database sessions, settings, and rate limiting.

```python
def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(403, "admin required")
    return user

@app.delete("/users/{id}")
async def delete_user(id: int, admin: User = Depends(require_admin)):
    ...
```

The pattern: write the dependency once, declare it on every route that needs it, and FastAPI handles the wiring.

## Sub-dependencies

A dependency can itself declare dependencies. FastAPI walks the graph, calling each dependency at most once per request, and caches the result so multiple routes (or dependencies of dependencies) sharing the same dependency don't recompute it.

```python
def get_db() -> Session: ...
def get_current_user(db: Session = Depends(get_db)): ...
def require_admin(user = Depends(get_current_user)): ...

@app.delete("/x")
async def delete_x(admin = Depends(require_admin), db = Depends(get_db)):
    # get_db ran once; both the handler and get_current_user share the session
    ...
```

This is what makes the dependency system practical — a chain of three or four dependencies still results in one DB session, one user lookup, and one auth check per request.

## Yielding dependencies

Use `yield` instead of `return` when the dependency needs setup/teardown around the request. The code before `yield` runs before the handler; the code after runs once the response is sent (even if the handler raised).

```python
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@app.get("/items")
async def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

This is the standard pattern for database sessions, file handles, lock acquisitions, and anything else that needs deterministic cleanup. Async variant: `async def` with `yield` works the same way.

## Dependency overrides in tests

`app.dependency_overrides[real_dep] = fake_dep` swaps a dependency at the application level — useful for replacing the database with an in-memory fake, mocking the current user, or short-circuiting external APIs in tests.

```python
def get_settings(): return Settings()
def fake_settings(): return Settings(debug=True, jwt_secret="test")

app.dependency_overrides[get_settings] = fake_settings
```

The override is applied for the whole app, not per request, so tests typically set the override in a fixture, run the test, and clear `dependency_overrides` afterward.

## Class-based dependencies

Any callable works as a dependency, including class instances with `__call__`. This is useful when the dependency needs configurable state (a feature flag, a rate-limit window, a service client) without leaking globals.

```python
class RateLimiter:
    def __init__(self, requests_per_minute: int):
        self.rpm = requests_per_minute

    def __call__(self, request: Request) -> None:
        if exceeds_limit(request.client.host, self.rpm):
            raise HTTPException(429, "rate limited")

limiter = RateLimiter(60)

@app.get("/expensive", dependencies=[Depends(limiter)])
async def expensive():
    ...
```

Note the `dependencies=[...]` argument on the decorator — useful when the dependency runs for its side effect (auth check, rate limit, logging) and the result isn't needed by the handler.
