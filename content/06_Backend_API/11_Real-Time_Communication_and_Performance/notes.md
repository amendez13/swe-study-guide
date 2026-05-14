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

Choosing the right transport for different features in the same application:

```text
Feature                 Transport    Why
──────────────────────  ───────────  ─────────────────────────────────
Product catalog         REST + ETag  Read-heavy, changes rarely → cache
Order status            SSE          Server pushes updates, client listens
Live chat               WebSocket    Bidirectional, low-latency messages
Weekly email digest     Background   No real-time requirement at all

Product catalog with caching:
  GET /products/42
  → Cache-Control: max-age=300, ETag: "v17"
  → 304 Not Modified on revalidation (saves bandwidth)

Order tracking with SSE:
  GET /orders/42/events (Accept: text/event-stream)
  → data: {"status": "confirmed", "time": "10:30"}\n\n
  → data: {"status": "shipped", "time": "14:15"}\n\n
  → data: {"status": "delivered", "time": "16:42"}\n\n

Live chat with WebSocket:
  ws://api.example.com/chat/room/7
  → client sends: {"type": "message", "text": "hello"}
  → server broadcasts to all room members
```

Each feature uses the transport that matches its interaction pattern — not the most advanced one available.
