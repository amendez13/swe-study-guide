## Request-response vs. real-time communication

Most backend APIs are request-response systems: the client asks, the server answers, and the connection ends. Real-time features such as chat, live dashboards, or collaborative editing need ongoing communication instead of periodic polling alone.

That changes both the transport and the operational model. Long-lived connections behave differently from short stateless requests.

Example: `GET /notifications` every 5 seconds is a polling design; a persistent websocket subscription is a real-time design.

## WebSockets and streaming

WebSockets provide a bidirectional channel between client and server so both sides can send messages over one open connection. Streaming responses (SSE) are a related pattern where the server sends incremental updates without waiting for the full result.

These tools solve real problems, but they are not default upgrades over REST. They are appropriate when the product needs timely push behavior, not when plain polling would already be good enough.

```text
Transport        Direction           Protocol      Use case
───────────────  ──────────────────  ────────────  ────────────────────
Polling          Client → Server     HTTP          Simple, low-frequency
Long-polling     Client ← Server     HTTP          Notifications
SSE              Server → Client     HTTP          Live scores, feeds
WebSocket        Bidirectional       WS over HTTP  Chat, collaboration

WebSocket lifecycle:
  1. Client sends HTTP upgrade request
  2. Server responds with 101 Switching Protocols
  3. Both sides send/receive frames on the open connection
  4. Either side can close the connection

SSE lifecycle:
  1. Client sends GET with Accept: text/event-stream
  2. Server keeps connection open, sends events as they happen:
     data: {"price": 142.50, "symbol": "AAPL"}\n\n
  3. Client auto-reconnects if connection drops
```

## State, fanout, and backpressure

Real-time systems must decide how to track connected clients, how to broadcast updates, and what happens when a client or downstream system cannot keep up. Those concerns are less visible in ordinary request-response APIs.

This is where simple demos often hide production difficulty. Keeping one websocket open is easy; managing thousands of them predictably is not.

```text
Connection state:
  Server must track which clients are connected and to which rooms/topics.
  If server restarts → all connections drop → clients must reconnect.
  Sticky sessions or a pub/sub backplane (Redis) help with multi-server.

Fanout:
  A message in a chat room must reach every connected member.
  Room with 5 members → 5 writes.  Room with 20,000 → 20,000 writes.
  At scale: fan out through Redis pub/sub or a message broker.

Backpressure:
  A slow client can't keep up with the message rate.
  Options: buffer (risk OOM), drop old messages, or disconnect the client.
  Server should set a per-client send buffer limit.
```

## HTTP caching primitives

Performance work is not only about code speed. HTTP already provides primitives like `Cache-Control`, `ETag`, and `Last-Modified` that can avoid unnecessary recomputation and reduce bandwidth.

Using these well can improve perceived performance dramatically, especially for read-heavy endpoints that do not change often.

```http
# First request — server returns data + cache headers:
GET /products/42 HTTP/1.1

HTTP/1.1 200 OK
Cache-Control: max-age=60
ETag: "v17"

{"id": 42, "name": "Widget", "price": 9.99}

# Within 60 seconds — client uses cached copy, no request sent.

# After 60 seconds — client revalidates:
GET /products/42 HTTP/1.1
If-None-Match: "v17"

HTTP/1.1 304 Not Modified   ← no body, saves bandwidth

# If the product changed:
HTTP/1.1 200 OK
ETag: "v18"

{"id": 42, "name": "Widget", "price": 12.99}
```

## Server-side caching and invalidation

Some expensive reads benefit from in-memory or distributed caches in front of the database or downstream APIs. Caching can cut latency sharply, but it introduces invalidation and consistency complexity.

This tradeoff is why caching is often described as easy to add and hard to get correct. The hard part is deciding when cached data is stale enough to matter.

Example: cache product details for 5 minutes, but invalidate immediately after a product price update.

## Rate limiting and payload discipline

Performance and resilience also depend on limiting abuse and avoiding waste. Rate limits protect the service from accidental or malicious overload, while disciplined payload design prevents overfetching and oversized responses from becoming a hidden scaling tax.

Good performance work is often boring but high leverage: smaller payloads, bounded endpoints, predictable limits, and fewer unnecessary calls.

```http
429 Too Many Requests
Retry-After: 60
```
