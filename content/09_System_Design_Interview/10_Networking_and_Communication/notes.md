# Networking and Communication

How services talk to each other and to clients. The choice between REST, RPC, WebSockets, and message queues shapes the entire architecture. In system design interviews, you'll typically use REST for the public API, gRPC for internal services, and WebSockets or SSE for real-time features.

## Key Points

- **REST** — resource-oriented HTTP API. Stateless, cacheable, universally understood. The default for public-facing APIs.
- **RPC / gRPC** — call remote functions as if local. Binary Protocol Buffers, strict schemas, streaming support. Default for internal service-to-service calls.
- **REST vs. RPC** — REST for public, CRUD, and cacheable APIs. gRPC for internal, low-latency, streaming, and polyglot services. Many systems use both.
- **API Gateway** — single entry point handling routing, auth, rate limiting, and SSL termination. Draw one in every microservices diagram.
- **Forward vs. reverse proxy** — forward proxy acts for clients (hides client identity); reverse proxy acts for servers (load balancing, SSL, caching). Reverse proxies are ubiquitous in system design.
- **Real-time communication** — WebSockets for bidirectional (chat, gaming); SSE for server-push only (notifications, live updates); long-polling as a fallback.
- **Idempotency** — same operation, same result on retry. Use idempotency keys for non-idempotent operations (POST) to prevent duplicates in distributed systems.

## Example

API design for a ride-sharing service:

```text
Public REST API (client → API Gateway):
  POST /rides           — request a ride (idempotency key required)
  GET  /rides/123       — get ride status
  GET  /rides/123/eta   — get estimated time of arrival

Internal gRPC (service → service):
  MatchingService.FindDriver(ride_id) → driver_id
  PricingService.CalculateFare(route) → fare
  PaymentService.Charge(ride_id, fare) → receipt

Real-time (server → client):
  WebSocket /ws/rides/123/track
    Server pushes driver location updates every 2 seconds.
    Client sends nothing (could also use SSE, but WebSocket
    is already open for bidirectional chat with driver).

Idempotency:
  POST /rides with Idempotency-Key: "user42-1710000000"
  If the client retries (network timeout), the server returns
  the same ride_id without creating a duplicate ride request.
```

Different communication patterns for different needs — all in one system.
