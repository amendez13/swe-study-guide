# Consistency and Replication

The fundamental trade-off in distributed systems: how fresh does the data need to be, and what are you willing to pay for that freshness? Every system design interview touches this trade-off because any system with more than one database node must choose a consistency model.

## Key Points

- **CAP theorem** — during a partition, choose consistency or availability. Since partitions are inevitable, the real choice is CP or AP.
- **PACELC** — extends CAP: even without a partition, trade off latency vs. consistency. More useful for everyday design decisions.
- **Strong consistency** — all reads see the latest write. Requires synchronous replication. Use for financial transactions, locks, inventory.
- **Eventual consistency** — replicas converge eventually, but reads may be stale. Use for feeds, view counts, recommendations.
- **Read-after-write** — a user sees their own writes. Achieved by reading from the leader for recently-written data.
- **Quorum (W + R > N)** — tunable consistency. More replicas in the quorum means stronger consistency but slower operations.
- **Conflict resolution** — LWW (simple, lossy), vector clocks (detect conflicts), application-level merge (domain-specific), CRDTs (automatic merge).
- **Linearizability** — strongest model. Operations appear instantaneous. Required for leader election and distributed locks. Implemented via consensus protocols.

## Example

Choosing a consistency model for different features in a social media platform:

```text
Feature: Post "like" count
  Model: Eventual consistency
  Why: A like count that's 2 seconds stale is fine.
       Prioritize low write latency — millions of likes/minute.
  Config: N=3, W=1, R=1

Feature: User profile update
  Model: Read-after-write consistency
  Why: User must see their own profile changes immediately.
       Other users can see stale profile for a few seconds.
  Config: N=3, W=2, R=2 for the user's own reads;
          W=2, R=1 for other users' reads.

Feature: Username uniqueness
  Model: Linearizability
  Why: Two users cannot claim the same username simultaneously.
       This requires a global ordering of operations.
  Implementation: Write to a linearizable store (PostgreSQL with
  SERIALIZABLE isolation, or a distributed lock via ZooKeeper).

Feature: Direct message delivery
  Model: Strong consistency (per-conversation)
  Why: Messages must appear in order. A user sending "yes" then
       "wait, no" must not have those delivered out of order.
  Config: Partition messages by conversation_id, use a single
          leader per partition for ordered writes.
```

The key insight: different features in the same system can use different consistency models. Match the model to the feature's tolerance for staleness.
