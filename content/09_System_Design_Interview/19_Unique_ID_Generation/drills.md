# Unique ID Generation — Drills

Original practice for which constraint removes an id scheme, how a packed id behaves, and how a short code spends its alphabet. Each card is one exercise: commit to an answer, then check it. The numbers are invented for Rowan Glassworks, a hot shop with three furnaces, holly, yew, and ash. Each furnace logs a pour. A clerk's tablet may send the same pour twice. A finished bowl gets a short code on the street window. Why a wall clock steps stays in Distributed System Failure Modes. What a repeated call means stays in Networking and Communication. Which primary accepts a write stays in Consistency and Replication. Schema bytes stay in Encoding Serialization and Schema Evolution. A provisioned furnace number is not a leader election, which stays in Transactions and Concurrency Control. The redirect and the cache of a short link stay in Classic Design Problems.

## ID Fit

The pour log needs every constraint in `ORDER`, checked from the top. Which constraint is the first one `uuid-v4` misses, the first one `ulid` misses, and the first one `ticket` misses? Which option misses none?

```python
ORDER = ("time-sortable", "bits-64", "no-round-trip", "unique")
OPTIONS = {
    "uuid-v4": ("unique", "no-round-trip"),
    "ulid": ("unique", "time-sortable", "no-round-trip"),
    "ticket": ("unique", "time-sortable", "bits-64"),
    "snowflake": ("unique", "time-sortable", "bits-64", "no-round-trip"),
}
```

**Answer:** `uuid-v4` misses time-sortable first. It is also wider than 64 bits, and the pour log fails it on the order before it fails it on the width. `ulid` has the timestamp and needs no round trip, and it misses bits-64. `ticket` is unique, time-sortable, and 64 bits, and it misses no-round-trip because the furnace asks a desk. `snowflake` meets all four. A tablet that must mint with no furnace number is a different bar, and that bar is where the UUID fits.

```python
ORDER = ("time-sortable", "bits-64", "no-round-trip", "unique")
OPTIONS = {
    "uuid-v4": ("unique", "no-round-trip"),
    "ulid": ("unique", "time-sortable", "no-round-trip"),
    "ticket": ("unique", "time-sortable", "bits-64"),
    "snowflake": ("unique", "time-sortable", "bits-64", "no-round-trip"),
}


def ruling(have: tuple[str, ...]) -> str:
    owned = set(have)
    for constraint in ORDER:
        if constraint not in owned:
            return constraint
    return "none"


print(*(ruling(OPTIONS[name]) for name in ("uuid-v4", "ulid", "ticket", "snowflake")))
# time-sortable bits-64 no-round-trip none
```

## UUID Locality

Four pours were made in the order p1, p2, p3, p4. Each carries a version-4 id, shown here as a small integer. Sort those rows by the id. If a leaf page is `id mod 4`, which page does each insert hit, in pour order? How many bytes is the key beside an 8-byte Snowflake id?

```python
POURS = (("p1", 50), ("p2", 12), ("p3", 90), ("p4", 7))
UUID_BYTES = 16
SNOW_BYTES = 8
```

**Answer:** The id order is p4, p2, p1, p3. Pour order and id order are different sequences, so the clustered index is not a pour log. The inserts hit pages 2, 0, 2, 3. They do not stay on the right edge of the B-tree. The key is 16 bytes next to 8. Uniqueness still holds: 122 random bits, and these four values do not meet. The tablet's retry name can be a UUID. The meaning of the retry stays on Idempotency.

```python
POURS = (("p1", 50), ("p2", 12), ("p3", 90), ("p4", 7))
UUID_BYTES = 16
SNOW_BYTES = 8


def by_id(rows: tuple[tuple[str, int], ...]) -> tuple[str, ...]:
    return tuple(name for name, _key in sorted(rows, key=lambda row: row[1]))


def pages(rows: tuple[tuple[str, int], ...]) -> tuple[int, ...]:
    return tuple(key % 4 for _name, key in rows)


print(by_id(POURS), pages(POURS), UUID_BYTES, SNOW_BYTES)
# ('p4', 'p2', 'p1', 'p3') (2, 0, 2, 3) 16 8
```

## Snowflake Capacity

