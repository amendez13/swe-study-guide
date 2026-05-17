# Transactions and Concurrency

Postgres uses MVCC to let readers and writers coexist without blocking each other. Understanding transactions, isolation levels, and locking strategies is essential for building applications that are both correct and performant under concurrent access.

## Key Points

- **ACID** — atomicity (all or nothing), consistency (constraints hold), isolation (snapshots), durability (WAL to disk). Postgres provides all four by default.
- **BEGIN/COMMIT/ROLLBACK** — explicit transaction boundaries. Without BEGIN, every statement is its own transaction.
- **Isolation levels** — Read Committed (default: each statement sees latest committed data), Repeatable Read (transaction-level snapshot), Serializable (full consistency, retry on conflict).
- **MVCC** — old row versions stay visible to running transactions. Readers never block writers. Dead tuples accumulate until VACUUM.
- **Row-level locking** — FOR UPDATE prevents concurrent modification. Use NOWAIT to fail fast, SKIP LOCKED for job queues.
- **Deadlocks** — Postgres detects and aborts one transaction automatically. Prevent by locking in consistent order and keeping transactions short.
- **Optimistic vs pessimistic** — pessimistic locks upfront (FOR UPDATE); optimistic checks at write time (version column). Choose based on conflict frequency.

## Example

```sql
-- Simulate a safe money transfer between accounts

BEGIN ISOLATION LEVEL READ COMMITTED;

  -- Lock both rows in a consistent order (lower ID first) to prevent deadlocks
  SELECT id, balance FROM accounts WHERE id IN (1, 2) ORDER BY id FOR UPDATE;

  -- Check business rules
  -- (application code would verify sufficient balance here)

  UPDATE accounts SET balance = balance - 100.00 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100.00 WHERE id = 2;

COMMIT;
-- If any statement fails, the entire transfer is rolled back atomically
```

This demonstrates explicit transaction control, row-level locking with FOR UPDATE, consistent lock ordering to prevent deadlocks, and the atomicity guarantee (both updates succeed or neither does).
