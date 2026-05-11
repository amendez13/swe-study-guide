# Framework Foundations

The pieces FastAPI is built on and the contract it offers to your code. Knowing these makes the rest of the framework feel less like magic.

## Key Points

- **ASGI vs WSGI** — WSGI is synchronous (Flask, classic Django); ASGI is async-capable. FastAPI runs on ASGI, which is what lets `async def` path operations cooperatively handle concurrent I/O.
- **The `FastAPI` application instance** — the root object you instantiate once. It holds the route table, middleware stack, exception handlers, and OpenAPI metadata. Everything else attaches to it.
- **Uvicorn (and Hypercorn)** — Uvicorn is the ASGI server that actually accepts connections and runs your app. `uvicorn app:app --reload` in dev; multiple workers behind a process manager (`gunicorn -k uvicorn.workers.UvicornWorker`) in production.
- **Starlette under the hood** — FastAPI extends Starlette for the HTTP machinery (`Request`, `Response`, middleware, routing, WebSockets, background tasks). Reading the Starlette docs is often the right next step when something feels under-documented in FastAPI.
- **Pydantic under the hood** — Pydantic models are not optional infrastructure; they are the data contract. A typed parameter is a Pydantic-validated parameter. v2 is the current major version and is a Rust-backed rewrite with breaking changes from v1.
- **Auto-generated OpenAPI schema** — every route, parameter, model, and response shape is reflected into an OpenAPI 3 document at `/openapi.json` with no extra code.
- **Swagger UI and ReDoc** — `/docs` (Swagger UI) is the interactive request console; `/redoc` is the read-only reference view. Both are generated from the OpenAPI schema.
- **Type hints as the API contract** — a single `param: int` declaration drives parsing, validation, type coercion, error responses, and the OpenAPI schema entry. This convergence is FastAPI's defining design choice.

## Example

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Books API",
    version="0.1.0",
    description="Minimal FastAPI app demonstrating the framework primitives.",
)


class Book(BaseModel):
    id: int
    title: str


@app.get("/books/{book_id}", response_model=Book)
async def read_book(book_id: int) -> Book:
    return Book(id=book_id, title="Example")
```

Running it:

```bash
uvicorn main:app --reload
# Open http://127.0.0.1:8000/docs for Swagger UI
# Open http://127.0.0.1:8000/openapi.json for the raw schema
```

This eight-line app exercises every concept in this topic: an ASGI app instance, a Pydantic response model, a typed path parameter, automatic OpenAPI generation, and interactive docs — all served by Uvicorn.
