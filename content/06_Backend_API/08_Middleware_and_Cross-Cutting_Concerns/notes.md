# Middleware and Cross-Cutting Concerns

Not every important backend behavior belongs inside a route handler. Middleware and related framework hooks exist so concerns like tracing, CORS, and shared logging can be applied once and then trusted everywhere.

## Key Points

- **Middleware wraps requests** - It runs around handler execution and is ideal for shared request-wide behavior.
- **Cross-cutting concerns should stay shared** - Logging, compression, tracing, and similar policies do not belong in every endpoint manually.
- **Correlation IDs make debugging possible** - They tie logs and traces for one request together.
- **CORS is a browser security contract** - A request can work in `curl` and still fail in the browser if cross-origin policy is wrong.
- **Shared response policies reduce drift** - Consistent headers and envelopes are easier to maintain centrally.
- **Framework syntax changes, concepts do not** - Middleware, filters, and interceptors solve similar design problems across stacks.

## Example

```python
def middleware(request: dict, handler):
    request_id = request.get("request_id", "generated-123")
    response = handler(request)
    response["headers"]["x-request-id"] = request_id
    return response


def handler(request: dict) -> dict:
    return {"status": 200, "headers": {}, "body": {"ok": True}}


print(middleware({}, handler))
```

The handler stays focused on business behavior, while the middleware adds shared request context that every endpoint can benefit from.
