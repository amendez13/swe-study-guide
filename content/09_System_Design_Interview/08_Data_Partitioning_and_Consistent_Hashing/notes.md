# Data Partitioning and Consistent Hashing

One primary stops being enough when its write log or its disk is the ceiling. Horizontal partitioning gives each shard a subset of the rows. Vertical partitioning moves a table or a feature onto another server, which is a different move from buying a larger machine. The rest of this topic is how a key finds a shard, what moves when the cluster changes, and what to do when one key is still too hot.

## Key Points

- **Horizontal partitioning (sharding)** — different rows on different primaries once one primary's writes or disk are the ceiling. A query without the key is a scatter-gather. The Scale Cube's Z-axis is this split.
- **Vertical partitioning** — different tables, columns, or features on different servers. A bigger machine is vertical scaling, not this split.
- **Choosing a shard key** — the dominant query should hit one shard, and the key should still spread writes. The other query is a lookup.
- **Range partitioning** — contiguous spans. A range scan stays local. A clumped key leaves a hot edge.
- **Hash partitioning** — `hash(key) % N` spreads point lookups. Changing N remaps almost every key. A range scan asks every shard.
- **Consistent hashing** — hash the key, then walk clockwise to the first node. An add takes the arc from the predecessor through the new node. A remove gives that node's arc to its successor. About `1/N` of the keys move when the arcs are even.
- **Virtual nodes** — many positions per machine. The arcs even out, and an add or a remove draws from many neighbors instead of one.
- **Rebalancing** — fixed partitions, a dynamic split, or virtual nodes. Copy while traffic continues, with one owner for each write.
- **Request routing** — the client holds the partition map, a proxy holds it, or any node forwards from a map the nodes gossip.
- **Hot partition mitigation** — salt a hot key, split a hot range, or isolate the key. A salted read merges the pieces.

## Example

A ferry desk. Sailing ids 0 through 11 use `id % N`, and N goes from 4 to 5. On a separate ring the shards sit at 10, 40, and 75. A key that lands on a position belongs to that node. Past the last position, the walk wraps.

```python
def moved(n_before: int, n_after: int, keys: int) -> int:
    return sum((key % n_before) != (key % n_after) for key in range(keys))


def clockwise(key_hash: int, nodes: list[int]) -> int:
    ordered = sorted(nodes)
    for pos in ordered:
        if key_hash <= pos:
            return pos
    return ordered[0]


print(moved(4, 5, 12), clockwise(30, [10, 40, 75]), clockwise(80, [10, 40, 75]))
# 8 40 10
```

Eight of the twelve ids change shard when the modulus changes. Hash 30 belongs to the node at 40. Hash 80 wraps to the node at 10. Most of this small set moves because N is part of the address, not because those ids sat on a boundary. Adding a node on the ring steals one arc from one neighbor, which is the smaller move. The passenger page stays a lookup beside `sailing_id`. Salting a holiday sailing spreads that one key, and the sailing page merges the pieces. A gate-scan log that does not belong on the booking primary is a vertical split, not another shard of the same rows.

## See also

- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — vertical and horizontal scaling, and the Scale Cube. The Z-axis points here.
- [Databases Relational](../06_Databases_Relational/) — Database Sharding and Sharding Challenges: the relational diagnosis, cross-shard reads, and the copy.
- [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/) — store types, and why a key-value store leaves one machine.
- [Consistency and Replication](../09_Consistency_and_Replication/) — copies on the next nodes, quorums, and a read that may see an older value.
- [Caching](../05_Caching/) — cache-aside and a hot cache key. The ring those caches use is this topic.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — two-phase commit when a write must prepare on two shards.
- [High Availability and Reliability](../03_High_Availability_and_Reliability/) — a whole site going dark, which is not a ring rebalance.
