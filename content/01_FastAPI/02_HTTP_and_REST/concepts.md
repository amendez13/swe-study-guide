## REST as resource-oriented design

REST organizes an API around **resources** identified by URLs and **actions** expressed as HTTP methods. URLs are nouns (`/books`, `/books/42`), methods are verbs (`GET`, `POST`, `PUT`, `DELETE`), and the server keeps no client state between requests.

The opposite style is RPC, where URLs encode verbs (`/getBookById?id=42`, `/deleteBook?id=42`). Resource-oriented design is what lets HTTP caches, proxies, and clients reason about a request without knowing your application — `GET /books/42` is obviously a safe, cacheable read no matter what your code does.

```python
# REST-style
@app.get("/books/{id}")        # read one
@app.post("/books")            # create
@app.put("/books/{id}")        # replace
@app.delete("/books/{id}")     # delete

# RPC-style — avoid in a REST API
@app.post("/getBookById")
@app.post("/deleteBook")
```

## CRUD ↔ HTTP method mapping

The four CRUD operations map directly to four HTTP methods, with `PATCH` filling in for partial updates:

| CRUD | HTTP | Body | Semantics |
|------|------|------|-----------|
| Create | `POST` | yes | Server assigns the ID; not idempotent |
| Read | `GET` | no | Safe, idempotent, cacheable |
| Update (replace) | `PUT` | yes | Idempotent; client supplies full resource |
| Update (partial) | `PATCH` | yes | Idempotent in spirit; client supplies a delta |
| Delete | `DELETE` | no | Idempotent |

In FastAPI each method is a decorator on the path operation function: `@app.get(...)`, `@app.post(...)`, etc.

## Idempotency

A method is **idempotent** if calling it N times has the same effect as calling it once. `GET`, `PUT`, `DELETE`, and `PATCH` are idempotent by spec; `POST` is not.

This matters in practice because the network is unreliable. A client that doesn't get a response may retry — safely if the method is idempotent, but dangerously if it isn't. Retrying a `POST /payments` could charge a card twice; retrying a `PUT /users/42` cannot duplicate the user. Idempotency also gates caching (only safe methods are cacheable) and conditional requests.

## Status code classes

Every HTTP response carries a three-digit status code in one of five classes:

- **1xx Informational** — the request was received and processing continues (rare in REST APIs).
- **2xx Success** — the request succeeded.
- **3xx Redirection** — further action is needed; usually follow a `Location` header.
- **4xx Client error** — the request was malformed, unauthorized, or referred to a missing resource.
- **5xx Server error** — the server failed to fulfill an otherwise valid request.

The class alone tells a client whether to retry: 4xx is the client's fault and won't fix itself; 5xx might succeed on retry.

## Commonly used status codes

The codes you'll reach for repeatedly:

- **200 OK** — generic success with a body.
- **201 Created** — a `POST` created a new resource; return the new resource (and a `Location` header) in the body.
- **204 No Content** — success, no body (typical for `DELETE`).
- **400 Bad Request** — the request was malformed in a way that isn't covered by a more specific 4xx.
- **401 Unauthorized** — missing or invalid credentials (the name is misleading — it's really *unauthenticated*).
- **403 Forbidden** — authenticated but not permitted.
- **404 Not Found** — the resource doesn't exist.
- **409 Conflict** — the request conflicts with the current state (duplicate key, edit collision).
- **422 Unprocessable Entity** — what FastAPI returns when Pydantic validation fails.
- **500 Internal Server Error** — unhandled exception on the server.

```python
from fastapi import HTTPException, status

@app.get("/books/{id}")
async def get_book(id: int):
    book = books.get(id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book
```

## Request and response anatomy

Every HTTP exchange has the same shape on both sides:

- **Request:** method (`GET`), path (`/books/42`), query string (`?include=author`), headers (`Authorization`, `Accept`), and optionally a body.
- **Response:** status code (`200`), headers (`Content-Type`, `Cache-Control`), and optionally a body.

`curl -v` is the most useful tool for inspecting both:

```bash
$ curl -v "http://127.0.0.1:8000/books/42?include=author" \
       -H "Accept: application/json"
> GET /books/42?include=author HTTP/1.1
> Host: 127.0.0.1:8000
> Accept: application/json
<
< HTTP/1.1 200 OK
< content-type: application/json
< content-length: 47
<
{"id": 42, "title": "Example", "author": "..."}
```

Knowing this anatomy is what makes API debugging tractable — almost every API problem can be reduced to "which of these fields is wrong?"

## Content negotiation

Clients tell the server what they're sending with `Content-Type` and what they want back with `Accept`. The server can return different representations of the same resource based on those headers — JSON for an API client, HTML for a browser, CSV for a spreadsheet importer.

FastAPI defaults to JSON for both directions. The `Content-Type` of incoming requests is parsed automatically (`application/json` populates the typed body parameter, `application/x-www-form-urlencoded` populates `Form(...)` parameters, `multipart/form-data` populates `UploadFile`), and responses are serialized to JSON unless you return a different `Response` subclass.

```python
from fastapi.responses import HTMLResponse, PlainTextResponse

@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return "<h1>Hello</h1>"

@app.get("/health", response_class=PlainTextResponse)
async def health() -> str:
    return "ok"
```

## Less common HTTP methods

Beyond the five CRUD-mapped methods, HTTP defines a few more that you'll occasionally encounter:

- **OPTIONS** — used by browsers as a **CORS preflight** to ask the server whether a cross-origin request is allowed. FastAPI's `CORSMiddleware` answers these automatically. Also used by some tools for capability discovery.
- **HEAD** — identical to `GET` but the server returns headers only, no body. Useful for cache validation and link-checking.
- **TRACE** — a debug-only method that echoes the request back. Usually disabled in production for security reasons.
- **CONNECT** — used by HTTP proxies to open a TCP tunnel (e.g. for HTTPS through an HTTP proxy). Not something you implement in an application.