Holly's id uses 41 timestamp bits, 10 worker bits, and 12 sequence bits. How many ids can holly mint in one millisecond, and how many is that in one second? The 4,097th mint of that millisecond has no unused sequence value. What does holly do with it?

```python
TIMESTAMP_BITS = 41
WORKER_BITS = 10
SEQUENCE_BITS = 12
```

**Answer:** The sequence width alone sets the millisecond count: 2^12 is 4,096 ids in that millisecond, and a thousand of those milliseconds make 4,096,000 ids in one second. The 41-bit field is the span of the clock, about 69 years, and the 10 worker bits name 1,024 furnaces. Neither number raises the count inside one millisecond. Values in the sequence run from 0 through 4,095. The 4,097th mint waits for the next millisecond and then uses sequence 0. Using 0 again inside the same millisecond repeats an id holly already returned. The shop and furnace numbers in those 10 bits are written down at provision time. That write is not Leader Election.

```python
TIMESTAMP_BITS = 41
WORKER_BITS = 10
SEQUENCE_BITS = 12


def per_millisecond(sequence_bits: int) -> int:
    return 1 << sequence_bits


one_ms = per_millisecond(SEQUENCE_BITS)
print(one_ms, one_ms * 1000, TIMESTAMP_BITS, WORKER_BITS)
# 4096 4096000 41 10
```

## Clock Backward

Holly's last id used timestamp 5000 and sequence 12. The wall clock now reads 4990. The pair `(holly, 4990, 0)` is already in the issued set. What is true of a new id stamped 4990 with sequence 0, and what does a mint that keeps uniqueness do?

```python
FURNACE = 1
LAST = (5000, 12)
CLOCK_TS = 4990
ISSUED = {(FURNACE, 4990, 0), (FURNACE, 5000, 12)}
```

**Answer:** The new id is already in the issued set, so uniqueness fails, and `(1, 4990, 0)` sorts before `(1, 5000, 12)`, so the pour log would place the new pour ahead of one already written. A mint that keeps uniqueness returns `wait` while the wall clock is behind the last timestamp this furnace issued. Holly mints again when the clock reaches 5000, and the next sequence is 13 if that slot is free. Why the clock stepped is Unreliable Clocks. This exercise is the id holly refuses to stamp.

```python
FURNACE = 1
LAST = (5000, 12)
CLOCK_TS = 4990
ISSUED = {(FURNACE, 4990, 0), (FURNACE, 5000, 12)}


def bad(furnace: int, clock_ts: int) -> tuple[int, int, int]:
    return (furnace, clock_ts, 0)


def safe(last: tuple[int, int], clock_ts: int) -> str:
    last_ts, _seq = last
    if clock_ts < last_ts:
        return "wait"
    return "mint"


bad_id = bad(FURNACE, CLOCK_TS)
print(bad_id in ISSUED, bad_id < (FURNACE, LAST[0], LAST[1]), safe(LAST, CLOCK_TS))
# True True wait
```

## Ticket Step

North takes offset 1 and south takes offset 2. The shared step is 2. List the first three ids from each desk. Are the six ids unique? South issues its three before north issues any. Does issuance order match id order?

```python
STEP = 2
COUNT = 3
NORTH_OFFSET = 1
SOUTH_OFFSET = 2
```

**Answer:** North issues 1, 3, 5. South issues 2, 4, 6. The six ids are unique because each residue belongs to one desk. Issuance order is 2, 4, 6, 1, 3, 5, which is not id order, so the smaller id can be the later pour. A gap is the same arithmetic: while south is down, north's next ids are still the odds, and the evens never appear. One desk with one counter would keep a single order and would also be one outage. These two desks only mint. The pour primaries are Offset Primary.

```python
STEP = 2
COUNT = 3
NORTH_OFFSET = 1
SOUTH_OFFSET = 2


def series(offset: int, step: int, count: int) -> tuple[int, ...]:
    return tuple(offset + step * i for i in range(count))


north = series(NORTH_OFFSET, STEP, COUNT)
south = series(SOUTH_OFFSET, STEP, COUNT)
unique = len(set(north + south)) == len(north) + len(south)
issued = south + north
print(north, south, unique, issued == tuple(sorted(issued)))
# (1, 3, 5) (2, 4, 6) True False
```

