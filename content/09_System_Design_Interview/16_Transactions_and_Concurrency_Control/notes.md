# Transactions and Concurrency Control

How to ensure correctness when multiple operations or users interact with the same data simultaneously. Transactions provide the abstraction; isolation levels and concurrency strategies determine the cost. In system design interviews, this topic appears whenever you're booking seats, transferring money, or coordinating writes across services.

## Key Points

- **Transaction** — all-or-nothing unit of work. Without it, a crash between two related writes leaves data in an inconsistent state.
- **Isolation levels** — Read Committed (no dirty reads), Repeatable Read/Snapshot (consistent view), Serializable (no anomalies). Higher isolation = lower throughput.
- **Optimistic vs. pessimistic** — optimistic checks at commit (high throughput, retries on conflict); pessimistic locks upfront (no retries, but blocks others).
- **Two-phase locking** — growing then shrinking lock phases guarantee serializability but can deadlock.
- **Two-phase commit** — atomic commits across multiple nodes. Blocks if coordinator crashes. Prefer sagas for cross-service transactions.
- **Consensus algorithms** — Raft, Paxos, Zab. Used by ZooKeeper, etcd, Consul for leader election and distributed coordination. Requires majority availability.

## Example

Designing concurrency control for a ticket booking system:

```text
Problem:
  1,000 users try to book 100 remaining seats for a concert.
  Two users must not book the same seat.

Approach 1 — Pessimistic locking (database-level):
  BEGIN;
  SELECT * FROM seats WHERE id = 42 FOR UPDATE;
  -- Row locked. Other transactions wait.
  UPDATE seats SET status = 'booked', user_id = 'user_A' WHERE id = 42;
  COMMIT;
  -- Lock released. Next transaction proceeds.

  + Guaranteed no double-booking.
  - High contention on popular seats → long waits.
  Verdict: works for moderate scale.

Approach 2 — Optimistic concurrency (version-based):
  SELECT id, version FROM seats WHERE id = 42;  -- version = 5
  -- Application logic...
  UPDATE seats SET status = 'booked', user_id = 'user_A', version = 6
  WHERE id = 42 AND version = 5;
  -- If 0 rows affected → someone else booked it → retry or show "taken"

  + No locking, higher throughput.
  - High retry rate when 100 users target the same seat.
  Verdict: better for low-contention scenarios.

Approach 3 — Atomic counter (Redis):
  DECR remaining_seats  -- atomic, returns new count
  If count >= 0 → proceed to book in DB.
  If count < 0 → sold out, INCR to restore.

  + Very fast, handles high concurrency.
  - Separate from DB (must reconcile).
  Verdict: good for fast "sold out" checks before hitting the DB.
```

The right approach depends on contention level: pessimistic for high contention (popular items), optimistic for low contention (most e-commerce).
