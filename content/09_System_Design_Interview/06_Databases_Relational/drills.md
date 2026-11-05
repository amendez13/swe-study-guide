# Databases — Relational — Drills

Original practice for a relational primary, its replicas, and a shard key. Each card is one exercise: commit to an answer, then check it. The numbers are invented for a neighborhood tool library, where members reserve tools. Quorums and the hash ring stay in their own topics.

## Replica Count

The library serves 10,000 reads per second and 400 writes per second. Each replica can serve 4,000 reads per second. You have measured the primary at 1,500 writes per second. Reads go to replicas. Do three replicas cover the reads? Do two? Do the writes fit the measured primary?

```python
READS = 10_000
WRITES = 400
EACH = 4_000
PRIMARY_WRITE_CAP = 1_500
```

**Answer:** Three replicas cover 12,000 reads per second, which clears 10,000. Two cover 8,000, which does not. The 400 writes fit the 1,500 you measured on the primary. Another replica does not raise that write ceiling. Shipping the log to more replicas is extra disk and network on the primary. Measure that. Do not subtract a guessed amount from 1,500.

```python
READS = 10_000
WRITES = 400
EACH = 4_000
PRIMARY_WRITE_CAP = 1_500

three = 3 * EACH
two = 2 * EACH
print(three, two, three >= READS, two >= READS, WRITES <= PRIMARY_WRITE_CAP)
# 12000 8000 True False True
```

## Read After Write

A member commits a new phone number at log position 50. The primary is at 50. Replica A has applied through 42, replica B through 55, and replica C through 47. What does a read of A return relative to the commit? What does the primary return? What does B return? If the next read goes to C, which requirement breaks?

```python
COMMIT = 50
PRIMARY = 50
REPLICA_A = 42
REPLICA_B = 55
REPLICA_C = 47
```

**Answer:** A is behind the commit, so the member sees the old number. The primary has the new number. B has it too. C is behind B, so the following read moves backward even though B already showed the new number. Seeing your own write and never moving backward are different. Stay on one replica only after it has reached 50, or send that member to the primary. The primary read spends primary capacity. The pin waits out lag and fails if a later request switches replica.

```python
COMMIT = 50
PRIMARY = 50
REPLICA_A = 42
REPLICA_B = 55
REPLICA_C = 47


def caught_up(position: int) -> bool:
    return position >= COMMIT


print(caught_up(REPLICA_A), caught_up(PRIMARY), caught_up(REPLICA_B), REPLICA_C < REPLICA_B)
# False True True True
```

## Primary Loss

The primary acknowledged through log position 80. Replication was asynchronous. Replica A has applied through 74. Replica B has applied through 71. Which acknowledged positions are missing if you promote A? Which are missing if A had flushed before each of those acknowledgements and you still promote A? Which are missing if you waited for A but promote B?

```python
ACKED = 80
APPLIED = {"A": 74, "B": 71}
```

**Answer:** Promoting A drops acknowledged positions 75 through 80. The client was told those commits succeeded. If A flushed each commit before the acknowledgement, and you promote A, none of them are missing. Waiting on A and then promoting B drops 72 through 80. Receipt in memory is not the flush this count uses. Fence the old primary before either promotion. An unfenced primary can accept a new commit the new primary does not have. When the old node returns, discard the commits that are only on it. Replaying them onto A forks the log.

```python
ACKED = 80
APPLIED = {"A": 74, "B": 71}


def missing(promote: str, flushed_before_ack: str | None) -> list[int]:
    have = APPLIED[promote]
    if flushed_before_ack == promote:
        have = ACKED
    return list(range(have + 1, ACKED + 1))


print(missing("A", None), missing("A", "A"), missing("B", "A"))
# [75, 76, 77, 78, 79, 80] [] [72, 73, 74, 75, 76, 77, 78, 79, 80]
```

## Vertical or Shard

The primary has 64 GB of RAM. The hot indexes and rows measure 100 GB, and the slow queries are waiting on disk reads. The table is 400 GB. The plan for next year is a 160 GB working set and 700 GB on disk. The largest machine you can take has 256 GB of RAM and 8 TB of disk. Writes are 800 per second today and the plan is 1,400 per second, spread across members. The primary is not waiting on one row lock or on the log flush. Same-size replicas are available. Do you resize, add replicas, or shard?

**Answer:** Resize. The measured problem is a working set that does not fit in 64 GB, and 256 GB covers the planned 160 GB. The disk fits. A 64 GB replica misses the same working set and takes no writes. Sharding would split a member's reservations from the member row while one primary can still hold both. The larger core count is not a measured write capacity. Confirm 1,400 writes per second on that machine. A hot row or a saturated log flush would remain the ceiling after the resize, which is not this workload.

