## Path parameters

Values embedded directly in the URL, declared as `{name}` placeholders in the path and matched to a function parameter of the same name. The type annotation drives parsing and validation: `book_id: int` rejects `/books/abc` with a 422 before your handler runs.

```python
@app.get("/books/{book_id}")
async def get_book(book_id: int):
    return {"id": book_id}
```

Path parameters are always required — there's no way to make them optional, since the path either matches or it doesn't.

## Query parameters

Key-value pairs after the `?` in a URL (`/books?limit=10&offset=20`). Declared as function arguments whose names don't appear in the path. A default value makes them optional; no default makes them required.

```python
@app.get("/books")
async def list_books(limit: int = 10, offset: int = 0, q: str | None = None):
    return {"limit": limit, "offset": offset, "q": q}
```

Like path parameters, the type annotation drives parsing — `?limit=abc` is rejected with a 422.

## Required vs optional parameters

The rule is simple: **absence of a default value means required**. To make a parameter optional, give it a default. To allow `None`, use `T | None = None` (or `Optional[T]` on pre-3.10 Python).

```python
async def search(
    q: str,                       # required
    limit: int = 10,              # optional with default
    after: str | None = None,     # optional, nullable
): ...
```

This applies to query parameters, body fields, headers, and cookies — not path parameters, which are always required.

## Request body

A function parameter typed as a Pydantic `BaseModel` becomes the request body. FastAPI parses the JSON, validates it against the model, and passes the resulting instance into the handler.

```python
from pydantic import BaseModel

class BookIn(BaseModel):
    title: str
    author: str

@app.post("/books")
async def create_book(book: BookIn):
    return book
```

Validation failures return `422 Unprocessable Entity` with a structured error explaining which field failed and why. You can have multiple body parameters; FastAPI nests them under their argument names in the request JSON.

## Form data

For `application/x-www-form-urlencoded` and `multipart/form-data` bodies (the formats HTML forms use), declare each field with `Form(...)` instead of a Pydantic model:

```python
from fastapi import Form

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
```

Form bodies and JSON bodies are mutually exclusive on a single endpoint — pick one. Form data requires `python-multipart` to be installed.

## File uploads

For multipart file uploads, declare a parameter typed as `UploadFile`. FastAPI streams the upload to a `SpooledTemporaryFile` so large files don't get loaded into memory all at once.

```python
from fastapi import File, UploadFile

@app.post("/avatars")
async def upload_avatar(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}
```

Use `list[UploadFile]` for multiple files. The `File(...)` marker is only needed when you also want to attach validation metadata like `description`.

## Headers and cookies

`Header()` and `Cookie()` declare typed parameters that pull from request headers and cookies respectively. Hyphens in header names become underscores in Python (`X-Request-ID` → `x_request_id`); FastAPI handles the translation.

```python
from fastapi import Cookie, Header

@app.get("/me")
async def whoami(
    user_agent: str = Header(...),
    session: str | None = Cookie(None),
):
    return {"agent": user_agent, "session": session}
```

Same defaults rule applies: required when no default, optional otherwise.

## `Path()`, `Query()`, `Body()` for metadata

Sometimes you need a parameter type without losing the ability to attach validation rules, a description, or examples. The `Path()`, `Query()`, and `Body()` markers let you do both:

```python
from fastapi import Path, Query

@app.get("/books/{book_id}")
async def get_book(
    book_id: int = Path(..., ge=1, description="Internal book ID"),
    fields: str | None = Query(None, max_length=200, examples=["title,author"]),
):
    return {"id": book_id, "fields": fields}
```

The `...` (Ellipsis) means "required, no default." All metadata flows into the OpenAPI schema so Swagger UI shows the description, constraints, and examples.