## Offset Primary

Holly, yew, and ash are the pour primaries. The step is 3 and the offsets are 1, 2, and 3. Each primary has issued three ids. Do those nine ids collide? Elm then tries offset 4 while the step is still 3. Which of elm's first three ids are already issued? The step then becomes 4, the offsets stay 1, 2, 3, and 4, and every next id must be greater than the largest id already issued. What is the first id for each offset?

```python
OLD_STEP = 3
NEW_STEP = 4
OFFSETS = (1, 2, 3, 4)
COUNT = 3
```

**Answer:** The nine ids are 1 through 9, with no collision. Elm's old series is 4, 7, 10, and 4 and 7 are already issued. There is no fourth residue modulo 3. After the step becomes 4, the first ids above 9 are holly 13, yew 10, ash 11, and elm 12. Who is allowed to accept a pour write is Replication Topologies. The residues are the id scheme.

```python
OLD_STEP = 3
NEW_STEP = 4
OFFSETS = (1, 2, 3, 4)
COUNT = 3


def series(offset: int, step: int, count: int) -> tuple[int, ...]:
    return tuple(offset + step * i for i in range(count))


issued: set[int] = set()
for offset in OFFSETS[:3]:
    issued.update(series(offset, OLD_STEP, COUNT))
elm_old = series(4, OLD_STEP, COUNT)
overlap = tuple(sorted(set(elm_old) & issued))
high = max(issued)


def first_above(offset: int, step: int, high_id: int) -> int:
    start = offset
    while start <= high_id:
        start += step
    return start


starts = tuple(first_above(offset, NEW_STEP, high) for offset in OFFSETS)
print(len(issued) == 9, overlap, starts)
# True (4, 7) (13, 10, 11, 12)
```

## Short Code

The window will label 20,000 bowls in base 62. How many codes do 2 characters hold, how many do 3 hold, and how many characters does the counter path use? Bowl 1 and bowl 3,845 share a 2-character hash slot when the salt is 0. What is that slot, and what slot does bowl 3,845 take when its salt becomes 1?

```python
BOWLS = 20_000
BASE = 62
SALT_STEP = 13
```

**Answer:** Two characters hold 3,844 codes, which is short of 20,000. Three characters hold 238,328, so the counter path uses 3 and does not look the code up. A 2-character hash prefix has those same 3,844 slots. Bowl 1 and bowl 3,845 both land on slot 97 when the salt is 0. Salt 1 moves bowl 3,845 to slot 110, and the desk keeps that code only after the lookup shows the slot free. The same lookup, with a new salt or one more character, is the collision path at any prefix length. The redirect and the cache of a short link stay on URL Shortener.

```python
BOWLS = 20_000
BASE = 62
SALT_STEP = 13


def space(chars: int, base: int) -> int:
    return base**chars


def slot(bowl: int, salt: int, space_size: int) -> int:
    return (bowl * 97 + salt * SALT_STEP) % space_size


two = space(2, BASE)
three = space(3, BASE)
counter_chars = 3 if two < BOWLS <= three else 0
print(two, three, counter_chars, slot(1, 0, two), slot(1 + two, 0, two), slot(1 + two, 1, two))
# 3844 238328 3 97 97 110
```

## Pick the ID

The shop has three jobs open at once: the pour row, the name the tablet puts on a call it may send twice, and the code on the window card. Which scheme fits each job?

```python
OBJECTS = ("pour-row", "tablet-retry", "window-card")
```

**Answer:** The pour row is a Snowflake id: time order, 8 bytes, minted on the furnace. The tablet retry is a UUID, because the tablet has no furnace number. What that name means when the call is repeated is Idempotency. The window card is a base-62 counter. A ULID would sort and would still be 16 bytes, so it misses the pour key's width. An offset sequence on the three primaries would stay unique and would not give the pour log one timeline.

```python
OBJECTS = ("pour-row", "tablet-retry", "window-card")
PICK = {
    "pour-row": "snowflake",
    "tablet-retry": "uuid",
    "window-card": "base62",
}

print(*(PICK[name] for name in OBJECTS))
# snowflake uuid base62
```
