# Load Balancing

The mechanism that makes horizontal scaling work. A load balancer distributes requests across backend servers, provides failover when servers die, and enables zero-downtime deployments. Every system design interview that involves multiple servers includes one.

## Key Points

- **What it does** — distributes requests across backend servers to spread load and provide failover. Appears at multiple layers: client → web, web → app, app → database.
- **DNS-level balancing** — returns different IPs for the same domain. Simple but coarse-grained, slow to update, and can't health-check backends.
- **Layer 4 vs. Layer 7** — L4 routes by IP/port (fast, no content inspection); L7 routes by HTTP headers, paths, and cookies (flexible, content-aware). Default to L7 for HTTP services.
- **Algorithms** — round robin (simple), weighted round robin (heterogeneous servers), least connections (best general default), IP hash (sticky sessions), consistent hashing (cache routing).
- **Health checks** — active (periodic probes to `/health`) or passive (monitor real request error rates). Unhealthy servers are removed from the pool.
- **Sticky sessions** — same client always hits the same server. Needed for in-memory session state, but breaks even scaling. Prefer external session stores.
- **LB redundancy** — a single LB is a SPOF. Use active-passive pairs or cloud-managed LBs that are inherently redundant.

## Example

Choosing the right load balancing algorithm for a chat application:

```text
Scenario: Chat app with WebSocket connections
  - 10M concurrent connections across 50 servers
  - Each connection is long-lived (minutes to hours)
  - Connections are stateful (server holds session state)

Bad choice: Round Robin
  New connections are evenly distributed, but server load
  depends on active connections, not new ones. A server
  with 300K idle connections and one with 100K active
  connections look the same to round robin.

Good choice: Least Connections
  Routes new connections to the server with fewest active
  connections, naturally balancing load as connections
  come and go.

Also needed: Sticky sessions (or connection-level affinity)
  WebSocket connections are stateful — once established,
  all messages on that connection must go to the same server.
  The LB handles this at L4 by tracking the TCP connection.
```

The algorithm choice follows directly from the workload characteristics: long-lived, stateful connections favor least-connections with L4 affinity.
