# Networking and Communication

Clients and services have to agree on a transport, on how many calls share a connection, and on the shape of each call. TCP repairs an ordered byte stream. UDP leaves loss visible. HTTP connections decide whether one slow response blocks the next. REST and RPC are the two call shapes, often both in one system. A proxy or a gateway is the front door. Polling, long-polling, WebSockets, and server-sent events are how a client hears about a change after the first page load. An idempotency key is what makes a retried write stay one write.

## Key Points

- **TCP and UDP** — TCP is an ordered byte stream and the stack repairs loss. UDP is a datagram. The application adds order, a resend, or an auth tag when it needs them.
- **HTTP connections** — keep-alive reuses a connection. HTTP/1.1 still returns one response at a time. HTTP/2 multiplexes streams on one connection, which is why gRPC wants it.
- **REST** — a resource URL and an HTTP method. The request stands alone, a stable GET can name a cache lifetime, and a redirect carries the next URL in Location.
- **RPC** — the call site looks local, and gRPC can stream on HTTP/2. Field numbers and schema changes stay in Encoding Serialization and Schema Evolution.
- **REST or RPC** — REST for a public, CRUD, cacheable API. RPC for an internal call that wants low latency or a stream. The edge can be REST while services use RPC.
- **Forward and reverse proxy** — a forward proxy hides the client. A reverse proxy hides the servers. A gateway is a reverse proxy that routes and checks API calls. Pool algorithms stay in Load Balancing.
- **API gateway** — one host that routes, authenticates, terminates TLS, and applies a request budget. The row and the business rule stay on the service. Peer addresses stay in Service Discovery.
- **Polling and long-polling** — a short poll asks on an interval and can be late by that interval. A long poll holds the request until a change or a timeout. Each delivery is still one HTTP request.
- **WebSockets and SSE** — a WebSocket lets either side write after the upgrade, and the socket lives on one process. SSE is a server-to-client HTTP stream that can resume from the last event id.
- **Idempotency** — GET, a PUT with the same body, and DELETE can be repeated. POST carries an idempotency key so a retry returns the stored response.

## Example

A neighborhood print shop takes an order for 500 cards. The browser calls the public API. The press service is internal. Six proof thumbnails are in flight at once. The order POST times out and the browser sends it again.

```python
def effects(keys: list[str]) -> int:
    seen: set[str] = set()
    count = 0
    for key in keys:
        if key in seen:
            continue
        seen.add(key)
        count += 1
    return count


def connections(in_flight: int, multiplex: bool) -> int:
    return 1 if multiplex else in_flight


print(effects(["7c1e", "7c1e"]), effects(["7c1e", "9af0"]), connections(6, False), connections(6, True))
# 1 2 6 1
```

`POST /jobs` with `Idempotency-Key: 7c1e` is the public REST call. The retry is the same key, so the side-effect count stays 1 and the shop returns the stored job. Key `9af0` is a second order, and the count is 2. The job service starts the press with RPC, a call that looks local and can stream temperature back. The six thumbnails need six HTTP/1.1 connections, because each connection returns one response at a time, and they need one HTTP/2 connection. A customer who can wait fifteen seconds short-polls `GET /jobs/18`. The press room, which both sends a pause and reads temperature, uses a WebSocket, and that socket stays on the process that accepted it. The gateway checks the token, applies the budget, and routes `/jobs`. The shop's laptops reach a vendor through a forward proxy. The public address in front of the catalog servers is a reverse proxy.

## See also

- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — Stateless vs. Stateful Services, and the Shared Session Store. A WebSocket is state in one process.
- [Load Balancing](../04_Load_Balancing/) — TLS Termination, Sticky Sessions, Layer 4 and Layer 7, DNS-Level Load Balancing, and the algorithms that pick a server in a pool.
- [Caching](../05_Caching/) — a response that already named a cache lifetime. The edge that serves a public object is Content Distribution and Media.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Message Delivery Guarantees when a consumer can see the same message twice.
- [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/) — Service Boundaries and Service Discovery. The gateway is the client's front door, not the registry.
- [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/) — Protocol Buffers and schema changes for an RPC payload.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Unreliable Networks: loss, duplicates, timeouts, and backoff. The idempotency key is what a retry needs.
- [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/) — the Rate Limiter. The gateway applies a budget and does not define the bucket.
- [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/) — Presence, vendor push, Real-Time Delivery Patterns, and Delivery Guarantees for Notifications.
- [Content Distribution and Media](../22_Content_Distribution_and_Media/) — a public object at the edge. This topic only needs that a GET can say it is cacheable.
- [Payment and Financial Systems](../23_Payment_and_Financial_Systems/) — Idempotency in Payments, the ledger behind a charge that uses the same kind of key.
