# HTTP and REST

The protocol every web API speaks, and the architectural style FastAPI assumes you're building on top of it. You can't write a clean FastAPI app without internalizing HTTP semantics first.

## Key Points

- **REST is resource-oriented** — URLs are nouns, methods are verbs, server is stateless. The opposite is RPC, where URLs encode actions; resist that style.
- **CRUD maps to HTTP** — Create/`POST`, Read/`GET`, Update-replace/`PUT`, Update-partial/`PATCH`, Delete/`DELETE`.
- **Idempotency** — `GET`, `PUT`, `PATCH`, `DELETE` are idempotent; `POST` is not. Matters for retries and caching.
- **Status codes have classes** — 1xx info, 2xx success, 3xx redirect, 4xx client error, 5xx server error. The class alone tells a client whether retrying is worthwhile.
- **Workhorse codes** — `200`, `201`, `204`, `400`, `401`, `403`, `404`, `409`, `422`, `500`. Know what each says about the request.
- **Anatomy is symmetric** — request has method, path, query, headers, optional body; response has status, headers, optional body.
- **Content negotiation** — `Content-Type` and `Accept` headers let one URL serve many representations. FastAPI defaults to JSON.
- **Edge-case methods** — `OPTIONS` for CORS preflight, `HEAD` for headers-only, `TRACE` and `CONNECT` for niche cases.

## Example

A minimal REST endpoint set for a `books` resource that demonstrates the method mapping, idempotency, and status codes:

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class Book(BaseModel):
    id: int
    title: str


books: dict[int, Book] = {}


@app.get("/books", status_code=status.HTTP_200_OK)
async def list_books() -> list[Book]:
    return list(books.values())


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book: Book) -> Book:
    if book.id in books:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Book exists")
    books[book.id] = book
    return book


@app.put("/books/{book_id}", status_code=status.HTTP_200_OK)
async def replace_book(book_id: int, book: Book) -> Book:
    books[book_id] = book  # idempotent — same input, same final state
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int) -> None:
    if book_id not in books:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
    del books[book_id]
```

Every line maps to a concept above: resource-oriented paths, method-to-CRUD mapping, idempotent `PUT` and `DELETE`, distinct status codes for success and failure, and Pydantic-validated bodies that return `422` automatically when malformed.
