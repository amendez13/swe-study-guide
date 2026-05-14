## Partial Failures

In a distributed system, some components fail while others continue normally. Unlike a single-machine program where the whole process crashes, a distributed system must tolerate and reason about partial failure.

```text
Examples:
  One of 10 database replicas becomes unreachable.
  A network switch fails, partitioning 3 of 20 servers.
  One microservice has a memory leak; others are healthy.
  A single disk fails on one storage node in a 100-node cluster.

Key challenge:
  You can't always tell if a remote node has crashed, is slow,
  or if the network between you and it is broken. All three
  look the same from the caller's perspective: no response.
```

Designing for partial failure means assuming that any component can fail at any time and building in detection (health checks, timeouts), isolation (bulkheads, circuit breakers), and recovery (retries, failover, replication).

## Unreliable Networks

The network between distributed components can lose, delay, duplicate, or reorder packets. These are not edge cases — they happen routinely at scale.

```text
Failure modes:
  Lost packet     — request or response never arrives
  Delayed packet  — arrives after the timeout
  Duplicated      — same packet delivered twice
  Reordered       — packets arrive out of send order

Detection mechanism: timeouts
  If no response within T milliseconds, assume failure.
  But T too short → false positives (mark healthy nodes as dead).
  T too long → slow failure detection.

  Typical approach:
    Aggressive timeout + retry with exponential backoff + jitter.
    e.g., timeout 500ms, retry at 1s, 2s, 4s with ±random jitter.
```

Network unreliability is why idempotency, retries, and at-least-once delivery guarantees are standard in distributed systems.

## Unreliable Clocks

Physical clocks on different machines drift and cannot be perfectly synchronized. Relying on wall-clock time for ordering events across machines is fundamentally unsafe.

```text
Two types of clocks:

  Time-of-day clock:
    Returns wall-clock time (e.g., 2024-03-15T10:30:00Z).
    Synchronized via NTP, but can jump backward after correction.
    NOT safe for ordering events or measuring durations.

  Monotonic clock:
    Returns an always-increasing counter (e.g., nanoseconds since boot).
    Never jumps backward. Safe for measuring durations on one machine.
    NOT comparable across machines.

Why this matters:
  Machine A's clock: 10:30:00.000
  Machine B's clock: 10:30:00.150 (150ms ahead due to drift)
  Event on A at 10:30:00.100 and event on B at 10:30:00.050
  Wall-clock says B was first. Real time says A was first.
  → Last-write-wins with wall-clock timestamps can silently lose data.

Solutions:
  Logical clocks (Lamport timestamps, vector clocks)
  Google TrueTime (GPS + atomic clocks, bounded uncertainty)
  Hybrid logical clocks (combine physical and logical)
```

## Byzantine Faults

A node behaves arbitrarily or maliciously — sending contradictory messages to different peers, corrupting data, or lying about its state. Named after the Byzantine Generals Problem.

```text
Crash-stop faults:
  A node either works correctly or stops responding.
  Most internal systems assume this model.
  Handled by: timeouts, retries, failover.

Byzantine faults:
  A node actively misbehaves (bug, corruption, malicious actor).
  Requires special protocols (PBFT, Byzantine consensus).
  Much more expensive — typically needs 3f+1 nodes to tolerate f faults.

When to worry about Byzantine faults:
  ✓ Blockchain and cryptocurrency networks
  ✓ Aviation and aerospace systems
  ✗ Internal microservices (trust the nodes, just handle crashes)
  ✗ Most system design interview scenarios
```

In interviews, briefly mention: "We're assuming crash-stop failures, not Byzantine." This shows you know the distinction without over-designing.

## Split Brain

A network partition where both sides of the split believe they are the active leader, causing conflicting writes and data divergence.

```text
Scenario:
  Cluster: Node A (leader), Node B, Node C
  Network partition separates A from {B, C}.

  Node A still thinks it's the leader → accepts writes.
  Nodes B and C can't reach A → elect B as new leader.
  B also accepts writes → TWO leaders, conflicting data!

Prevention:
  Fencing tokens:
    Leader election assigns a monotonically increasing token.
    Old leader's writes are rejected because its token is stale.

  Quorum-based election:
    Leader needs majority (>N/2) acknowledgment to operate.
    In a 3-node cluster, a partition of {A} vs {B,C}:
    A has 1/3 → cannot maintain quorum → steps down.
    {B,C} has 2/3 → elects new leader. ✓

  Consensus protocols (Raft, Paxos):
    Built-in leader election with split-brain prevention.
    Used by ZooKeeper, etcd, Consul.
```

## Cascading Failures

A failure in one component triggers failures in others, spreading through the system like dominoes. The most dangerous failure mode because it can turn a minor issue into a total outage.

```text
Example chain:
  1. Database gets slow (disk issue).
  2. App servers wait on DB → thread pools fill up.
  3. App servers can't accept new requests → LB marks them unhealthy.
  4. Remaining app servers get ALL traffic → they also overload.
  5. Total outage.

Prevention:
  Timeouts:       Don't wait forever for a slow dependency.
  Circuit breakers: Stop calling a failing service.
  Bulkheads:      Isolate thread pools per dependency so one
                  slow service doesn't exhaust all threads.
  Load shedding:  Reject excess requests early (return 503)
                  rather than trying to serve them all poorly.
  Retries with backoff: Prevent retry storms from amplifying load.
```

In interviews, when you identify a single point of failure, also trace the cascading failure path: "If this database goes down, what happens to the services that depend on it?"
