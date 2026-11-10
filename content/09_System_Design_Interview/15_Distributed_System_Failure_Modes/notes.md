# Distributed System Failure Modes

A distributed system fails in pieces. One replica can be silent while the other two still answer, and a timeout still leaves open whether that replica crashed, ran slowly, or lost its path. A payment call can lose a confirmation, see it late, see it twice, or see two updates arrive out of send order. Six clients that retry on the same second can spend the capacity one slow downstream call left behind. The cards are those modes. Pool membership, replica repair, the idempotency key, the dead-letter count, fencing, leader election, the breaker, and the reduced answer stay in the topics that own them.

## Key Points

- **Partial failures** — some of the cluster is down and the rest keeps working. A missed deadline is a crash, a slow replica, or a cut link, and this attempt leaves the cause unnamed.
- **Unreliable networks** — a message can be lost, delayed, duplicated, or reordered. Lost replies and duplicates land here. The wait before a retry is Timeouts and Retries.
- **Timeouts and retries** — a deadline under the healthy band marks a live processor dead, and a long deadline delays failover. The gap doubles, jitter spreads the clients, and a retry budget caps the storm. Retry when the call is idempotent. After N failures, park the message.
- **Unreliable clocks** — a wall clock drifts and can step, so the greater stamp can be the earlier write. A monotonic clock times a duration on one machine. Two monotonic clocks have two boot origins, so the write order stays open.
- **Byzantine faults** — a participant can present two claims. Nodes you operate are crash-stop, and that is the usual interview assumption. Untrusted voters are the Byzantine case.
- **Split brain** — both sides of a cut accept writes, and one booking lands in two histories. The side of one must stop. Fencing, an overlapping write set, and a single leader are the neighboring cards.
- **Cascading failures** — one failure recruits the next, including a retry storm. A deadline, a retry budget, a bulkhead, and load shedding limit the spread. A breaker stops calls into a failing dependency, and a paused page is the reduced answer.

## Example

Six payment clients each retry once. Aligned, all six land on second 2. With a spread, client `i` lands on second `i % 3`, the peak on one second is two, and all six retries are still issued. Last-write-wins on the wall stamps keeps value 4. The later write in real time was value 7. A side of one node, out of three, stops taking writes.

```python
CALLERS = 6


def peak(jitter: bool) -> int:
    placed = [caller % 3 if jitter else 2 for caller in range(CALLERS)]
    return max(placed.count(second) for second in set(placed))


def lww_value(stamps: list[tuple[int, int]]) -> int:
    return max(stamps)[1]


def may_take_writes(side: int, nodes: int = 3) -> bool:
    return side * 2 > nodes


print(peak(False), peak(True), lww_value([(1300, 4), (1100, 7)]), may_take_writes(1))
# 6 2 4 False
```

The aligned peak is 6 and the spread peak is 2. Value 4 carries the greater wall stamp, 1300 against 1100. Value 7 was written later, at a real time of 1180 ms against replica A's 1000 ms. The single node on the small side of the cut returns false and stops taking writes. A silence from one replica still has three open causes, and the monotonic counters on two replicas still leave the winner between those values open.

## See also

- [High Availability and Reliability](../03_High_Availability_and_Reliability/) — Failover Strategies, Multi-DC and Geo Routing, Circuit Breaker Pattern, and Graceful Degradation. A spare, a dark site, breaker behavior, and a reduced answer stay there.
- [Load Balancing](../04_Load_Balancing/) — Health Checks. Whether a server stays in the pool stays there.
- [Databases Relational](../06_Databases_Relational/) — Failover and Promotion. Fencing a relational primary stays there.
- [Consistency and Replication](../09_Consistency_and_Replication/) — Replica Failure Handling, Quorum Reads and Writes, and Conflict Resolution. Heartbeats, replica repair, the overlapping write set, and version vectors stay there.
- [Networking and Communication](../10_Networking_and_Communication/) — Idempotency. The key on a retried write stays there. Lost replies and duplicates are Unreliable Networks. The wait is Timeouts and Retries.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Dead Letter Queue. After N failures the message parks there. The wait between tries is Timeouts and Retries.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — Consensus Algorithms. How an etcd or ZooKeeper ensemble agrees on one leader stays there.
