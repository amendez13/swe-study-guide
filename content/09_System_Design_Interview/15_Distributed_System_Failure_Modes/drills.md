# Distributed System Failure Modes — Drills

Original practice for what a silence can mean, what a packet can do, and which cut stops a cascade. Each card is one exercise: commit to an answer, then check it. The numbers are invented for Cove Station, where a desk reads three tide houses and assigns a boat a slip. Pool membership stays in Load Balancing. Replica repair stays in Consistency and Replication. Fencing a relational primary stays in Databases Relational. The idempotency key stays in Networking and Communication. Parking a message after N failures stays in Message Queues and Async Processing. Breaker behavior, a reduced answer, and a second site stay in High Availability and Reliability. Agreeing on one leader stays in Transactions and Concurrency Control.

## Slow or Dead

The desk asked the north house for a tide at t = 0. The deadline is 200 ms. No bytes came back. What can the desk conclude, and what stays open?

```python
OBSERVED = "silence"
CAUSES = ("crash", "slow", "cut")
```

**Answer:** The desk can conclude that the deadline was missed. It cannot conclude that the north house crashed. A slow house and a cut link produce the same silence, so all three causes stay open. This attempt stops waiting on that house and leaves the cause unnamed. Whether a server leaves a pool is Health Checks. The heartbeat that drops a replica from one attempt, and the repair after, is Replica Failure Handling.

```python
OBSERVED = "silence"
CAUSES = ("crash", "slow", "cut")


def named_cause(observed: str) -> str:
    if observed == "silence":
        return "unknown"
    return observed


print(named_cause(OBSERVED), len(CAUSES))
# unknown 3
```

![Slow or Dead](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills-1-slow-or-dead.png)

*Source: [`diagrams/failure-modes-drills.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills.drawio), page 1.*

## Packet Mode

Four grants leave the desk. Name what the kiosk has to tolerate in each case, and what a retry of the slip write requires.

```text
1. lost — boat 12's grant never arrives.
2. delayed — the grant arrives after the kiosk has already sent the assignment again.
3. duplicated — the same grant is delivered twice.
4. reordered — boat 18's grant arrives before boat 12's, and boat 12 was sent first.
```

```python
MODES = ["lost", "delayed", "duplicated", "reordered"]
```

**Answer:** A missing grant, a late grant, a second copy, and an arrival order that differs from send order. Silence still does not say whether the grant was lost, is still in flight, or met a desk that has stopped. A second copy has to leave one assignment in place. Send order is a poor stand-in for the order the kiosk applies. A retry of the slip write is safe when a second call leaves the first assignment as it was, which is Idempotency. The key that makes that true stays on that card. The deadline and the gap before the retry are Timeouts and Retries.

```python
MODES = ["lost", "delayed", "duplicated", "reordered"]
TOLERATE = {
    "lost": "missing",
    "delayed": "late",
    "duplicated": "second-copy",
    "reordered": "arrival-order",
}

print(" ".join(TOLERATE[mode] for mode in MODES))
# missing late second-copy arrival-order
```

![Packet Mode](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills-2-packet-mode.png)

*Source: [`diagrams/failure-modes-drills.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills.drawio), page 2.*

## Timeout Tune

Healthy houses answer in 40 to 90 ms. Classify a deadline of 30 ms, one of 200 ms, and one of 30 seconds.

```python
HEALTHY_MS = range(40, 91)
CANDIDATES_MS = (30, 200, 30_000)
```

**Answer:** 30 ms is a false death. Every healthy answer sits above it, so the desk treats a live house as down and can move work off it. 200 ms sits above the healthy range, so a house that answers on time stays, and a house that is gone is noticed at 200 ms. 30 seconds is slow detection. A crashed house holds the slip threads for 30 seconds, and failover waits out that deadline. The length of the deadline is the whole of this choice. The growing gap after the miss is Backoff and Jitter.

```python
HEALTHY_MS = range(40, 91)
CANDIDATES_MS = (30, 200, 30_000)


def false_death(deadline_ms: int) -> bool:
    return deadline_ms < max(HEALTHY_MS)


print(false_death(30), false_death(200), CANDIDATES_MS[2] // 1000)
# True False 30
```

![Timeout Tune](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills-3-timeout-tune.png)

*Source: [`diagrams/failure-modes-drills.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills.drawio), page 3.*

## Backoff and Jitter

Six kiosks retry once. Aligned, every kiosk sends at second 2. With a spread, kiosk `i` sends at second `i % 3`. How many retries are issued in each schedule, and what is the peak on one second?

```python
CALLERS = 6
```

**Answer:** Both schedules issue 6 retries. The aligned peak is 6, all of them on second 2, which is the dip turning into a storm. The spread peak is 2. The same work hurts less when it does not share a second. A later gap of 4 seconds piles up the same way if every kiosk still shares it. The cap that refuses retries past a budget, so the fleet stops adding calls, is the retry budget on Timeouts and Retries. This count is only the spread.

```python
CALLERS = 6


def placed(jitter: bool) -> list[int]:
    return [caller % 3 if jitter else 2 for caller in range(CALLERS)]


def peak(slots: list[int]) -> int:
    return max(slots.count(second) for second in set(slots))


aligned = placed(False)
spread = placed(True)
print(len(aligned), peak(aligned), len(spread), peak(spread))
# 6 6 6 2
```

![Backoff and Jitter](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills-4-backoff-and-jitter.png)

*Source: [`diagrams/failure-modes-drills.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills.drawio), page 4.*

## Clock Order

