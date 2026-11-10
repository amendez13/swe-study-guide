# Transactions and Concurrency Control — Drills

Original practice for a unit of work, the anomaly a level still allows, and which side of a cut may lead. Each card is one exercise: commit to an answer, then check it. The numbers are invented for Lantern Press, a letterpress co-op. A run marks a plate used and takes sheets from a lot in one press database. Three coordination nodes, west, east, and loft, keep the night schedule. The four ACID letters, durability on the committing node, and fencing a relational primary stay in Databases Relational. Replica linearizability, strong consistency, and quorum overlap stay in Consistency and Replication. The transactional outbox stays in Message Queues and Async Processing. Saga compensations stay in Microservices and System Decomposition. Split brain as a mode stays in Distributed System Failure Modes. A race inside a limiter stays in Rate Limiting and Throttling.

## Need a Transaction

Plate P-14 and lot L-3 are one run. The lot starts at 800 sheets, and the run takes 400. The plate write lands. The process dies before the lot write. What is left when those writes stand alone? What does commit leave, and what does rollback leave?

```python
START_LOT = 800
RUN_SHEETS = 400
```

**Answer:** Alone, the plate is used and the lot is still 800. The sheets are on the press, and the lot can hand them out again. Commit leaves the plate used and the lot at 400. Rollback leaves the plate free and the lot at 800. Durability of a commit that did land, and the four letters around it, stay on ACID Properties.

```python
START_LOT = 800
RUN_SHEETS = 400


def crash_between() -> tuple[str, int]:
    return "used", START_LOT


def after_commit() -> tuple[str, int]:
    return "used", START_LOT - RUN_SHEETS


def after_rollback() -> tuple[str, int]:
    return "free", START_LOT


print(crash_between(), after_commit(), after_rollback())
# ('used', 800) ('used', 400) ('free', 800)
```

## Isolation Pick

Name the anomaly each level still allows on the press database. Lots A and B hold 300 sheets each. The shop rule keeps their sum at or above 500. West takes 200 from A and east takes 200 from B, each having read a sum of 600. What is the sum afterward, and when is serializable worth its cost?

```python
LEVELS = ["read-committed", "snapshot", "serializable"]
LOT_A = 300
LOT_B = 300
TAKE = 200
FLOOR = 500
```

**Answer:** Read committed still allows a non-repeatable read: west's second read of a lot can show a commit east made in between. Snapshot isolation still allows this write skew, and the sum afterward is 200, under the floor of 500. Each writer updated a different row, so the two updates missed each other. Serializable closes both of those anomalies and aborts one of the two runs. Pay for it on a rule that spans rows this way. A unique key on one plate is the cheaper check for a single row. This is one database. Linearizability and strong consistency of replicas stay in Consistency and Replication.

```python
LEVELS = ["read-committed", "snapshot", "serializable"]
LOT_A = 300
LOT_B = 300
TAKE = 200
FLOOR = 500
ALLOWS = {
    "read-committed": "non-repeatable-read",
    "snapshot": "write-skew",
    "serializable": "none",
}


def lot_sum(lot_a: int, lot_b: int, take: int) -> int:
    return lot_a - take + lot_b - take


left = lot_sum(LOT_A, LOT_B, TAKE)
print(" ".join(ALLOWS[name] for name in LEVELS), left, left >= FLOOR)
# non-repeatable-read write-skew none 200 False
```

## Optimistic or Pessimistic

The night poster is plate P-14, and forty operators want it. Day jobs give each operator a different plate. Which strategy fits each, and what does an update that read version 7 and now finds version 8 mean when it changes 0 rows?

```python
CASES = ["night-poster", "day-jobs"]
READ_VERSION = 7
VERSION_NOW = 8
```

**Answer:** Lock first on the night poster. A conflict is the common case, and a retry would throw the work away most of the time. Check the version at commit on day jobs, where a conflict is rare. Zero rows means the version moved and this run retries. The plate stays with the operator who committed version 8.

```python
CASES = ["night-poster", "day-jobs"]
STRATEGY = {"night-poster": "pessimistic", "day-jobs": "optimistic"}
READ_VERSION = 7
VERSION_NOW = 8


def version_rows(read_version: int, now: int) -> int:
    if now != read_version:
        return 0
    return 1


print(" ".join(STRATEGY[name] for name in CASES), version_rows(READ_VERSION, VERSION_NOW))
# pessimistic optimistic 0
```

