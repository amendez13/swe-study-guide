# Dependency Injection

Placeholder notes for FastAPI dependency injection.

## Key Points

- `Depends()` declares a dependency in a route function signature
- Dependencies can themselves have dependencies (nested/chained)
- Use `yield` in a dependency for setup/teardown (e.g. DB sessions)
- Class-based dependencies enable reusable, configurable logic

## Example

```python
from fastapi import Depends, FastAPI

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
async def list_users(db=Depends(get_db)):
    return db.query(User).all()
```
