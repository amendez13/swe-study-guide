# Real-Time Communication and Performance

Backend APIs do not all need the same interaction model. Some are best served by short request-response cycles, while others need live updates, caches, and explicit limits to stay responsive under real traffic.

## Key Points

- **Request-response is the default** - Real-time transport should be chosen because the use case demands it.
- **WebSockets and streaming enable push behavior** - They support long-lived communication patterns that REST alone does not.
- **Operational complexity rises quickly** - State tracking, broadcast behavior, and backpressure become central.
- **HTTP caching already solves many problems** - `ETag` and related headers can avoid unnecessary work.
- **Server-side caches trade speed for complexity** - Invalidation and staleness policy matter as much as hit rate.
- **Rate limits and payload discipline are performance tools** - Resilience often improves through bounded usage and smaller responses.

## Example

```python
def not_modified(client_etag: str | None, current_etag: str) -> int:
    return 304 if client_etag == current_etag else 200


print(not_modified("abc123", "abc123"))
print(not_modified("old", "abc123"))
```

This example shows the core idea behind one performance primitive: if the client already has the current representation, the server can avoid resending the full body.
