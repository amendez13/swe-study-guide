## Path operation decorators

The `@app.get`, `@app.post`, `@app.put`, `@app.delete`, `@app.patch`, `@app.options`, `@app.head`, and `@app.trace` decorators bind a function to a `(method, path)` pair on the FastAPI application. The decorator is what turns a plain Python function into a route handler.

```python
@app.get("/books/{id}")
async def get_book(id: int):
    return {"id": id}
```

The decorator also accepts metadata like `status_code`, `tags`, `summary`, `description`, `response_model`, and `responses` — all of which flow into the generated OpenAPI schema.

## Path operation function signature

The function signature is the API contract. FastAPI inspects each parameter and decides where to source it from based on its type and any explicit markers:

- A name that matches a placeholder in the path → path parameter.
- A Pydantic `BaseModel` → request body.
- An `UploadFile` → file upload.
- A `Depends(...)` default → injected dependency.
- Anything else with a primitive type → query parameter.

This means changing a parameter's type changes the API surface. A typo or missing type hint can silently move a parameter from "query" to "body" or vice versa.

## Route declaration order matters

FastAPI matches routes in the order they're registered. Static paths must be declared **before** dynamic paths that could match them, or the dynamic path will swallow the static one.

```python
# Right: static first
@app.get("/books/mybook")     # matches GET /books/mybook
async def my_book(): ...

@app.get("/books/{title}")    # matches everything else
async def get_book(title: str): ...

# Wrong: dynamic first — /books/mybook now hits get_book("mybook")
@app.get("/books/{title}")
async def get_book(title: str): ...

@app.get("/books/mybook")     # unreachable
async def my_book(): ...
```

## `APIRouter` for modular routing

`APIRouter` lets you split routes across files by domain (users, posts, comments, admin) and mount them on the main app. The routers are usable independently — the same router can be mounted at different prefixes, included in tests, or composed with other routers.

```python
# users.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{id}")
async def get_user(id: int): ...

# main.py
from fastapi import FastAPI
from . import users, posts

app = FastAPI()
app.include_router(users.router)
app.include_router(posts.router)
```

Without `APIRouter`, every route ends up on the `app` instance, which gets unwieldy past a handful of endpoints.

## Router prefixes and tags

`APIRouter(prefix="/users", tags=["users"])` does two things: it prepends `/users` to every path declared on the router, and it adds `users` as a Swagger tag so the endpoints are grouped together in the docs.

You can also override per-route: `@router.get("/me", tags=["users", "current-user"])`. Tags are purely documentation; they don't affect routing.

Prefixes can also be supplied at include time: `app.include_router(users.router, prefix="/v1")`, useful for API versioning without duplicating router code.

## Multiple apps and sub-applications

FastAPI apps can be mounted inside other FastAPI apps. The mounted app gets its own OpenAPI schema, middleware stack, and dependency overrides — useful for versioned APIs (`/v1`, `/v2`) or for isolating an admin surface from the public API.

```python
v1 = FastAPI()
v2 = FastAPI()

app = FastAPI()
app.mount("/v1", v1)
app.mount("/v2", v2)
```

Each sub-app appears in the parent's routing but is otherwise independent — different middleware, different dependency overrides, different Swagger UI.
