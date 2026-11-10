# Transactions and Concurrency Control

Lantern Press prints a run by marking a plate used and taking sheets from a lot. Those two writes commit together, or the crash between them leaves the lot still offering sheets that are already on the press. Concurrent runs on that one database pick an isolation level, a lock or a version check, and a lock order. A decision across the press book and the paper ledger waits if its coordinator dies after both have prepared. Three nodes, west, east, and loft, choose one schedule writer by majority, and a lease in that store holds one press. The four letters, replica guarantees, compensations, and the outbox live in the topics that own them.

## Key Points

- **Transaction** — the plate write and the lot write commit together or roll back together. A crash between them, with nothing tying the writes, leaves the plate used and the lot unchanged.
- **Isolation levels** — read committed hides uncommitted rows and can change its answer mid-run. A snapshot holds the first answer and can still allow write skew. Serializable aborts one side of that skew. This is one database.
- **Optimistic or pessimistic** — lock first when many operators want one plate. Check a version at commit when conflicts are rare. Zero rows updated means the version moved and the run retries.
- **Two-phase locking** — acquire locks, then release them at commit. A wait-for cycle is a deadlock. A timeout or aborting one side of the cycle breaks it.
- **Two-phase commit** — prepare, then commit or abort. Participants that voted yes wait if the coordinator dies before the decision. Across services, each service commits locally and compensates later. A local commit plus a later publish is the outbox.
- **Consensus algorithms** — a log entry commits when a majority acknowledges it. Raft is the name to give. Call etcd or ZooKeeper. Three nodes commit with 2 acknowledgements and survive 1 failure.
- **Leader election** — one schedule writer, chosen by a majority. The side of one must stop writing. The side of two may elect.
- **Distributed locks** — a lease on a key in the consensus store. After the lease ends, a new holder may take the key. An expired holder still has to be fenced.

## Example

Plate P-14 is marked used, and the process dies before lot L-3 drops from 800 to 400. A later claim read version 7 and finds version 8. The schedule log has 5 nodes.

```python
START_LOT = 800
RUN_SHEETS = 400


def crash_between() -> tuple[str, int]:
    return "used", START_LOT


def version_rows(read_version: int, now: int) -> int:
    if now != read_version:
        return 0
    return 1


def majority(nodes: int) -> int:
    return nodes // 2 + 1


print(crash_between(), version_rows(7, 8), majority(5), majority(5) - 1)
# ('used', 800) 0 3 2
```

The crash leaves the plate used and the lot at 800, so the same sheets can be offered again. Commit would have left the lot at 400, and rollback would have left the plate free and the lot at 800. The version update changes 0 rows, so that claim retries. Five nodes commit a schedule entry when 3 acknowledge, and that majority still forms after 2 failures. West alone, 1 of 3, still must not write the schedule while east and loft elect.

## See also

- [Databases Relational](../06_Databases_Relational/) — ACID Properties and Failover and Promotion. The four letters, durability on the node that commits, and fencing a relational primary stay there.
- [Consistency and Replication](../09_Consistency_and_Replication/) — Linearizability, Strong Consistency, and Quorum Reads and Writes. Replica guarantees and the overlapping read and write sets stay there.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Transactional Outbox. One local commit and a later publish stay there.
- [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/) — Saga Pattern. Compensating writes across services stay there.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Split Brain. Two writers after a cut stay there. Agreeing on one leader stays here.
- [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/) — a race inside a limiter. A lost update on this database stays here.
