# HTTP Semantics and URI Design

Backend API design starts with speaking HTTP correctly. If methods, status codes, URIs, and headers are used consistently, the rest of the stack becomes easier to reason about for clients, operators, and the engineers maintaining the service.

## Key Points

- **Requests and responses have a fixed shape** - Method, path, headers, query string, and body on the way in; status, headers, and body on the way out.
- **Methods carry meaning** - `GET` reads, `POST` creates, `PUT` replaces, `PATCH` mutates, and `DELETE` removes.
- **Status codes drive behavior** - Monitoring, retry logic, and client error handling all depend on them.
- **URIs should be stable and readable** - Name resources clearly and avoid coupling paths to implementation details.
- **Path and query parameters serve different roles** - Identity belongs in the path; filtering and shaping belong in the query string.
- **Idempotency matters operationally** - Some requests can be retried safely and some cannot.
- **Headers carry control metadata** - Auth, caching, tracing, and representation negotiation often belong there.

## Example

```python
request = {
    "method": "GET",
    "path": "/orders",
    "query": {"status": "paid", "limit": "20"},
    "headers": {"Accept": "application/json"},
}

response = {
    "status": 200,
    "headers": {"Content-Type": "application/json"},
    "body": [{"id": 1, "status": "paid"}],
}

print(request["method"], request["path"], request["query"])
print(response["status"], response["headers"]["Content-Type"], response["body"][0]["id"])
```

The example is simple, but it captures the mental model: a request names a resource and shapes the result, while the response communicates success and representation explicitly.