## Lock Order

West locks P-14, then waits for L-3. East locks L-3, then waits for P-14. Does this deadlock, and which rule breaks it?

```python
HOLDS = {"west": "P-14", "east": "L-3"}
WAITS = {"west": "L-3", "east": "P-14"}
```

**Answer:** Yes. Each run waits for the lock the other holds, which is a cycle. A lock timeout aborts the run that waited too long. Walking the wait-for cycle and aborting one of the two breaks it the same way. The aborted run retries. Taking P-14 before L-3 on every run makes the second run wait on P-14, and this cycle does not form.

```python
HOLDS = {"west": "P-14", "east": "L-3"}
WAITS = {"west": "L-3", "east": "P-14"}


def deadlock(holds: dict[str, str], waits: dict[str, str]) -> bool:
    return holds["east"] == waits["west"] and holds["west"] == waits["east"]


print(deadlock(HOLDS, WAITS))
# True
```

## 2PC Hang

The press book and the paper ledger have both voted yes and prepared. The coordinator dies before it sends commit or abort. What may a participant do? When is a saga the better shape?

```python
PREPARED = ("press-book", "paper-ledger")
DECISION = None
```

**Answer:** A participant that has voted yes waits. The locks it took at prepare stay held until the coordinator returns and finishes the decision. Commit and abort are both still open, so the participant chooses neither. When the press book and the paper ledger are two services, a saga is the better shape: each service commits locally, and a failed later step is repaired by a compensating write. Those compensations stay on the Saga Pattern card. The press row and an outbox row in one local commit, then a publish, are the Transactional Outbox.

```python
PREPARED = ("press-book", "paper-ledger")
DECISION = None


def participant_action(decision: str | None) -> str:
    if decision is None:
        return "wait"
    return decision


print(participant_action(DECISION), len(PREPARED))
# wait 2
```

## Majority Ack

The schedule log has 5 nodes. How many must acknowledge an entry before it is committed, and how many failures does that majority survive?

```python
NODES = 5
```

**Answer:** 3 acknowledgements commit the entry. The group still commits after 2 failures, because 3 of 5 can still answer. With 3 nodes the same rule is 2 acknowledgements and 1 failure. How many replicas a read set and a write set must share is Quorum Reads and Writes. This number is the majority on one log entry. Raft is the name for the protocol. Call etcd or ZooKeeper.

```python
NODES = 5


def majority(nodes: int) -> int:
    return nodes // 2 + 1


def failures_survived(nodes: int) -> int:
    return (nodes - 1) // 2


print(majority(NODES), failures_survived(NODES), majority(3), failures_survived(3))
# 3 2 2 1
```

## Leader Cut

West is cut off from east and loft. Three nodes, a cut of 1 against 2. Which side may elect a schedule writer, and which side must stop writing?

```python
NODES = 3
WEST = 1
EAST_AND_LOFT = 2
```

**Answer:** East and loft may elect and may keep writing the schedule. West must stop. An entry from the side of one would diverge from an entry the pair commits. Both sides writing is Split Brain. The overlapping set a replicated read and write need is Quorum Reads and Writes. Fencing a relational primary that still accepts commits is Failover and Promotion. This exercise is which side may lead.

```python
NODES = 3
WEST = 1
EAST_AND_LOFT = 2


def may_elect(side: int, nodes: int = NODES) -> bool:
    return side * 2 > nodes


print(may_elect(WEST), may_elect(EAST_AND_LOFT))
# False True
```

## Lock Lease

The holder of `press/folio` has a 10-second lease and has paused for 14 seconds. What may a new holder assume?

```python
LEASE_S = 10
PAUSED_S = 14
```

**Answer:** The new holder may take `press/folio`. The lease has expired, so the key is open. The new holder has no basis to treat the paused process as stopped. That process can resume and write as if it still held the press. An expired holder has to be fenced before those writes count. Fencing a relational primary, so the old node cannot commit, is Failover and Promotion. The steps of that fence stay on that card.

```python
LEASE_S = 10
PAUSED_S = 14


def lease_expired(paused_s: int, lease_s: int) -> bool:
    return paused_s > lease_s


print(lease_expired(PAUSED_S, LEASE_S))
# True
```
