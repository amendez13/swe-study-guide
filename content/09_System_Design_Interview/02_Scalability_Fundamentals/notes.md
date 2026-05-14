# Scalability Fundamentals

How systems grow from serving one user to millions. Scalability is not about building for Google-scale on day one — it's about knowing which bottleneck hits next and which technique addresses it, so you can evolve the architecture as load grows.

## Key Points

- **Vertical scaling** — bigger machine, no code changes, but hits hardware ceilings and is a single point of failure. The right first move for early-stage systems.
- **Horizontal scaling** — more machines behind a load balancer. Requires the application tier to be stateless so any instance can handle any request.
- **Stateless vs. stateful** — stateless services scale by cloning; stateful services (databases, caches, WebSocket servers) require replication or partitioning.
- **Describing load** — quantify QPS, read/write ratio, data volume, and peak-to-average ratio before choosing a scaling strategy.
- **Describing performance** — throughput (requests/sec) and latency (p50, p95, p99). Tail latency matters most at scale because even 1% of requests affects thousands of users.
- **The Scale Cube** — three dimensions: X-axis (clone instances), Y-axis (functional decomposition into services), Z-axis (data partitioning/sharding).
- **Scaling from zero to millions** — the evolutionary path: single server → separate DB → cache → horizontal app tier → DB replication → CDN → sharding → async processing.

## Example

A back-of-the-envelope scaling decision for a read-heavy social feed:

```text
Given:
  50M DAU, 20 feed views/day, 2 posts/day
  Average feed response: 5 KB

Reads:
  50M × 20 = 1B reads/day ≈ 12,000 QPS avg, ~36,000 QPS peak

Writes:
  50M × 2 = 100M writes/day ≈ 1,200 QPS avg

Read:Write ratio ≈ 10:1 → read-heavy system

Scaling strategy:
  - Cache the feed (Redis) → reduces DB read QPS by ~90%
  - 3 read replicas → remaining DB reads spread across replicas
  - Horizontal app tier (6-8 stateless servers behind LB)
  - Single DB leader handles 1,200 QPS writes (well within capacity)
  - Shard the DB later if write QPS or storage outgrows one leader
```

The numbers drive the design: a 10:1 read-heavy ratio means investing in caching and read replicas, not in write-path optimization or sharding (yet).