## Shard Key Pick

Eight reservations, four members, and two days. The online query is "reservations for this member." A nightly job wants today's rows. `member_id` puts each member on one shard. `created_at` puts every "today" row on one shard and every "yesterday" row on another. How many shards does m1's page touch under each key? How many of the eight rows are today's?

```python
ROWS = [
    ("m1", "today"),
    ("m2", "today"),
    ("m3", "today"),
    ("m4", "today"),
    ("m1", "yesterday"),
    ("m2", "yesterday"),
    ("m3", "yesterday"),
    ("m4", "yesterday"),
]
DAY_SHARD = {"today": 0, "yesterday": 1}
```

**Answer:** m1's page touches 1 shard if the key is `member_id` and 2 shards if the key is `created_at`. Four of the eight rows are today, so the today shard already holds half of this sample. On a launch day that shard also takes almost all live writes. Use `member_id` for the member page. Scatter the nightly job, or keep a side report. A member who is most of the traffic is still a hot shard under `member_id`. That is the next card.

```python
ROWS = [
    ("m1", "today"),
    ("m2", "today"),
    ("m3", "today"),
    ("m4", "today"),
    ("m1", "yesterday"),
    ("m2", "yesterday"),
    ("m3", "yesterday"),
    ("m4", "yesterday"),
]
DAY_SHARD = {"today": 0, "yesterday": 1}


def member_shards(member: str, key: str) -> int:
    if key == "member_id":
        return 1
    return len({DAY_SHARD[day] for who, day in ROWS if who == member})


def today_rows() -> int:
    return sum(1 for _, day in ROWS if day == "today")


print(member_shards("m1", "member_id"), member_shards("m1", "created_at"), today_rows(), len(ROWS))
# 1 2 4 8
```

## Hot Shard

Four shards. `hash(member_id) % 4` spreads row counts evenly. Of 10,000 writes per second, member m9 is 70 percent. The other 30 percent spreads evenly across all four shards, including m9's. What write rate does m9's shard take? What does each other shard take?

```python
WRITES = 10_000
HOT_PERCENT = 70
N = 4
```

**Answer:** m9's shard takes 7,750 writes per second: all 7,000 of m9, plus 750 of the rest. Each other shard takes 750. Equal row counts hide this. A replica of m9's shard adds reads and does not take those writes. Splitting m9 across shards helps only when the member page can merge the pieces. One counter row for m9 does not split that way.

```python
WRITES = 10_000
HOT_PERCENT = 70
N = 4

hot = WRITES * HOT_PERCENT // 100
rest = WRITES - hot
owner = hot + rest // N
other = rest // N
print(owner, other)
# 7750 750
```

## Resharding Cost

Reservation ids are `0` through `999`. The shard is `id % N`, and N goes from 4 to 5. How many ids change shard? Separately, 20 fixed buckets are `id % 20`, with several buckets on each node. How many ids move if you move one bucket, the ids where `id % 20 == 0`?

```python
KEYS = range(1000)
```

**Answer:** Modulo hashing moves 800 of the 1,000 ids. One fixed bucket moves 50. Both numbers are copies plus a cutover while writes continue. During the copy, a read has to know which side owns the id, and a write to both sides forks it. Consistent hashing's fraction of keys, and the client lookup, stay in Data Partitioning and Consistent Hashing.

```python
KEYS = range(1000)

modulo = sum((key % 4) != (key % 5) for key in KEYS)
one_bucket = sum((key % 20) == 0 for key in KEYS)
print(modulo, one_bucket)
# 800 50
```

## Index Choice

The only index is `(member_id, created_at)`. Which of these use it as the access path, and where does a second index earn its write cost?

```sql
SELECT * FROM reservations
WHERE member_id = 42
ORDER BY created_at DESC
LIMIT 20;

SELECT * FROM reservations
WHERE created_at > DATE '2024-06-01';

SELECT * FROM reservations
WHERE member_id = 42 AND tool_id = 7;

SELECT * FROM reservations
WHERE member_id > 40 AND created_at = DATE '2024-06-01';
```

**Answer:** The member page uses this index: equality on `member_id`, then `created_at` order. The date-only filter does not. `created_at` is not the leading column, and a skip scan is not a plan to promise. An index on `created_at` serves that report and slows every insert. The `tool_id` query can walk `member_id` and then filter `tool_id`. `(member_id, tool_id)` is the better index when `tool_id` is what selects inside the member. Keep both only if both queries are hot. The last query can walk the `member_id` range and then filter the date. Dates are ordered only inside one member, so `created_at =` that day is not a contiguous step after a range on `member_id`. `SELECT *` still fetches the row. None of these are covering indexes.
