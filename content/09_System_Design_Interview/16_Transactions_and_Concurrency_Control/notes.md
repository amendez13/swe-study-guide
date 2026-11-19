# Transactions and Concurrency Control

A transaction makes two writes on one database succeed or fail together, and an isolation level decides what a concurrent transaction is allowed to see. Locks or a version check keep the hot row honest. A commit that spans the order database and the payment database can block if its coordinator dies, so those services more often commit locally and compensate. A small cluster agrees on one log entry by majority, elects one leader from the side that still has that majority, and hands out a lease that expires while a paused holder can still wake up.

## Key Points

- **Transaction** — debit checking and credit savings commit together, or both roll back. A crash between the two writes, with no transaction around them, leaves the $400 in neither account.
- **Isolation levels** — read committed hides uncommitted rows, and a later statement can see a new commit. A snapshot holds the first answer and can still allow write skew, as when two on-call doctors both step down. Serializable aborts one of them. This is one database.
- **Optimistic or pessimistic** — lock the inventory row first when many buyers want the last unit. Check a version at commit when each buyer touches a different SKU. Zero rows updated means the version moved and the checkout retries.
- **Two-phase locking** — acquire locks, then release them at commit. A wait-for cycle between two account transfers is a deadlock. A timeout, aborting one side, or locking the lower account id first breaks it.
- **Two-phase commit** — prepare, then commit or abort. Participants that voted yes wait if the coordinator dies before the decision. An order service and a payment service each commit locally, and a failed charge cancels the order. A local commit plus a later publish is the outbox.
- **Consensus algorithms** — a log entry commits when a majority has stored it. Raft is the name to give. Call etcd or ZooKeeper. Three nodes commit with 2 acknowledgements and survive 1 failure.
- **Leader election** — one writer, chosen by a majority of votes in one term. The side of one cannot commit. The side of two may elect.
- **Distributed locks** — a 10-second lease on a key in the consensus store. After a 14-second pause the lease has ended and a new holder may take the key. The billing store rejects the expired holder's older token.

## Example

Checking starts at $800 and savings at $0. The debit of $400 lands and the process dies before the credit. A later reservation read version 7 and finds version 8. The coordination log has 5 nodes, and a billing lease of 10 seconds has already been paused for 14.

```python
START_CHECKING = 800
START_SAVINGS = 0
TRANSFER = 400


def crash_between() -> tuple[int, int]:
    """Debit landed. Credit did not. Nothing tied the two writes together."""
    return START_CHECKING - TRANSFER, START_SAVINGS


def version_rows(read_version: int, now: int) -> int:
    if now != read_version:
        return 0
    return 1


def majority(nodes: int) -> int:
    return nodes // 2 + 1


def may_lead(side: int, nodes: int) -> bool:
    return side * 2 > nodes


def lease_expired(paused_s: int, lease_s: int) -> bool:
    return paused_s > lease_s


print(
    crash_between(),
    version_rows(7, 8),
    majority(5),
    majority(5) - 1,
    may_lead(1, 3),
    may_lead(2, 3),
    lease_expired(14, 10),
)
# (400, 0) 0 3 2 False True True
```

`(400, 0)` is checking debited and savings never credited, so the $400 is in neither account. Commit would have left `(400, 400)`. Rollback would have left `(800, 0)`. The version update changes 0 rows, so that reservation retries. Five nodes commit a log entry when 3 have stored it, and that majority still forms after 2 failures. One node of three may not lead. The other two may. `True` means a 14-second pause has outlived the 10-second lease, so the next worker may take the key, and the billing store still has to reject the old token.

## See also

- [Databases Relational](../06_Databases_Relational/) — ACID Properties and Failover and Promotion. The four letters, durability on the node that commits, and fencing a relational primary stay there.
- [Consistency and Replication](../09_Consistency_and_Replication/) — Linearizability, Strong Consistency, and Quorum Reads and Writes. Replica guarantees and the overlapping read and write sets stay there.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Transactional Outbox. One local commit and a later publish stay there.
- [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/) — Saga Pattern. Compensating writes across services stay there.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Split Brain. Two writers after a cut stay there. Agreeing on one leader stays here.
- [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/) — a race inside a limiter. A lost update on a database row stays here.
- [Payment and Financial Systems](../23_Payment_and_Financial_Systems/) — Idempotency in Payments. The key that makes a retried charge return the first result stays there.
