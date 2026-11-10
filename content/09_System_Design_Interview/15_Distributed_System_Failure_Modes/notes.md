# Distributed System Failure Modes

Cove Station assigns each boat a slip and reads the tide from three houses on the breakwater. The desk can lose one house and keep assigning. It cannot look at a silence and name the cause. Six kiosks that retry on the same second can spend the capacity a single slow gauge left behind. The cards below are the modes. The repairs, the key on a retried write, and the protocol that picks one leader live in the topics that own them.

## Key Points

- **Partial failures** — some of the harbor is down and the rest keeps working. A missed deadline is a crash, a slow house, or a cut, and the desk cannot tell which.
- **Unreliable networks** — a packet can be lost, delayed, duplicated, or reordered. Lost replies and duplicates land here. The wait before a retry is Timeouts and Retries.
- **Timeouts and retries** — a short deadline marks a healthy house dead, and a long one delays failover. The gap doubles, jitter spreads the kiosks, and a retry budget caps the storm. Retry when the call is idempotent. After N failures, park the message.
- **Unreliable clocks** — a wall clock drifts and can step, so the greater stamp can be the earlier write. A monotonic clock times a duration on one machine. It does not order two houses.
- **Byzantine faults** — a peer can contradict itself. Desks the harbor runs are crash-stop, and that is the usual interview assumption. Untrusted voters are the case that assumption does not cover.
- **Split brain** — both sides of a cut accept writes, and one boat lands in two books. The side of one must stop. Fencing, an overlapping write set, and a single leader are the neighboring cards.
- **Cascading failures** — one failure recruits the next, including a retry storm. A deadline, a retry budget, a bulkhead, and load shedding limit the spread. A breaker stops calls into a failing desk, and a paused board is the reduced answer.

## Example

Six kiosks retry a slip assignment. Aligned, all six land on second 2. With a spread, the peak on one second is two, and the six retries are still issued. Last-write-wins on the wall stamps keeps slip 4. The later assignment in real time was slip 7. A side of one desk, out of three, does not keep taking writes.

```python
CALLERS = 6


def peak(jitter: bool) -> int:
    placed = [caller % 3 if jitter else 2 for caller in range(CALLERS)]
    return max(placed.count(second) for second in set(placed))


def lww_slip(stamps: list[tuple[int, int]]) -> int:
    return max(stamps)[1]


def may_take_writes(side: int, nodes: int = 3) -> bool:
    return side * 2 > nodes


print(peak(False), peak(True), lww_slip([(1300, 4), (1100, 7)]), may_take_writes(1))
# 6 2 4 False
```

The aligned peak is 6 and the spread peak is 2. Slip 4 carries the greater wall stamp, 1300 against 1100, and south's slip 7 was written later, at a real time of 1180 ms against north's 1000 ms. The single desk on the small side of the cut returns false and stops assigning. A silence from the north house still has three open causes, and the monotonic counters on two houses still do not pick a winner between those slips.

## See also

- [High Availability and Reliability](../03_High_Availability_and_Reliability/) — Failover Strategies, Multi-DC and Geo Routing, Circuit Breaker Pattern, and Graceful Degradation. A spare, a dark site, breaker behavior, and a reduced answer stay there.
- [Load Balancing](../04_Load_Balancing/) — Health Checks. Whether a server stays in the pool stays there.
- [Databases Relational](../06_Databases_Relational/) — Failover and Promotion. Fencing a relational primary stays there.
- [Consistency and Replication](../09_Consistency_and_Replication/) — Replica Failure Handling, Quorum Reads and Writes, and Conflict Resolution. Heartbeats, replica repair, the overlapping write set, and version vectors stay there.
- [Networking and Communication](../10_Networking_and_Communication/) — Idempotency. The key on a retried write stays there. Lost replies and duplicates are Unreliable Networks. The wait is Timeouts and Retries.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Dead Letter Queue. After N failures the message parks there. The wait between tries is Timeouts and Retries.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — Consensus Algorithms. How the desks agree on one leader stays there.
