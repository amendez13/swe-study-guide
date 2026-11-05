# Databases — Relational

A relational primary holds the durable rows the web tier does not. Indexes and a larger machine come first. Replicas add reads and a failover path that can drop an acknowledged commit. Sharding adds write and storage capacity and gives up local joins. Pick the store from the access path.

## Key Points

- **Relational database** — a separate durable tier of tables, constraints, and SQL. One primary takes the writes.
- **Choosing relational or NoSQL** — joins and constraints stay here. A one-key access path, or a write rate past one primary, is the NoSQL topic.
- **ACID** — atomic, constrained, isolated at a chosen level, and durable on the node that acknowledged. Read committed still allows phantoms. Durability does not survive discarding that node.
- **Normalization and denormalization** — store a fact once until a measured join, or a cross-shard read, is worth a durable copy.
- **Indexing** — a B-tree serves the leftmost prefix. Equality columns lead. A range on the first column filters the rest. Every index taxes writes.
- **Vertical database scaling** — more RAM can hold the working set. More cores do not raise the write rate when the wait is a lock or a log flush. Measure the new box.
- **Replication** — the primary acknowledges alone under asynchronous replication, so a later promotion can lose that commit. Synchronous flush on the replica you will promote closes that gap and stalls if the replica is silent.
- **Read replicas** — extra read capacity, no extra write capacity, and lag. Your own next read can use the primary. A different replica can move backward.
- **Failover and promotion** — detect, promote the furthest replica, fence the old primary, then reroute. DNS and a moved address are not a fence. The promoted replica may lack acknowledged commits.
- **Sharding** — other primaries, chosen by a key. Hash keeps one member together. A time range piles today onto one shard.
- **Sharding challenges** — hot keys, moving rows, cross-shard joins and commits, and indexes that are not the shard key.

## Example

A tool library. The primary has acknowledged through log position 80. The replica you would promote has applied through 74. Three replicas can each serve 4,000 reads a second. The member page needs 10,000.

```python
def missing_commits(acked: int, applied: int) -> int:
    return acked - applied


def read_capacity(replicas: int, each: int) -> int:
    return replicas * each


print(missing_commits(80, 74), read_capacity(3, 4000), read_capacity(2, 4000))
# 6 12000 8000
```

Six acknowledged commits are absent on that replica, so promoting it drops them. Three replicas cover the 10,000 reads. Two do not. The primary still takes every write. An index on `(member_id, created_at)` serves the member page and does not serve a date-only report.

## See also

- [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/) — key-value, document, wide-column, graph, and time-series stores.
- [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/) — fixed buckets, the ring, and how a client finds a shard.
- [Consistency and Replication](../09_Consistency_and_Replication/) — quorums, read-your-writes, and monotonic reads.
- [Caching](../05_Caching/) — a disposable copy in front of the primary.
- [High Availability and Reliability](../03_High_Availability_and_Reliability/) — site failover and detection time.
- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — vertical and horizontal scaling for the stateless tier.
