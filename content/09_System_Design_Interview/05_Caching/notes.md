# Caching

An application cache keeps a volatile copy of a row or of a result you would otherwise recompute, so the next reader can skip that work. It helps when the same keys come back and a bounded stale window is acceptable. The database stays the source of truth, except while write-behind holds an acknowledged write that has not been flushed. Shared public delivery for a distant audience stays in Content Distribution and Media.

## Key Points

- **When caching helps** — repeated expensive reads, and a caller that can accept a bounded stale window. Eviction, expiry, and restarts drop the copy. The hit ratio comes from a measurement on this workload.
- **Cache tier placement** — an in-process copy has no network hop and is private to the instance. A shared tier scales memory and request rate apart from the application fleet.
- **Hit ratio math** — mean latency weights hits and misses by a measured ratio. Database reads equal misses only when each miss performs one read and errors are counted honestly.
- **Cache-aside** — the application reads the cache, fills a miss with a TTL, commits the database, then deletes the key. The writer deletes because it often cannot rebuild the cached document.
- **Read-through / write-through** — the cache loads a miss itself, and a write acknowledges only after the database commit. Unread keys still get stored. A cache outage fails the write unless the application bypasses.
- **Write-behind** — acknowledge from the cache and flush later. A crash loses dirty keys that never reached a replica or the database. A miss must not cover a dirty key with the older row.
- **Eviction policies** — LRU drops the least recently used key when memory is full. Exact LRU is a map plus a doubly linked list. Expiry is a separate mechanism. FIFO ignores reuse.
- **TTL tuning** — too short lowers the hit ratio. Too long widens a missed invalidation. Add jitter so fills that landed together do not expire together. A TTL does not size the cache.
- **Cache invalidation** — commit, then delete. A reader that already loaded the old row can store it after the delete. A lease or a tombstone rejects that store. A bare delete leaves nothing to compare. Negative markers stay short and are deleted on create.
- **Stampede protection** — one loader per key, or serve the previous value while one refresh runs. Jitter spreads aligned expiry. A deleted key still needs the loader.
- **Hot key mitigation** — one key on one node saturates that node. Copy a read-mostly document and read a random replica, or keep a short process copy. Split a key only when the reader can merge the parts. A cluster replica spreads the key only when reads may use that other copy.
- **Distributed cache** — partition keys so memory and request rate spread. Consistent hashing moves about `1/N` of the keys when a node joins. A replica saves the keys and can serve a stale read.
- **Failure and overprovisioning** — a dead single node sends the full read rate at the database if callers fall through. One cold node of N adds about `h * R / N` database reads. Spare memory keeps a burst from evicting the hot set.
- **Multi-layer caching** — request map, process, shared tier, database. An assembled page is its own key. Editing a source row does not rebuild that key.

## Example

A library catalog. In this minute the cache recorded 900 hits and 100 misses, hits at 1 ms and misses at 15 ms, both measured at the caller. Those counts are a measurement for this minute, not a property of adding a cache. The write deletes the document key after the price row commits. The TTL on a fill is 60 seconds plus up to 10 seconds of jitter.

```python
def average_ms(hits: int, misses: int, hit_ms: float, miss_ms: float) -> float:
    total = hits + misses
    return (hits * hit_ms + misses * miss_ms) / total


def write_then_delete(db: dict[str, str], cache: dict[str, str], key: str, value: str) -> None:
    db[key] = value
    cache.pop(key, None)


def jittered_ttl(base_s: int, spread_s: int, roll: int) -> int:
    return base_s + (roll % (spread_s + 1))


db = {"book:7": "old price"}
cache = {"book:7": "old document"}
write_then_delete(db, cache, "book:7", "new price")
hits, misses = 900, 100
print(cache.get("book:7"), average_ms(hits, misses, 1, 15), misses, jittered_ttl(60, 10, 7))
# None 2.4 100 67
```

`None` means the next read misses and rebuilds the document from the committed price. A reader that already loaded the old document can still store it after this delete. The TTL on that store is the bound, unless the cache cancelled the reader's compare-and-swap token. `2.4` ms is the mean for this measured split, and the 100 misses are the database reads only if each miss performed one read. `67` is one jittered TTL, so a wave of fills does not expire on the same second.

## See also

- [Content Distribution and Media](../22_Content_Distribution_and_Media/) — shared public delivery. Those cards stay in that topic.
- [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/) — the ring and virtual nodes, when a cache node joins or leaves.
- [Consistency and Replication](../09_Consistency_and_Replication/) — a replica read, a lagging fill, and how stale a caller can accept.
- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — the point in the growth path where a cache appears. The patterns stay here.
