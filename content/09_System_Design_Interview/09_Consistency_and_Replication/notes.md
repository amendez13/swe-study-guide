# Consistency and Replication

A value that lives on more than one node forces a choice on every read and every write: how fresh the copy must be, and how many copies answer before the client hears that the write succeeded. CAP and PACELC name the choice. The topology places the copies. The quorum, the version, and the repair say what a later reader can trust.

## Key Points

- **CAP theorem** — during a partition the live choice is CP or AP. A CA label assumes the network never splits. The same product can tune the choice per operation.
- **PACELC theorem** — with no partition, each operation still chooses latency or consistency. That choice is the common case.
- **Replication topologies** — single-leader, multi-leader, or leaderless. Sync waits for another copy. Async acknowledges first and lets the other copy apply later.
- **Strong consistency** — an acknowledged write is what a later read of that key returns, including a read from another client.
- **Eventual consistency** — once writes pause, replicas converge. A read before that can be older, and the model sets no deadline on the gap.
- **Read-after-write consistency** — the writer's session sees its own write. A monotonic read keeps a later read in that session from moving backward.
- **Linearizability** — operations take effect in one real-time order. Locks, a leader lease, and a single claim need it. Raft and Paxos produce the order.
- **Quorum reads and writes** — W + R > N makes the read set share a replica with the write set. W = 1 and R = 1 can miss.
- **Conflict resolution** — last-write-wins drops a value, and a wall clock is a weak stamp. A version vector keeps concurrent writes. A merge or a CRDT combines them.
- **Read and write path** — the coordinator waits for W acknowledgements, asks R replicas, returns the newest version, and can repair an older answer.
- **Replica failure handling** — a missed heartbeat ends the wait. A hint covers a short outage. A Merkle tree finds the ranges a long outage left behind.

## Example

A pottery studio keeps a lobby count of pots fired today and a shelf card for each pot. The count uses three replicas, with W = 1 and R = 1. The shelf card uses three replicas, with W = 2 and R = 2. Two glaze notes on one pot carry timestamps 11 and 12.

```python
def overlaps(n: int, w: int, r: int) -> bool:
    return w + r > n


def lww(stamps: list[tuple[int, str]]) -> str:
    return max(stamps)[1]


print(overlaps(3, 2, 2), overlaps(3, 1, 1), lww([(11, "matte"), (12, "gloss")]))
# True False gloss
```

The lobby count can miss a firing that was just recorded, because the read set and the write set can be disjoint. The shelf card's sets share a replica, so a later read of that card sees the acknowledged note. Last-write-wins keeps gloss and drops matte. The dropped note can be the one a member wrote later on a clock that was behind. A shelf label that only one pot may claim is linearizable. The member who edits a display name needs the next reload in that session to show the new name. The copies sit on successive nodes of the ring. A second studio building is another site. A replica that is down for the afternoon catches up from a hint. A replica that stays gone leaves ranges a Merkle tree marks for copy.

## See also

- [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/) — which nodes hold the copies. The ring walk and rebalancing stay there.
- [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/) — the key-value API, and why a store leaves one machine.
- [Databases Relational](../06_Databases_Relational/) — one primary, lag, read replicas, promotion, and fencing.
- [High Availability and Reliability](../03_High_Availability_and_Reliability/) — nines, failover of a site, and a second data center.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — partial failure, unreliable clocks, and split brain as a mode.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — Raft, Paxos, and a commit that must prepare on two stores.
