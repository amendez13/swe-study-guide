## `response_model`

`response_model` on the route decorator declares the output schema. FastAPI validates the return value against the model, drops fields not in the schema, and includes the model in the OpenAPI document.

```python
class UserOut(BaseModel):
    id: int
    email: str

@app.get("/users/{id}", response_model=UserOut)
async def get_user(id: int):
    return load_user_with_password_hash(id)  # password_hash is filtered out
```

This is the canonical way to hide internal fields (password hashes, soft-delete flags, internal IDs) from API responses without writing serialization code by hand.

## Explicit status codes

The default success code is `200`. Override it per route with `status_code=...` on the decorator. Use the constants from `fastapi.status` for readability — `status.HTTP_201_CREATED` is clearer than a bare `201`.

```python
from fastapi import status

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(...): ...

@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int) -> None: ...
```

The declared status code shows up in the OpenAPI schema, which is what Swagger UI and generated clients use to set their expectations.

## `HTTPException`

`HTTPException` is the canonical way to abort a request with a specific HTTP status. Raise it from anywhere in your handler (or dependencies) and FastAPI returns a JSON error response with the given status code and detail.

```python
from fastapi import HTTPException, status

@app.get("/books/{id}")
async def get_book(id: int):
    book = repo.find(id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book
```

`detail` can be a string, dict, or list — whatever you pass becomes the JSON body. You can also pass `headers={...}` to set response headers (used by 401s for the `WWW-Authenticate` header).

## Custom exception handlers

When the same translation appears repeatedly ("if `BookNotFound` is raised, return 404 with this body"), register an exception handler once instead of catching the exception in every route.

```python
class BookNotFound(Exception):
    def __init__(self, book_id: int):
        self.book_id = book_id

@app.exception_handler(BookNotFound)
async def book_not_found_handler(request, exc: BookNotFound):
    return JSONResponse(
        status_code=404,
        content={"error": "book_not_found", "id": exc.book_id},
    )
```

Now any route can `raise BookNotFound(id)` and get a consistent response shape. You can also override the built-in `RequestValidationError` handler to customize the 422 response format across the whole API.

## `JSONResponse` and other response classes

FastAPI serializes return values to JSON by default. When you need something else — HTML, plain text, a streaming download, a redirect — return a `Response` subclass directly or set `response_class` on the route.

```python
from fastapi.responses import (
    HTMLResponse, PlainTextResponse, RedirectResponse,
    StreamingResponse, FileResponse,
)

@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return "<h1>Hello</h1>"

@app.get("/legacy")
async def legacy():
    return RedirectResponse("/new", status_code=308)

@app.get("/download/{id}")
async def download(id: int):
    return FileResponse(path=f"files/{id}.pdf", filename="report.pdf")
```

`StreamingResponse(generator)` is the right tool for large bodies you don't want to buffer in memory — log tails, CSV exports, generated PDFs.

## Response headers and cookies

Two ways to set headers on a response:

1. Accept a `Response` parameter in the handler and mutate its `headers` / call `set_cookie`. FastAPI merges your changes into the final response.
2. Return a `Response` subclass directly with `headers=...` in the constructor.

```python
from fastapi import Response

@app.post("/items")
async def create_item(response: Response):
    item = repo.create(...)
    response.headers["Location"] = f"/items/{item.id}"
    response.set_cookie("last_created", str(item.id), httponly=True)
    return item
```

Use the first form when you want FastAPI to handle serialization; the second when you're building the response by hand.
