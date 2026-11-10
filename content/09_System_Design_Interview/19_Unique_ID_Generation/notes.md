# Unique ID Generation

Rowan Glassworks logs a pour from holly, yew, or ash, takes a retry from the clerk's tablet, and prints a short code on the bowl in the street window. A pour id is unique across the furnaces, sorts in pour order, fits in 8 bytes, and can be minted on the furnace. A tablet key and a window card drop parts of that bar on purpose. Clocks, the meaning of a retry, replication topology, schema bytes, leader election, and the shortener product stay in the topics that own them.

## Key Points

- **ID Requirements** — unique across the furnaces, time-sortable, 10,000 local mints a second on one furnace, and 8 bytes. One database's autoincrement covers that while every insert shares it.
- **UUID** — 128 bits, 122 of them random in version 4, minted with no shared counter. A million rows are not a collision problem. The clustered index loses pour order, pays 16 bytes, and splits on random inserts. A tablet can use a UUID as the name of a call.
- **Snowflake ID** — the high bit stays 0, then 41-bit milliseconds since 2024-01-01, 5 shop bits, 5 furnace bits, and a 12-bit sequence. One furnace mints 4,096 ids in a millisecond. The next mint waits. A wall clock behind the last stamp waits too. Furnace numbers are provisioned.
- **Ticket Server** — one desk is one order and one outage. North and south, step 2, offsets 1 and 2, stay unique. South can issue 6 before north issues 1.
- **Multi-Master Sequence** — holly, yew, and ash use step 3 and offsets 1, 2, and 3. The series do not meet, and they are not a pour clock. A fourth primary needs step 4 and a next id above the ids already issued.
- **ULID and Other Modern Alternatives** — a ULID is 48 timestamp bits and 80 random bits, written as 26 Base32 characters. UUID v7 sorts as a UUID and stays 16 bytes. The 8-byte pour key stays a Snowflake id.
- **Base62 or Hash** — a counter in base 62 uses 3 characters for 20,000 bowls. A hash prefix of that length can collide, and the desk checks, then salts again or adds a character. The shortener product stays in Classic Design Problems.
- **ID Strategy** — Snowflake for the pour key, a UUID for the tablet's call name, ULID or UUID v7 for a sortable 16-byte id, a ticket desk for one moderate order, an offset sequence on the pour primaries, and Base62 or a hash for the window card.

## Example

Holly packs a Snowflake id for two sequences in millisecond 5 and the first sequence in millisecond 6. The three pour primaries take step 3. A window card counts the base-62 characters for 20,000 bowls.

```python
def pack(ts: int, furnace: int, seq: int) -> int:
    return (ts << 22) | (furnace << 12) | seq


def series(offset: int, step: int, count: int) -> tuple[int, ...]:
    return tuple(offset + step * i for i in range(count))


def width(n: int, base: int = 62) -> int:
    chars = 1
    space = base
    while space < n:
        chars += 1
        space *= base
    return chars


holly = series(1, 3, 3)
yew = series(2, 3, 3)
ash = series(3, 3, 3)
print(
    pack(5, 1, 0) < pack(5, 1, 1) < pack(6, 1, 0),
    len(set(holly + yew + ash)) == 9,
    width(20_000),
)
# True True 3
```

Millisecond 6 sorts after millisecond 5, and inside millisecond 5 the sequence sorts. The three offset series are nine distinct ids. Twenty thousand bowls fit in 3 base-62 characters. A wall clock that steps backward is Unreliable Clocks. A repeated tablet call is Idempotency.

## See also

- [Interview Framework and Process](../01_Interview_Framework_and_Process/) — The Four-Step Framework. Scoping a unique-id question stays there.
- [Consistency and Replication](../09_Consistency_and_Replication/) — Replication Topologies. Who accepts a write, and how the other copies learn it, stays there. The offset and the step stay here.
- [Networking and Communication](../10_Networking_and_Communication/) — Idempotency. What a repeated call means stays there. A UUID the tablet mints can be the key.
- [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/) — schema bytes stay there. Base62 and a hash prefix for a short code live here.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Unreliable Clocks. Why a wall clock steps stays there. Waiting out a backward step on one furnace stays here.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — Leader Election. A furnace id written down at provision time is not an election.
- [Classic Design Problems](../24_Classic_Design_Problems/) — URL Shortener. The redirect, the cache, and the read path stay there. The short code stays here.
