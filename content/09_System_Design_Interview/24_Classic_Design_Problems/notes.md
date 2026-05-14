# Classic Design Problems

The system design interview canon — problems that appear repeatedly because each one exercises a specific set of distributed systems trade-offs. Recognizing which patterns apply to which problem is half the battle. This topic covers eight classic problems and the core design decisions in each.

## Key Points

- **URL shortener** — hash or counter-based short code generation, 301 vs 302 redirects, read-heavy caching. Exercises hashing, storage, and analytics trade-offs.
- **Chat system** — WebSocket connections, message storage with ordering guarantees, group fan-out, presence detection. Exercises real-time delivery and eventual consistency.
- **News feed / timeline** — fan-out on write for normal users, fan-out on read for celebrities, hybrid merge at read time. The classic read/write trade-off.
- **Web crawler** — URL frontier with politeness and priority queues, content deduplication via fingerprinting, distributed coordination. Exercises BFS at web scale.
- **Distributed key-value store** — consistent hashing, quorum reads/writes, vector clocks or LWW for conflict resolution, gossip protocol for failure detection.
- **Metrics monitoring** — push vs pull collection, time-series storage with compression, roll-up aggregation, alerting rules with deduplication.
- **Ticket booking** — optimistic vs pessimistic locking, reservation with TTL, overbooking policies. Exercises transaction isolation under contention.
- **Stock exchange** — single-threaded matching engine per symbol, price-time priority, sequencer for fairness, microsecond latency requirements.

## Example

Designing a URL shortener — the simplest classic problem that still tests real trade-offs:

```text
Requirements:
  100M URLs shortened per month. 10B redirects per month.
  Read:write ratio = 100:1. Short codes 7 characters (Base62).
  Custom aliases optional. Analytics (click count, referrer).

Write path (shorten):
  POST /shorten { long_url: "https://example.com/very/long/path" }
  1. Generate short code:
     Counter approach: get next ID from distributed counter (Snowflake).
     ID = 1234567890 → Base62 encode → "1LY7VK"
  2. Store in DB: short_code (PK) | long_url | user_id | created_at
  3. Return: https://short.ly/1LY7VK

Read path (redirect):
  GET /1LY7VK
  1. Check Redis cache: "1LY7VK" → "https://example.com/very/long/path"
     Cache hit → 302 redirect. Done.
  2. Cache miss → query DB → populate cache → 302 redirect.
  3. Async: increment click_count, log referrer and timestamp.

Scale:
  Writes: 100M/month ≈ 40 writes/sec → single DB handles this easily.
  Reads:  10B/month ≈ 4000 reads/sec → Redis cache absorbs most of this.
  Storage: 100M × 1 KB ≈ 100 GB/year. Modest.

  The bottleneck is cache hit rate, not compute.
  With a 90% cache hit rate: 400 reads/sec hit the DB. Trivial.
```
