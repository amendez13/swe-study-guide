# Path Operations and Routing

How FastAPI maps URLs and HTTP methods to Python functions, and how to keep the route table organized as the application grows.

## Key Points

- **Path operation decorators** — `@app.get(path)`, `@app.post(path)`, etc., bind a function to a `(method, path)` pair and capture OpenAPI metadata.
- **Signature drives the contract** — parameter types decide whether each argument comes from the path, query string, body, headers, dependencies, or files.
- **Order matters** — static paths must be declared before dynamic paths that could match them.
- **`APIRouter`** — split routes across files by domain; mount routers on the app with `app.include_router()`.
- **Prefixes and tags** — `prefix="/users"` rewrites all routes; `tags=["users"]` groups them in Swagger UI. Override per-route when needed.
- **Sub-applications** — mount one FastAPI app inside another for versioning or admin isolation; each gets its own middleware and docs.

## Example

A two-router app demonstrating decorators, signature-driven parsing, router composition, and the static-before-dynamic rule:

```python
from fastapi import APIRouter, FastAPI

# users router
users = APIRouter(prefix="/users", tags=["users"])

@users.get("/me")                            # static route — declared first
async def current_user():
    return {"username": "me"}

@users.get("/{user_id}")                     # dynamic route
async def get_user(user_id: int):            # int parsing enforced by FastAPI
    return {"id": user_id}

# books router
books = APIRouter(prefix="/books", tags=["books"])

@books.get("/")
async def list_books(limit: int = 10):       # query param: ?limit=...
    return {"limit": limit}

@books.get("/{book_id}")
async def get_book(book_id: int):
    return {"id": book_id}

# main app
app = FastAPI(title="Library API")
app.include_router(users)
app.include_router(books)
```

`GET /users/me` hits `current_user`. `GET /users/42` hits `get_user`. Swapping the order of the two `@users.get` decorators would break `/users/me` — it would route to `get_user("me")` and fail with a 422 because `"me"` isn't an int.
