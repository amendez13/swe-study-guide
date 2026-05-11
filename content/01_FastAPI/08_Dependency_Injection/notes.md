# Dependency Injection

FastAPI's dependency injection system is how cross-cutting concerns (auth, DB sessions, settings, pagination, rate limiting) stay out of route handlers. Once you understand `Depends()`, most production patterns fall out of it.

## Key Points

- **`Depends(callable)`** computes a value by calling another function/class and passes it as a parameter; the dependency's own parameters become part of the route's request signature.
- **Reusable** — define a dependency once, use it on every route that needs it.
- **Sub-dependencies** — dependencies declare dependencies; FastAPI walks the graph and caches each result per request.
- **`yield` dependencies** — code before `yield` runs as setup, code after runs as teardown (even on exceptions); the standard pattern for DB sessions and file handles.
- **`app.dependency_overrides`** swaps a dependency at the app level for tests.
- **Class-based dependencies** — any callable, including class instances with `__call__`, works as a dependency; useful for configured services like rate limiters.

## Example

A small auth + DB stack showing sub-dependencies, `yield` cleanup, and a class-based rate limiter — plus a test override:

```python
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

engine = create_engine("sqlite:///./test.db")
SessionLocal = sessionmaker(bind=engine)

app = FastAPI()


# yield dependency — runs cleanup even on errors
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# sub-dependency — uses get_db
def get_current_user(token: str | None = None, db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(401, "missing token")
    user = db.query(User).filter_by(token=token).first()
    if user is None:
        raise HTTPException(401, "invalid token")
    return user


# sub-dependency — uses get_current_user
def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(403, "admin required")
    return user


# class-based dependency for rate limiting
class RateLimiter:
    def __init__(self, rpm: int):
        self.rpm = rpm

    def __call__(self, request: Request) -> None:
        if exceeds_limit(request.client.host, self.rpm):
            raise HTTPException(429, "rate limited")


limiter = RateLimiter(60)


@app.delete("/users/{id}", dependencies=[Depends(limiter)])
async def delete_user(
    id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),     # cached — same session as get_current_user
):
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(404)
    db.delete(user)
    db.commit()


# test override — swap the DB for an in-memory fake
def get_test_db():
    db = make_in_memory_session()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = get_test_db
```

When `DELETE /users/42` comes in, FastAPI resolves the graph: `get_db` opens a session, `get_current_user` uses it to look up the user, `require_admin` checks the flag, `RateLimiter` runs as a side effect via `dependencies=[...]`, and the handler reuses the same session. After the response is sent, `get_db`'s `finally` closes it.
