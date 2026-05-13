## Request-response vs. real-time communication

Most backend APIs are request-response systems: the client asks, the server answers, and the connection ends. Real-time features such as chat, live dashboards, or collaborative editing need ongoing communication instead of periodic polling alone.

That changes both the transport and the operational model. Long-lived connections behave differently from short stateless requests.

Example: `GET /notifications` every 5 seconds is a polling design; a persistent websocket subscription is a real-time design.

## WebSockets and streaming

WebSockets provide a bidirectional channel between client and server so both sides can send messages over one open connection. Streaming responses are a related pattern where the server sends incremental updates without waiting for the full result.

These tools solve real problems, but they are not default upgrades over REST. They are appropriate when the product needs timely push behavior, not when plain polling would already be good enough.

```text
Client <--> WebSocket connection <--> Server
Client <-- streamed chunks --------- Server
```

## State, fanout, and backpressure

Real-time systems must decide how to track connected clients, how to broadcast updates, and what happens when a client or downstream system cannot keep up. Those concerns are less visible in ordinary request-response APIs.

This is where simple demos often hide production difficulty. Keeping one websocket open is easy; managing thousands of them predictably is not.

Example: a chat service may need one room update to fan out to 2 users or 20,000 users, with different scaling implications.

## HTTP caching primitives

Performance work is not only about code speed. HTTP already provides primitives like `Cache-Control`, `ETag`, and `Last-Modified` that can avoid unnecessary recomputation and reduce bandwidth.

Using these well can improve perceived performance dramatically, especially for read-heavy endpoints that do not change often.

```http
ETag: "orders-v17"
Cache-Control: max-age=60
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
