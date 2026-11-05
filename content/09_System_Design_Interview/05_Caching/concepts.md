## When Caching Helps

A cache stores a copy of a database row, or of a result you would otherwise recompute, where the next read can finish without that work. The copy is volatile. Eviction, expiry, and a process restart drop it. The database remains the source of truth. Write-behind is the exception: an acknowledged write lives only in the cache until the flush.

A cache earns its place when the same keys are read again, the read is expensive next to a cache hop, and the caller can live with a bounded stale window. A handful of keys that are read far more often than the rest can sit in a cache smaller than the full data set. Reads spread evenly across a set that does not fit will mostly miss. Skip the cache when each key is read once, or when a stale permission or a stale balance is worse than a slow correct read. The hit ratio is a measurement for this workload. Hit Ratio Math turns that measurement into latency and database load.

## Cache Tier Placement

The read and write pattern is a separate choice from where the bytes sit.

```text
In-process:
  The value lives in the application process.
  No network hop.
  Each instance fills and expires its own copy.
  The copy dies with the process and spends that process's memory.

Shared remote tier:
  A separate fleet, such as Redis or Memcached.
  Every instance reads the same entry.
  Memory and get/set rate grow by adding cache nodes.
  Adds a network hop and a failure domain the application does not already have.
```

Use the process for a tiny set that one instance rereads constantly, with a short TTL. Use the shared tier when many instances should share one fill. More application instances multiply in-process copies. They do not grow a shared tier. The shared tier grows when the key set or the cache request rate grows, without growing the application fleet by the same amount. A request that walks more than one of these is Multi-Layer Caching.

## Hit Ratio Math

The hit ratio is `hits / (hits + misses)` over requests that were allowed to use the cache. It is an output of the working set, the capacity, the TTL, the invalidation rate, and the skew. It is the input to the latency and load arithmetic.

```python
def mean_ms(hits: int, misses: int, hit_ms: float, miss_ms: float) -> float:
    """Both times are measured at the caller, so a miss includes the failed lookup."""
    total = hits + misses
    return (hits * hit_ms + misses * miss_ms) / total
```

```text
database reads ≈ misses
required hit ratio ≈ 1 - (database budget / eligible reads)
```

Those two lines hold when each miss performs one database read. A stampede, a retry, or a fan-out from one key to many rows produces more database reads than there were misses. A negative cache produces fewer once the marker is stored: later lookups of that missing key hit the cache. Timeouts and errors are a third outcome. A fail-closed timeout performs no database read, so it stays out of the miss total. Count each retry that reaches the database. A miss total that leaves those retries out is short of the load. The ratio is an average across keys. One key can always miss inside a high average. The caller who misses waits the full miss time, and the mean hides that wait. An empty cache and a dead cache are a different measurement. Cache Failure and Overprovisioning is that case.

## Cache-Aside (Lazy Loading)

The application calls the cache and the database itself. A read looks up the key. A hit returns the stored value. A miss reads the database, stores the value with a TTL, and returns it. A write commits the database, then deletes the key. The next read misses and builds the cached value from the committed row.

```text
Read:  lookup → hit returns → miss reads the database, SET with a TTL, return
Write: commit the database → delete the key
```

The writer deletes, because the cached value is often a document the writer does not assemble, such as title, price, and cover under one key. Two writers that SET that document can also land out of commit order. A delete leaves the next miss to rebuild the document from the committed row. A reader that already loaded the old row can still SET it afterward. Cache Invalidation is that race. The TTL is set on the fill, so a delete that never arrives still expires. The first read after a miss or a delete is the slow one. Only keys that are actually read occupy a slot. A read can fall through to the database while the write still commits. Failing that read closed is the choice when the fall-through would overload the database.

## Read-Through and Write-Through

The application talks to the cache. On a miss, the cache loads the database, stores the value with a TTL, and returns it. On a write, the cache writes the database and acknowledges only after that commit. When the acknowledgement returns, the entry this cache wrote and the database row match.

The write waits for both hops. The cache stores the value even if nobody reads it again. If the database write fails, the cache drops the new value. If the cache is down, the write fails with it, unless the application bypasses to the database and fills later, which is cache-aside on that path. A process cache in front, a lagging replica, or a different key that embeds the row can still be stale after the acknowledgement. The first miss still pays the database. Concurrent misses meet inside the loader, so stampede protection has to live there. The application no longer sees those misses one by one.

## Write-Behind (Write-Back)

The application writes the cache and receives the acknowledgement. The cache flushes to the database later, often as a batch. Write latency is the cache hop. The database sees fewer writes.

