## CAP Theorem

In a network partition, a distributed system must choose between consistency (every read sees the latest write) and availability (every request gets a response). You cannot have both simultaneously during a partition.

```text
C — Consistency:   Every read returns the most recent write.
A — Availability:  Every request receives a response (no errors).
P — Partition tolerance: The system continues operating despite
                         network splits between nodes.

Since network partitions are inevitable in distributed systems,
the real choice is: CP or AP.

CP systems: refuse requests during partition to stay consistent.
  Examples: HBase, MongoDB (default), ZooKeeper

AP systems: serve requests during partition, accept stale reads.
  Examples: Cassandra, DynamoDB, CouchDB
```

In practice, most systems are not purely CP or AP — they operate on a spectrum and let you tune the trade-off per operation.

## PACELC Theorem

Extends CAP to address what happens when there is no partition, which is the common case. Even without a partition, the system trades off between latency and consistency.

```text
PAC: During a Partition, choose Availability or Consistency.
ELC: Else (no partition), choose Latency or Consistency.

Examples:
  DynamoDB:    PA/EL — available during partitions, low latency normally
  MongoDB:     PC/EC — consistent during partitions, consistent normally
  Cassandra:   PA/EL — available during partitions, low latency normally
  Spanner:     PC/EC — consistent always (uses TrueTime for global ordering)
```

PACELC is more useful than CAP for everyday design decisions because partitions are rare but the latency-consistency trade-off is constant.

## Strong Consistency

After a write completes, all subsequent reads from any node reflect that write. The system behaves as if there's only one copy of the data.

```text
Timeline:
  t0: Client A writes x = 5 to leader
  t1: Write acknowledged (replicated to all nodes synchronously)
  t2: Client B reads x from any node → gets 5 (guaranteed)

Cost:
  - Higher write latency (must wait for synchronous replication)
  - Lower availability (if a replica is down, writes may block)
  - Cannot scale writes across regions without latency penalty

When to use:
  Financial transactions, inventory counts, leader election,
  distributed locks — anywhere stale reads cause correctness bugs.
```

## Eventual Consistency

Replicas converge to the same state eventually, but may serve stale reads in the interim. The system prioritizes availability and low latency over immediate consistency.

```text
Timeline:
  t0: Client A writes x = 5 to node 1
  t1: Write acknowledged immediately (async replication starts)
  t2: Client B reads x from node 2 → might get old value (stale!)
  t3: Replication catches up
  t4: Client B reads x from node 2 → gets 5

The "eventually" window is typically milliseconds to seconds,
but can be longer during network issues or high load.

When acceptable:
  Social media feeds, view counts, product recommendations,
  DNS records — anywhere "slightly stale" doesn't break the user.

When NOT acceptable:
  Bank balances, seat reservations, distributed locks.
```

## Read-After-Write Consistency

A user always sees their own writes, even if other users may see stale data. This is the most common consistency requirement in web applications.

```text
Problem:
  User updates their profile name.
  User refreshes the page.
  Page reads from a lagging replica → shows the OLD name.
  User thinks the update failed.

Solutions:
  1. Read from leader for user's own data:
     If the user recently wrote, route their reads to the leader
     for a short window (e.g., 10 seconds).

  2. Client-supplied timestamp:
     Client sends "I last wrote at timestamp T."
     Server ensures the replica serving the read is at least
     at timestamp T, or falls back to the leader.

  3. Session consistency:
     Pin the user's session to a specific replica that has
     received all their writes.
```

## Quorum Reads and Writes

A tunable consistency mechanism for replicated systems. By requiring a quorum (majority) for reads and writes, you guarantee overlap between the read set and write set.

```text
N = total replicas
W = replicas that must acknowledge a write
R = replicas that must respond to a read

Rule: W + R > N guarantees consistency
  (at least one node in the read set saw the latest write)

Common configurations:
  N=3, W=2, R=2 — strong consistency, tolerates 1 failure
  N=3, W=3, R=1 — fast reads, slow writes, no write tolerance
  N=3, W=1, R=1 — fast everything, eventual consistency

Example with N=3, W=2, R=2:
  Write x=5 to nodes A, B (W=2 ack) → success
  Read x from nodes B, C (R=2 respond)
  Node B returns x=5, Node C returns x=3 (stale)
  Client takes the newest value: x=5 ✓
```

DynamoDB and Cassandra both use this model with configurable W and R per operation.

## Conflict Resolution

When concurrent writes create divergent state across replicas, the system needs a strategy to converge.

```text
Last-Write-Wins (LWW):
  Each write has a timestamp. The write with the latest
  timestamp wins. Simple, but silently drops concurrent writes.
  Used by: Cassandra (default)

Vector Clocks:
  Each node maintains a version vector [A:3, B:1, C:2].
  Concurrent writes are detected (neither version dominates).
  Application must merge or present both versions to the user.
  Used by: Amazon DynamoDB (originally), Riak

Application-Level Merge:
  The application defines merge logic for the data type.
  Example: shopping cart — union of all items from both versions.
  Most correct, but requires domain-specific code.

CRDTs (Conflict-Free Replicated Data Types):
  Data structures that merge automatically without coordination.
  Examples: counters, sets, registers, maps.
  Used by: Redis (CRDT-based active-active), Riak
```

In interviews, mention LWW as the simple default and note that it can lose data. If the problem requires correctness (shopping carts, collaborative editing), discuss application-level merge or CRDTs.

## Linearizability

The strongest consistency model: operations appear to take effect at a single instant between invocation and response, as if all clients are talking to a single copy of the data.

```text
Linearizable:
  If write W completes before read R starts (in real time),
  R must see the effect of W. No exceptions.

Required for:
  Leader election — only one node can believe it's the leader.
  Distributed locks — only one process holds the lock.
  Unique constraints — only one user can claim a username.

Not required for:
  Most application reads — eventual or read-after-write is enough.
  Analytics — stale data is fine.
  Caching — stale by design.

Cost:
  High latency (requires coordination across nodes).
  Unavailable during network partitions (CP behavior).
  Implemented via consensus protocols (Raft, Paxos).

Examples of linearizable systems:
  ZooKeeper, etcd, Google Spanner
```
