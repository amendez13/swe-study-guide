# Distributed System Failure Modes

The ways distributed systems break, and why they break differently from single-machine programs. Understanding these failure modes is what separates a system that handles 100 users from one that handles 100 million — at scale, everything that can go wrong will go wrong, and the system must keep working anyway.

## Key Points

- **Partial failures** — some components fail while others work. You can't always tell if a node is dead or just slow. Design for detection, isolation, and recovery.
- **Unreliable networks** — packets can be lost, delayed, duplicated, or reordered. Timeouts are the primary detection mechanism. Use retries with exponential backoff and jitter.
- **Unreliable clocks** — wall-clock time drifts across machines. Don't use timestamps for event ordering across nodes. Use logical clocks or bounded-uncertainty physical clocks.
- **Byzantine faults** — nodes behave arbitrarily. Relevant for blockchains, not for typical internal services. Assume crash-stop failures in most interview designs.
- **Split brain** — two leaders after a partition. Prevent with quorum-based election, fencing tokens, or consensus protocols (Raft, Paxos).
- **Cascading failures** — one failure triggers others. Prevent with timeouts, circuit breakers, bulkheads, load shedding, and backoff.

## Example

Tracing a cascading failure and designing the prevention:

```text
Scenario: Chat application, 10M concurrent users

Failure chain (without protection):
  1. Redis cache node fails → cache miss rate jumps from 5% to 100%.
  2. All reads hit PostgreSQL → DB CPU spikes to 100%.
  3. DB response time goes from 5ms to 5s → app server threads blocked.
  4. Thread pool exhausted → app servers return 503.
  5. Users retry → 10× more requests → remaining infrastructure collapses.
  Total outage in under 60 seconds.

Prevention layers:
  Layer 1 — Redis replication:
    Redis Sentinel auto-fails over to a replica in ~5 seconds.
    Brief spike in cache misses, not a total loss.

  Layer 2 — Circuit breaker on DB calls:
    If DB error rate > 50% for 10 seconds → open circuit.
    Return cached (potentially stale) data or a graceful error.
    DB gets breathing room to recover.

  Layer 3 — Bulkhead:
    Separate thread pool for chat messages vs. user profiles.
    Slow DB for profiles doesn't block chat message delivery.

  Layer 4 — Load shedding:
    If request queue > 1000, reject new requests with 503.
    Prevents thread pool exhaustion, keeps existing requests fast.

  Layer 5 — Retry budget:
    Clients retry at most 3 times with exponential backoff + jitter.
    Prevents retry storms from amplifying the load.

Result: Redis fails over, brief degradation, system recovers.
No cascading failure, no total outage.
```