North stamped slip 4 at a wall time of 1300 ms. South stamped slip 7 at a wall time of 1100 ms. In real time, north wrote at 1000 ms and south wrote at 1180 ms. North's monotonic counter reads 4,200,000,000. South's reads 90,000,000. Which slip does last-write-wins keep, which slip was later, and what do the monotonic readings add?

```python
NORTH_WALL = (1300, 4)
SOUTH_WALL = (1100, 7)
NORTH_REAL = (1000, 4)
SOUTH_REAL = (1180, 7)
NORTH_MONO_NS = 4_200_000_000
SOUTH_MONO_NS = 90_000_000
```

**Answer:** Last-write-wins keeps slip 4, because 1300 is the greater wall stamp. Slip 7 is the later write: real time 1180 ms is after 1000 ms. The stamp that won belongs to the earlier assignment. The monotonic readings do not repair the order. Each counter times durations on its own house, from its own boot. South's smaller number means south booted more recently. It does not mean south's slip happened first. Why a wall-clock stamp is a weak input to that pick is Conflict Resolution.

```python
NORTH_WALL = (1300, 4)
SOUTH_WALL = (1100, 7)
NORTH_REAL = (1000, 4)
SOUTH_REAL = (1180, 7)


def later_slip(stamps: list[tuple[int, int]]) -> int:
    return max(stamps)[1]


print(later_slip([NORTH_WALL, SOUTH_WALL]), later_slip([NORTH_REAL, SOUTH_REAL]))
# 4 7
```

![Clock Order](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills-5-clock-order.png)

*Source: [`diagrams/failure-modes-drills.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills.drawio), page 5.*

## Crash or Byzantine

Two groups interact with the desk. Which fault model fits each group?

```text
1. desk-trio — three desks the harbor operates. A desk follows the protocol, or it stops answering.
2. open-peers — boats the harbor does not operate submit slip claims. A boat can send one claim to one desk and a different claim to another.
```

```python
CASES = ["desk-trio", "open-peers"]
```

**Answer:** Crash-stop for the desk trio, and that is the assumption to state for machines the harbor runs. Byzantine for the open peers: a participant that can present two claims is outside crash-stop. Most interview designs stay with the desks you operate and say so. The protocol that tolerates liars, and the extra nodes it needs, stays outside this catalog.

```python
CASES = ["desk-trio", "open-peers"]
MODEL = {"desk-trio": "crash-stop", "open-peers": "byzantine"}

print(" ".join(MODEL[name] for name in CASES))
# crash-stop byzantine
```

![Crash or Byzantine](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills-6-crash-or-byzantine.png)

*Source: [`diagrams/failure-modes-drills.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills.drawio), page 6.*

## Split Quorum

Three desks, and a cut of one against two. Which side may elect and keep taking slip writes? What goes wrong if the single desk keeps assigning too?

```python
NODES = 3
SIDES = (1, 2)
```

**Answer:** The side of two may elect and may keep taking writes. The side of one must stop. A single desk that keeps assigning, while the pair also assigns, puts boat 12 in two books. That is split brain. Fencing a relational primary that still accepts writes is Failover and Promotion. The overlap a replicated write needs before it can finish is Quorum Reads and Writes. How the three desks agree on one leader is Consensus Algorithms.

```python
NODES = 3
SIDES = (1, 2)


def may_take_writes(side: int, nodes: int = NODES) -> bool:
    return side * 2 > nodes


print(may_take_writes(SIDES[0]), may_take_writes(SIDES[1]))
# False True
```

![Split Quorum](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills-7-split-quorum.png)

*Source: [`diagrams/failure-modes-drills.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills.drawio), page 7.*

## Cascade Cut

The south gauge slows, and the harbor comes apart in six steps. Name the cut for each step. Point at High Availability and Reliability where the cut is a breaker or a reduced answer.

```text
1. threads-wait — slip threads sit on the slow gauge with no deadline.
2. same-second — six kiosks retry on the same second, with no cap.
3. shared-pool — the tide board and the slip calls share one thread pool.
4. past-cap — the queue is past its cap and the desk still accepts every boat.
5. keep-calling — callers keep sending to a desk that is already failing.
6. blank-board — the public board goes blank where "assignments paused" would do.
```

```python
STEPS = [
    "threads-wait",
    "same-second",
    "shared-pool",
    "past-cap",
    "keep-calling",
    "blank-board",
]
```

**Answer:** Deadline, retry budget, bulkhead, shed, breaker, degraded response. The deadline frees the thread. The retry budget caps the storm, and the spread that keeps those retries off one second is Backoff and Jitter. The bulkhead is the tide board's own pool. Shedding rejects the extra boat once the queue is past its cap. Stopping the calls into a desk that is already failing is the Circuit Breaker Pattern. Answering "assignments paused" is Graceful Degradation. Those two cuts stay in High Availability and Reliability.

```python
STEPS = [
    "threads-wait",
    "same-second",
    "shared-pool",
    "past-cap",
    "keep-calling",
    "blank-board",
]
CUT = {
    "threads-wait": "deadline",
    "same-second": "retry-budget",
    "shared-pool": "bulkhead",
    "past-cap": "shed",
    "keep-calling": "breaker",
    "blank-board": "degraded",
}

print(" ".join(CUT[step] for step in STEPS))
# deadline retry-budget bulkhead shed breaker degraded
```

![Cascade Cut](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills-8-cascade-cut.png)

*Source: [`diagrams/failure-modes-drills.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-drills.drawio), page 8.*
