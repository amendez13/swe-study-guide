## ASGI vs WSGI

WSGI (Web Server Gateway Interface) is the synchronous Python web standard used by Flask and classic Django. ASGI (Asynchronous Server Gateway Interface) extends WSGI to support `async`/`await`, WebSockets, and long-lived connections.

FastAPI is built on ASGI, which is why `async def` path operations can cooperatively handle many concurrent requests on a single worker. A WSGI app blocks the whole worker on each request; an ASGI app yields back to the event loop on every `await`.

## The `FastAPI` application instance

The root object you instantiate once at the top of your app. It holds the route table, middleware stack, exception handlers, dependency overrides, and OpenAPI metadata — everything else attaches to it.

```python
from fastapi import FastAPI

app = FastAPI(
    title="Books API",
    version="0.1.0",
    description="A minimal FastAPI app.",
)

@app.get("/")
async def root():
    return {"hello": "world"}
```

## Uvicorn (and Hypercorn)

Uvicorn is the ASGI server that actually accepts TCP connections and runs your FastAPI app. FastAPI itself is a framework, not a server — it doesn't bind to a port.

```bash
# Dev: auto-reload on file changes
uvicorn main:app --reload

# Production: multiple workers behind a process manager
gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4
```

Hypercorn is an alternative ASGI server with similar capabilities and HTTP/2 + HTTP/3 support.

## Starlette under the hood

FastAPI extends [Starlette](https://www.starlette.io/) for its HTTP machinery: `Request`, `Response`, middleware, routing, WebSockets, background tasks, and the test client all come from Starlette.

When something feels under-documented in FastAPI, the Starlette docs are usually the right next step. FastAPI's contribution on top is the Pydantic-driven typing layer, dependency injection, and OpenAPI generation — the request/response plumbing is Starlette.

## Pydantic under the hood

Pydantic models are not optional infrastructure — they are the data contract for requests and responses. A typed parameter is a Pydantic-validated parameter, and a Pydantic model used as a function argument tells FastAPI to parse and validate the request body against it.

```python
from pydantic import BaseModel

class Book(BaseModel):
    id: int
    title: str

@app.post("/books")
async def create_book(book: Book):
    return book  # validated, typed, serializable
```

Pydantic v2 is the current major version and a Rust-backed rewrite with breaking changes from v1 (`model_dump` replaces `dict`, `@field_validator` replaces `@validator`, etc.).

## Auto-generated OpenAPI schema

Every route, parameter, model, and response shape is reflected into an OpenAPI 3 document at `/openapi.json` with no extra code. The schema is generated from your function signatures and Pydantic models — no separate spec file to maintain.

This schema is what powers the interactive docs, client SDK generators, and API gateways. Treat it as a real deliverable: keep your function signatures and response models clean and the schema will be clean too.

## Swagger UI and ReDoc

FastAPI serves two interactive docs sites for free, generated from the OpenAPI schema:

- **`/docs`** — Swagger UI, the interactive request console. Click "Try it out" to send real requests against the running app.
- **`/redoc`** — ReDoc, a cleaner read-only reference view, better for sharing with API consumers.

Both can be disabled or relocated via the `FastAPI(docs_url=..., redoc_url=...)` constructor arguments.

## Type hints as the API contract

A single declaration like `param: int` drives parsing, validation, type coercion, error responses, and the OpenAPI schema entry. This convergence is FastAPI's defining design choice.

In other frameworks you would write the route handler, a separate schema, a separate validator, and a separate docstring for the docs. In FastAPI, the type hint is all four. The cost is that you must take type hints seriously — sloppy types produce sloppy APIs.
