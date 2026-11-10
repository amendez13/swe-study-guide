# Message Queues and Async Processing — Drills

Original practice for what waits on a bus, who receives a message, and what a crash leaves behind. Each card is one exercise: commit to an answer, then check it. The numbers are invented for a cooperative seed vault. HTTP idempotency keys stay in Networking and Communication. Event-driven architecture and sagas stay in Microservices and System Decomposition. Stream processing, change data capture, and event sourcing stay in Storage and Data Processing at Scale. Timeout and backoff modes stay in Distributed System Failure Modes. Two-phase commit stays in Transactions and Concurrency Control. Rate-limit algorithms stay in Rate Limiting and Throttling. Notification delivery and feed fan-out stay in Real-Time and Notification Systems. Lag and depth as metrics stay in Observability.

## Queue or Not

A grower is at the intake desk. Four steps belong to this visit. Say which stay on the request and which go on the bus, and why.

```text
1. lot-slip — print the lot number on the paper the grower takes home.
2. accept-rule — the moisture meter says take the packet or refuse it, while the grower is standing there.
3. germination — a seven-day tray. The grower leaves with the slip.
4. yearbook — the annual diversity tally, published next winter.
```

```python
STEPS = ["lot-slip", "accept-rule", "germination", "yearbook"]
SYNC = {"lot-slip", "accept-rule"}
```

**Answer:** `lot-slip` and `accept-rule` stay on the request. The grower cannot leave with a blank slip, and the accept-or-refuse answer is the response. Putting either step on the bus keeps the grower waiting and adds a broker outage to a write the desk can do itself. `germination` and `yearbook` go on the bus. The slip is already in the grower's hand, the tray takes a week, and the tally is a later reader. The caller does not need those results to finish this visit.

```python
STEPS = ["lot-slip", "accept-rule", "germination", "yearbook"]
SYNC = {"lot-slip", "accept-rule"}

print(" ".join("sync" if step in SYNC else "queue" for step in STEPS))
# sync sync queue queue
```

## Point-to-Point or Pub/Sub

Assign each case to point-to-point, pub/sub, or consumer groups on one log.

```text
1. one-tray — one technician starts the germination tray. A second technician must not start it too.
2. three-desks — the catalog, the freezer inventory, and the diversity tally each record every finished tray.
3. split-lab — several technicians share the trays, and the catalog still records every finish.
```

```python
CASES = ["one-tray", "three-desks", "split-lab"]
```

**Answer:** Point-to-point, pub/sub, then consumer groups. One tray is one job, so one consumer takes it and the others do not. The three desks are independent subscribers, and each needs its own copy. The split lab is one group whose members divide the partitions, and the catalog is a second group on the same log, so it still sees every finish. Services that react across a boundary, and a saga's compensations, stay in Microservices and System Decomposition. A feed that writes a post into many timelines, or builds the timeline on read, stays in Real-Time and Notification Systems.

```python
CASES = ["one-tray", "three-desks", "split-lab"]
CHOICE = {
    "one-tray": "point-to-point",
    "three-desks": "pub-sub",
    "split-lab": "groups",
}

print(" ".join(CHOICE[name] for name in CASES))
# point-to-point pub-sub groups
```

## Delivery Pick

Name the contract for each case, and say what the lost acknowledgement does.

```text
1. humidity — one reading a minute from the drying room. A lost reading is replaced by the next one.
2. accession — the packet must be recorded. Handling the same message twice must not create a second lot.
3. lost-ack — the technician finished packet-17, and the acknowledgement never reached the broker.
```

```python
HUMIDITY: list[str] = []
ACCESSION = ["packet-17", "packet-17"]
```

**Answer:** At-most-once for the humidity reading, because a loss is acceptable and nobody retries it. At-least-once plus an idempotent consumer for the accession. That is the practical default: the broker retries until it sees an ack, and the handler stores the message id so a second delivery finds the lot and stops. The lost ack redelivers packet-17. With no idempotent handler the vault inserts a second lot. With the message id stored, the effect count stays 1. The visibility window on a queue, and an offset committed after the work on a log, are the two ways that retry happens. The HTTP header on a retried POST stays in Networking and Communication. Whether a phone shows a notice once stays in Real-Time and Notification Systems.

```python
def effects(deliveries: list[str], idempotent: bool) -> int:
    seen: set[str] = set()
    count = 0
    for name in deliveries:
        if idempotent and name in seen:
            continue
        seen.add(name)
        count += 1
    return count


HUMIDITY: list[str] = []
ACCESSION = ["packet-17", "packet-17"]

print(effects(HUMIDITY, True), effects(ACCESSION, False), effects(ACCESSION, True))
# 0 2 1
```

## Idle Consumers

The germination log has a fixed partition count. For each pair, how many technicians do work, and how many sit idle?

```python
CASES = [(4, 6), (8, 3)]
```

**Answer:** `(4, 2)` and `(3, 0)`, as `(working, idle)`. A member with no partition assigned does nothing. Six technicians and four partitions leave two idle, and adding those two does not raise throughput. Eight partitions and three technicians keep all three busy, and some hold more than one partition. The idle number is `max(consumers - partitions, 0)`. More parallelism means more partitions, and order still holds only within a key, which is Key Order.

```python
CASES = [(4, 6), (8, 3)]


def assignment(partitions: int, consumers: int) -> tuple[int, int]:
    working = min(partitions, consumers)
    return working, consumers - working


print([assignment(*case) for case in CASES])
# [(4, 2), (3, 0)]
```

## Key Order

