# Caching — Drills

Original practice for an application cache in front of a database. Each card is one exercise: commit to an answer, then check it. The numbers are invented for a neighborhood library catalog. Shared public delivery stays in Content Distribution and Media.

## Hit Ratio Latency

In one second the catalog cache saw 400 hits and 100 misses. A hit returns in 1 ms. A miss returns in 21 ms. Both times are measured at the caller. Each miss performed one database read, and there were no timeouts. What is the hit ratio, the mean latency in milliseconds, and the database reads in that second?

```python
HITS = 400
MISSES = 100
HIT_MS = 1
MISS_MS = 21
```

**Answer:** The hit ratio is 0.8. The mean is 5 ms. The database sees 100 reads per second. The mean uses both clocks at the caller, so the miss time already includes the lookup that failed. One hundred database reads depends on one read per miss. A stampede, a retry, or a timeout that fails the request changes that count. 0.8 describes this second. It does not travel with the cache to next week's traffic.

```python
HITS = 400
MISSES = 100
HIT_MS = 1
MISS_MS = 21

total = HITS + MISSES
hit_ratio = HITS / total
mean_ms = (HITS * HIT_MS + MISSES * MISS_MS) / total
print(f"{hit_ratio:.1f} {mean_ms:.0f} {MISSES}")
# 0.8 5 100
```

## Required Hit Ratio

The catalog serves 2,000 cache-eligible reads per second. The database budget for this path is 100 reads per second. Assume a warm cache, one database read per miss, and no stampede. What hit ratio stays inside the budget? If the single cache node dies and every read falls through, how many times the budget is the database load?

```python
READS = 2000
BUDGET = 100
```

**Answer:** The hit ratio has to be at least 0.95. A dead cache with fall-through sends 2,000 reads per second, which is 20 times the budget. 0.95 is the algebra for this budget, not a hit ratio you can expect from turning a cache on. Failing the request instead of falling through keeps the database at 100 and shows the reader an error. A stampede at a lower hit ratio can pass 100 database reads even while the cache process is up.

```python
READS = 2000
BUDGET = 100

hit_ratio = (READS - BUDGET) / READS
multiplier = READS // BUDGET
print(f"{hit_ratio:.2f} {multiplier}")
# 0.95 20
```

## Stale Read Race

`book:7` is price `v1` in the database. A reader has loaded `v1` and has not stored it. The writer commits `v2` and deletes the cache key. The reader then stores `v1`. What do the cache and the database hold? A second reader took a compare-and-swap token before that delete, and the delete cancelled the token. What does that reader leave in the cache? Separately, the writer deletes first, a reader stores `v1` from the database, and only then does the writer commit `v2`. Why is that order worse?

**Answer:** After the late store the cache holds `v1` and the database holds `v2`. The next read is stale until that entry expires. The cancelled token stores nothing, so the next read misses and loads `v2`. Deleting before the commit is worse because the writer's only delete has already happened. The refill of `v1` sits for the whole TTL, and no second delete is coming. "Store only if absent" does not save either case: after a bare delete the key is absent, so the stale store is accepted. A tombstone that still records `v2` can reject it. The tombstone has to remain in the cache for the comparison to exist.

```python
def late_set_after_delete() -> tuple[str, str]:
    cache: dict[str, str] = {}
    db = {"book:7": "v1"}
    loaded = db["book:7"]
    db["book:7"] = "v2"
    cache.pop("book:7", None)
    cache["book:7"] = loaded
    return cache["book:7"], db["book:7"]


def lease_rejects_late_set() -> tuple[str | None, str]:
    cache: dict[str, str] = {}
    db = {"book:7": "v1"}
    loaded = db["book:7"]
    db["book:7"] = "v2"
    token_live = False  # the delete cancelled the in-flight token
    if token_live:
        cache["book:7"] = loaded
    return cache.get("book:7"), db["book:7"]


def delete_before_commit() -> str:
    cache: dict[str, str] = {}
    db = {"book:7": "v1"}
    cache.pop("book:7", None)
    cache["book:7"] = db["book:7"]
    db["book:7"] = "v2"
    if cache["book:7"] != db["book:7"]:
        return "no-second-delete"
    return "caught"


print(late_set_after_delete(), lease_rejects_late_set(), delete_before_commit())
# ('v1', 'v2') (None, 'v2') no-second-delete
```

## LRU Trace

The cache holds three keys and uses exact LRU. The access sequence is A, B, C, A, D. Each new key inserts. A repeated key is an access, not a second insert. Which key is evicted when D arrives, and what is left from oldest to newest? Would FIFO have evicted the same key? If A's TTL had already elapsed, which mechanism removes A?

```python
OPS = ["A", "B", "C", "A", "D"]
CAPACITY = 3
```

**Answer:** D evicts B. B is the least recently used. The cache is C, A, D from oldest to newest. FIFO would evict A, the oldest insertion, even though A was just used. An elapsed TTL removes A by expiry, including when A is the newest key. This trace did not expire anyone. Expiry and eviction answer different questions: expiry asks whether the value may be served, and eviction asks which slot to reuse when memory is full.

