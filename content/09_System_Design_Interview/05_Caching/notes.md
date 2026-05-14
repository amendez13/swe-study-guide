# Caching

The single highest-leverage technique for reducing latency and database load in read-heavy systems. A well-placed cache can absorb 80–95% of read traffic, turning a database bottleneck into a non-issue. The cost is complexity: you now have two sources of truth that can diverge.

## Key Points

- **When caching helps** — high read:write ratio, power-law access distribution, tolerance for slight staleness. Less effective when every request is unique.
- **Cache-aside** — app checks cache, on miss reads DB and populates cache. Most common pattern. Only caches data that's actually requested.
- **Read-through / write-through** — cache sits inline and manages DB interaction. Write-through keeps cache and DB in sync at the cost of write latency.
- **Write-behind** — writes go to cache, async flush to DB. Low write latency, but risks data loss if cache crashes before flush.
- **Eviction policies** — LRU is the default. LFU for popularity-stable data. TTL limits staleness. "LRU with a TTL" is the safe interview answer.
- **Cache invalidation** — the hard problem. TTL as baseline, event-driven invalidation for critical data, versioned keys for safe rollover.
- **CDN** — a globally distributed cache for static content. Reduces origin load and latency for global users. Pull (on-demand) vs. push (proactive) models.
- **Distributed cache** — partition keys across multiple nodes via consistent hashing. Redis Cluster or Memcached for high-scale workloads.

## Example

Adding a cache layer to a user profile service:

```text
Before caching:
  GET /users/42 → DB query → 15ms response, 10,000 QPS to DB

After cache-aside with Redis:
  GET /users/42 → Redis GET user:42
    HIT  (95% of requests) → 1ms response, no DB query
    MISS (5% of requests)  → DB query → SET user:42 EX 300 → 15ms

  DB load: 10,000 × 0.05 = 500 QPS (95% reduction)
  Avg latency: 0.95 × 1ms + 0.05 × 15ms = 1.7ms

Invalidation:
  On PUT /users/42, delete cache key user:42.
  TTL of 300s as safety net in case invalidation is missed.

Trade-off accepted:
  A user who updates their profile may see stale data for
  up to 300 seconds on other devices. Acceptable for profiles,
  not acceptable for account balance.
```

This pattern — cache-aside with TTL plus explicit invalidation on writes — covers the majority of caching needs in system design interviews.