Until the flush, the cache holds the only copy of an acknowledged write. Evicting that key without flushing drops the write. A crash drops every dirty key that is neither in the database nor on a replica the acknowledgement waited for. A miss that loads the database can store a row older than the dirty buffer and hide the newer write. The miss path has to see the dirty entry, and a dirty key stays in the cache until it is flushed.

```text
Acknowledge after the cache write.
Flush before eviction.
A miss must not cover a dirty key with the older database row.
```

This fits samples, counters, and other streams that can lose a short unflushed window. A price, a balance, or a seat count that must survive a crash stays on cache-aside or write-through.

## Eviction Policies

Eviction frees a slot when the cache is at its memory ceiling. It can drop a value that is still inside its TTL. Expiry is the other mechanism: the TTL has elapsed, so the value must not be served even when memory is free. A TTL bounds how long a stored value may be served. An eviction policy chooses the slot. Most caches run both.

```text
LRU:   evict the key whose last access is oldest.
       Exact LRU is a hash map plus a doubly linked list.
       Get and put move that node to the head in O(1). The tail leaves.
       A long scan of one-time keys walks the hot set out of an exact LRU.
       A common approximation samples a few keys and evicts the oldest in the sample.

LFU:   evict the key with the lowest access count.
       Protects a key that stays popular. A raw count also sticks
       to yesterday's spike. A decaying count lets that key go.

FIFO:  evict the oldest insertion. A later access does not save it.

Random: evict a key at random. Cheap, and it will evict a hot key
        with the same chance as a cold one.
```

Name LRU when you need the hot set to survive a scan of cold keys, and name the TTL separately as the freshness bound. Say LFU when popularity is stable across a long window. Say random when implementation cost matters more than protecting a specific hot key.

## TTL Tuning

The TTL is how long a fill may be served. It is set when the value is stored. Too short, and a key that is still hot expires, the hit ratio falls, and database reads climb. Too long, and a missed invalidation stays visible for the whole TTL, and the slot holds a value past the point anyone should see it. Expiry ends the right to serve the value. Servers often reclaim the bytes lazily, on the next access or on a scan. Capacity is Eviction Policies.

Keys filled in the same second expire in the same second if they share a fixed TTL. That is a stampede. Add a spread so they do not:

```python
def ttl_s(base_s: int, spread_s: int, roll: int) -> int:
    """roll is a random integer drawn per fill. Spread is inclusive."""
    return base_s + (roll % (spread_s + 1))
```

Pick the base from the data. A catalog document can live for seconds. A negative marker for a missing key lives for a shorter base, because it hides a row that was just created. Jitter spreads expiries that would have lined up. A key you just deleted, and a cold node, still need Cache Stampede Protection.

## Cache Invalidation

Invalidation is how a write gets a stale copy out of the way. On the cache-aside path the writer commits the database, then deletes the key. The delete is idempotent, and the next miss rebuilds the document from the committed row. A lost delete is why the fill still carries a TTL.

```text
Commit, then delete. A reader can still put the old value back:

  Reader loads v1 from the database and has not stored it yet.
  Writer commits v2 and deletes the key.
  Reader SETs v1.
  The next read is v1 until that entry expires.

Delete, then commit. Worse, because the writer is already done:

  Writer deletes the key.
  Reader loads v1 (the commit has not happened) and SETs it.
  Writer commits v2 and does not delete again.
  v1 stays for the TTL on that SET (or until eviction, if the SET carried no TTL).
  Nothing else is scheduled to remove it.

A bare delete leaves the key absent, so a later SET of v1 succeeds.
"Store only if the key is missing" still accepts that SET.
A compare-and-swap token, on a cache that issues one at the start of
the read, is cancelled by the delete, and the late SET is rejected.
A tombstone that records v2 rejects an older SET. The tombstone has
to remain. After a bare delete there is no version left to compare.
```

The same late SET applies to a negative entry. Store "this key is absent" with a short TTL so a flood of lookups for a missing row hits the marker. Delete the marker when the row is created. A long negative TTL hides the new row, and a reader that already observed the absence can write the marker again after the create.

A new key name such as `book:7:v3` leaves the old entry to expire, and every reader has to learn `v3`. The pointer that says `v3` is itself a cache entry with the same race. An event that says "delete `book:7`" is the same delete, sent to every cache that might hold the key, including a process cache. A lost event is the case the TTL covers. Filling from a replica that has not applied the commit stores the lagging row. The fill source is the primary, or the staleness bound includes replication lag. That lag is [Consistency and Replication](../09_Consistency_and_Replication/).

## Cache Stampede Protection

A stampede is many misses of one key at the same moment. The TTL values line up, a deploy starts from an empty cache, or a popular key was just deleted. Each miss loads the database on its own, so the query count equals the miss count.