```python
from collections import OrderedDict

OPS = ["A", "B", "C", "A", "D"]
CAPACITY = 3


def trace(ops: list[str], capacity: int) -> tuple[str | None, list[str]]:
    cache: OrderedDict[str, None] = OrderedDict()
    evicted = None
    for key in ops:
        if key in cache:
            cache.move_to_end(key)
            continue
        cache[key] = None
        if len(cache) > capacity:
            evicted, _ = cache.popitem(last=False)
    return evicted, list(cache)


print(trace(OPS, CAPACITY))
# ('B', ['C', 'A', 'D'])
```

## Pick the Write Pattern

Three writes on the catalog. Name the pattern for each one.

The price writer updates a price column. The cache holds `{title, price, cover}` under `book:7`. The writer does not build that document. Readers may see the old document until the TTL. A crash must not lose the new price.

The seat writer updates a row that is stored in the cache in the same shape. When the write returns, a cache read must already show the new seat count, with no miss. A crash must not lose the write. Extra latency on the write is acceptable.

The entrance counter takes 20,000 samples a second into memory and flushes batches. The door display can lag about a second. Losing the unflushed second when the cache process dies is acceptable. The database cannot take one insert per sample.

**Answer:** The price document is cache-aside. Commit the price, then delete `book:7`. The next miss rebuilds the document from the committed row. Write-through would require the writer to build a document it does not have. Write-behind can lose the price on a crash.

The seat row is write-through. The acknowledgement waits for the database commit, and the cache entry is already the new row, so the next cache read hits. Cache-aside would delete the key and the next read would miss, which breaks the requirement. Write-behind can lose the seat count.

The entrance counter is write-behind. The acknowledgement is the memory update, and the database sees a batch. The unflushed second is the accepted loss. Cache-aside and write-through both send the database one write per sample. A dirty counter has to be flushed before it is evicted, and a miss must not replace it with an older database total.

## Stampede Fix

`book:7` was just deleted. Thirty requests miss it in the same instant. How many database reads happen with no protection, and how many with a single loader for that key?

```python
WAITERS = 30
```

**Answer:** No protection performs 30 database reads. A single loader performs 1. The other 29 wait for that result and then read the filled key. The loader and the waiters need a timeout. A loader that never returns protects the database and exhausts the application. If a slightly older document is acceptable, keep serving it and let one request refresh: the database still sees one read, and the 29 do not block. Jitter would have spread an expiry. It does nothing for a key you just deleted. Thirty lookups of a book id that is not in the database are the same herd unless a short negative entry remembers the absence. Create has to delete that entry. Single-flight does not move a key that stays hot after the fill. That is a hot-key problem.

```python
WAITERS = 30


def database_reads(waiters: int, single_flight: bool) -> int:
    if waiters == 0:
        return 0
    if single_flight:
        return 1
    return waiters


print(database_reads(WAITERS, False), database_reads(WAITERS, True))
# 30 1
```

## Cache Node Loss

Four cache nodes, keys spread evenly, no replica. The catalog sends 2,000 cache-eligible reads per second. A warm node hits 9/10 of its reads. Each miss is one database read. Callers fall through. The database was sized for the steady miss load. One node dies and its keys are cold. What is the steady database read rate, and what is it after the death? What changes if a warm replica takes those keys?

```python
R = 2000
N = 4
# Warm hit ratio is 9/10. Miss ratio is 1/10.
```

**Answer:** Steady database load is 200 reads per second. After the death it is 650. The dead node's 500 reads all miss, and the other 1,500 still miss 1/10, which is 150. The extra 450 is the hits that node used to absorb (`h * R / N` with h = 9/10). A budget of 200 falls over. A warm replica keeps the steady 200, apart from the failover itself. Spare memory on the surviving nodes holds none of the dead node's keys. An empty replacement that passes a port check is the same 650 until it is warm. Single-flight makes waiters for one key share one database read. During the fill, a second full of never-before-seen keys still costs one read each, up to the 500 requests on that node.

```python
R = 2000
N = 4

steady = R // 10
cold = R // N
database_reads = (R - cold) // 10 + cold
print(steady, database_reads)
# 200 650
```

## Hot Key Split

`book:7` is one JSON document and takes 800 of 1,000 catalog reads per second. The other 200 are spread evenly across four cache nodes. The document sits on one node. What load does that node take? If the whole document is copied to all four nodes and each read picks a node evenly, what load does each node take?

```python
HOT = 800
COLD = 200
N = 4
```

**Answer:** The owner takes 850 reads per second: all 800 of the hot key, plus 50 of the cold keys. The other nodes take 50. After the document is copied and each read picks a node evenly, every node takes 250. That 250 is the expected load, not a promise about one particular second. Slicing the JSON into four fragments goes the wrong way when the reader needs the whole document: each read then touches every node. A counter can be split, because the reader sums the shards. A short copy in each application process is the other lever. The shared node then sees about one read per process per TTL window, and each process copy expires on its own after a delete. The 850 are hits on one node. Collapsing a burst of misses leaves that hit load where it is.

```python
HOT = 800
COLD = 200
N = 4


def node_qps(replicated: bool) -> int:
    hot_share = HOT // N if replicated else HOT
    return hot_share + COLD // N


print(node_qps(False), node_qps(True))
# 850 250
```