The desk published three events, in this order: packet-17 received, packet-18 received, packet-17 weighed. The log has four partitions. packet-17 maps to partition 2. packet-18 maps to partition 0. What can a consumer assume, and what does a single global order cost?

```python
SLOT = {"packet-17": 2, "packet-18": 0}
PARTITIONS_FOR_GLOBAL = 1
TECHNICIANS = 5
```

**Answer:** packet-17 received and packet-17 weighed share partition 2, so the member who reads that partition sees weighed after received. packet-18 is on partition 0. The member reading packet-17 learns nothing about where packet-18 sits relative to those two events. Order is per key, because the key chooses the partition. A global order means one partition for the whole log. The group then has one working technician, and the other four sit idle. `min(1, 5)` is 1 working, and `5 - 1` is 4 idle.

```python
SLOT = {"packet-17": 2, "packet-18": 0}
PARTITIONS_FOR_GLOBAL = 1
TECHNICIANS = 5


def same_partition(left: str, right: str) -> bool:
    return SLOT[left] == SLOT[right]


working = min(PARTITIONS_FOR_GLOBAL, TECHNICIANS)
idle = TECHNICIANS - working
print(same_partition("packet-17", "packet-17"), same_partition("packet-17", "packet-18"), working, idle)
# True False 1 4
```

## Backpressure Move

Intake publishes 90 packets an hour. The lab finishes 30 an hour per technician, and one technician is running. Depth is already 600, and the rush holds this rate. What does five more hours of buffering alone do to the depth? What is the move when every packet has to be kept?

```python
IN_RATE = 90
PER_TECHNICIAN = 30
START = 600
HOURS = 5
```

**Answer:** Depth is 900 after five hours, because each hour adds `90 - 30` packets and `600 + 60 * 5` is 900. The rush does not end, so the depth keeps climbing and the broker's disk is the limit. Buffering fits a spike that drains later. It does not fit a rate that stays ahead. Dropping accessions loses packets the vault promised to keep. The move is to scale technicians to 3, which is the smallest count whose 30-an-hour pace matches 90. If the extra technicians cannot start in time, throttle intake so the desk stops accepting faster than the lab finishes. The limiter that refuses a grower stays in Rate Limiting and Throttling. Lag and depth, as numbers on a page, stay in Observability. Scaling past the partition count leaves technicians idle, which is Idle Consumers.

```python
IN_RATE = 90
PER_TECHNICIAN = 30
START = 600
HOURS = 5


def depth(hours: int) -> int:
    return START + (IN_RATE - PER_TECHNICIAN) * hours


def technicians_to_match(in_rate: int, per_technician: int) -> int:
    return (in_rate + per_technician - 1) // per_technician


print(depth(HOURS), technicians_to_match(IN_RATE, PER_TECHNICIAN))
# 900 3
```

## DLQ Trip

A packet that fails the tray handler is retried. The limit is 3. packet-9 has failed 3 times. packet-10 has failed once. packet-11 and packet-12 are still waiting and have not failed. What is on the dead letter queue, what stays on the main queue, and do packet-11 and packet-12 still move?

```python
MAX_TRIES = 3
ATTEMPTS = {"packet-9": 3, "packet-10": 1}
WAITING = ["packet-11", "packet-12"]
```

**Answer:** packet-9 is on the dead letter queue. packet-10, packet-11, and packet-12 stay on the main queue. packet-11 and packet-12 still move, because the poison packet left the main queue at the third failure instead of sitting at the head. packet-10 gets another try. The wait between those tries stays in Distributed System Failure Modes. A growing dead letter queue is a processing failure of its own, and its depth is a metric in Observability.

```python
MAX_TRIES = 3
ATTEMPTS = {"packet-9": 3, "packet-10": 1}
WAITING = ["packet-11", "packet-12"]


def split(attempts: dict[str, int], waiting: list[str], limit: int) -> tuple[list[str], list[str]]:
    dlq = [name for name, tries in attempts.items() if tries >= limit]
    main = [name for name, tries in attempts.items() if tries < limit] + waiting
    return dlq, main


print(split(ATTEMPTS, WAITING, MAX_TRIES))
# (['packet-9'], ['packet-10', 'packet-11', 'packet-12'])
```

## Outbox Crash

The intake service commits the packet row for packet-17, then the process dies before the publish call returns. packet-18 was never started. What does that dual write leave for subscribers? What does an outbox row, inserted in the same transaction as the packet row, leave for a publisher that starts after the restart?

```python
COMMITTED = ["packet-17"]
PUBLISHED: list[str] = []
```

**Answer:** Subscribers see nothing. The table holds packet-17, and the publish never happened, so the catalog and the tally stay unaware of a packet the vault already accepted. Restarting the intake process does not republish, because the event lived only in memory after the commit. The outbox row committed with the packet row, and it is still marked unsent. The publisher reads it and sends packet-17. A crash after that send and before the sent mark sends packet-17 again, so the subscriber still treats it as one lot. The other dual-write gap, publishing and then dying before the commit, would announce a packet the table does not hold. The outbox publishes a row only after that row has committed. Two-phase commit would ask the database and the broker to prepare together, and that protocol stays in Transactions and Concurrency Control. A saga would compensate other services, and that chain stays in Microservices and System Decomposition.

```python
def pending(committed: list[str], published: list[str]) -> list[str]:
    done = set(published)
    return [name for name in committed if name not in done]


print(pending(["packet-17"], []), pending(["packet-17"], ["packet-17"]))
# ['packet-17'] []
```
