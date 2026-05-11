# Request Parameters

How FastAPI pulls data from an incoming HTTP request and binds it to your function's arguments. Mastering this is what makes path operation functions feel like ordinary Python.

## Key Points

- **Path parameters** — `{name}` placeholders in the path, typed in the signature; always required.
- **Query parameters** — function args not in the path; a default makes them optional.
- **Required vs optional** — no default → required; default value or `T | None = None` → optional.
- **Request body** — a Pydantic `BaseModel`-typed arg becomes the JSON body, validated automatically.
- **Form data** — `Form(...)` for `application/x-www-form-urlencoded` and multipart bodies; needs `python-multipart`.
- **File uploads** — `UploadFile` streams large files; use `list[UploadFile]` for multiple.
- **Headers and cookies** — `Header()` and `Cookie()` markers; hyphens map to underscores.
- **`Path()` / `Query()` / `Body()`** — explicit markers that attach validators, descriptions, and examples to a parameter.

## Example

One endpoint that exercises every parameter source — path, query, body, header, and cookie — with metadata for OpenAPI:

```python
from fastapi import Cookie, FastAPI, Header, Path, Query
from pydantic import BaseModel

app = FastAPI()


class BookUpdate(BaseModel):
    title: str
    author: str


@app.put("/books/{book_id}")
async def update_book(
    # Path: required, validated
    book_id: int = Path(..., ge=1, description="Internal book ID"),
    # Query: optional with a default
    notify: bool = Query(False, description="Send a notification on update"),
    # Body: Pydantic model
    update: BookUpdate = ...,
    # Header: required (no default)
    x_request_id: str = Header(..., description="Trace ID for the request"),
    # Cookie: optional
    session: str | None = Cookie(None),
):
    return {
        "book_id": book_id,
        "notify": notify,
        "update": update,
        "request_id": x_request_id,
        "session_present": session is not None,
    }
```

A request would look like:

```bash
curl -X PUT "http://127.0.0.1:8000/books/42?notify=true" \
     -H "X-Request-ID: abc-123" \
     -H "Cookie: session=xyz" \
     -H "Content-Type: application/json" \
     -d '{"title": "New Title", "author": "Same Author"}'
```

FastAPI parses, validates, and binds each piece of the request to the right argument; anything malformed returns `422` before the handler runs.