One loader per key makes that one query. The other waiters share the result. Give the loader a timeout and the waiters a limit. Without those, the database stays safe and the application piles up on a loader that never returns. When a slightly older value is acceptable, keep serving it and let one request refresh. The waiters do not block, and the database still sees one read.

Jitter is what keeps expiries from lining up. A deleted key and a cold node still need one loader. A missing key is the same herd: a short negative entry, from Cache Invalidation, absorbs the lookups after the first. A key that stays hot after the fill still sits on one node. Hot Key Mitigation is that case.

## Hot Key Mitigation

Partitioning puts one key on one node. If that key is a large share of the request rate, that node saturates and the rest of the cluster is idle. The database can be healthy while that cache node is the bottleneck. A replica of the cluster spreads the key only when a read may use a copy besides the primary.

```text
Read-mostly document (one JSON value):
  Copy the whole value to several nodes.
  The client reads one copy, chosen at random.
  A write updates every copy, or a copy stays stale until its TTL.
  Slicing the JSON sends a reader that needs the whole document to every slice.

Mergeable value (a counter):
  Split into N shards. Increment one shard. Sum them on read.

Very hot and local:
  A short-lived copy in the process, in front of the shared key.
  The shared node sees about one read per instance per TTL window.
  Jitter those process TTLs so the instances do not miss the shared key together.
  Each process copy expires on its own after a delete of the shared key.
```

A stampede is a burst of misses. A hot key is a sustained rate of hits. Collapsing the misses does not move the hits off the node that owns the key.

## Distributed Cache Architecture

One cache process is a shared tier with a ceiling: the memory and the request rate of that machine. When it stops, every key misses. Past that ceiling, or when that failure is too large, partition the keys so memory and request rate spread.

```text
Modulo hashing: key % N. Adding a node moves almost every key.
Consistent hashing: adding a node moves about 1/N of the keys.
One key has one primary node, unless Hot Key Mitigation copied it.
```

Virtual nodes keep that moved slice even across machines of different sizes. The ring itself is [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/). The client has to know membership, or a proxy has to know it. A proxy adds a hop. A replica keeps the primary's keys after a crash. Reading the replica can return a stale value, which is a consistency choice on [Consistency and Replication](../09_Consistency_and_Replication/). Memcached clients usually hash to a node and keep no replica. Redis Cluster assigns slots and can keep a replica per slot. Either way, say whether a node death loses keys or fails them over.

## Cache Failure and Overprovisioning

A warm hit ratio is the load while the cache is up and full of useful keys. The database has to survive the moment that stops being true.

```text
R = cache-eligible reads per second
h = hit ratio while warm
One node holds the keys, and callers fall through to one database read:
  steady database reads ≈ R * (1 - h)
  cache down ≈ R
  multiplier ≈ 1 / (1 - h)

One of N nodes is cold, keys spread evenly, no replica:
  database reads ≈ R * (1 - h) + h * R / N
```

Callers that fail the request keep the database at the steady rate and return an error. Callers that fall through multiply the database load. A single process is the full multiplier. One cold node in a cluster, with no replica, adds about `h * R / N` database reads: the hits that node used to serve. A warm replica takes those keys over and the steady rate stands, apart from the failover blip. An empty process that passes a port check is still cold. Its hit ratio is 0 until something fills it. Warm it from the replica before it takes traffic, or single-flight the misses so each distinct key costs one database read while the waiters share it.

Memory has its own headroom. At the eviction ceiling, a burst of new keys evicts the hot set and the hit ratio falls while every node is healthy. Spare memory absorbs that burst, plus allocator waste and a replication buffer. The working set plus the burst has to fit. Otherwise eviction holds the hit ratio to whatever slice of that set still fits. There is no universal spare fraction to quote in place of that fit.

## Multi-Layer Caching

A request can meet more than one cache, and each layer has its own size, TTL, and invalidation path.

```text
Request map → process cache → shared cache → database
```

The request map dies with the response. The process cache holds a few hot keys for that instance. The shared tier holds the working set for the fleet. The database holds the durable row. A closer layer is smaller. A delete that reaches only the shared tier leaves the process copy in place until that copy's TTL.

Some values are assembled from many rows: a catalog card, a ranking, a page. Store the assembled value under its own key. Updating one of the source rows leaves the assembled key in place until that key is deleted or it expires. Rebuilding a hot assembled key on every miss is a stampede, so one refresh at a time, and a short process TTL in front of the shared copy when that one key would saturate a node. The assembled key is still a volatile copy. The database remains the source of truth for the page. Different data gets different layers. A session blob can live only in the shared tier for the life of the session. A ranking can be rebuilt on a schedule and cached as the result. A price document is filled on demand and deleted when the price row commits.
