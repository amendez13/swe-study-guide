# Unique ID Generation

Orders, tweets, and short links all need ids, and they do not need the same id. A distributed order id is unique across datacenters, sorts by time, fits in 8 bytes, and can be minted on the writer that inserts the row. A client retry key and a public short code drop parts of that bar on purpose. Clocks, the meaning of a retry, replication topology, schema bytes, leader election, and the shortener product stay in the topics that own them.

## Key Points

- **ID Requirements** — unique across writers, time-sortable, at least 10,000 local mints a second, and 8 bytes. One database's auto-increment covers that while every insert shares its counter. A second database that also starts at 1 reuses every id.
- **UUID** — 128 bits, 122 of them random in version 4, minted with no shared counter. A million rows are not a collision problem (about 1 in 10^25). The binary key is 16 bytes. InnoDB pays that width in the clustered index and in every secondary index, and random inserts split leaves away from the right edge. A client can send a UUID as the name of a call.
- **Snowflake ID** — Twitter's layout keeps the high bit 0, then 41-bit milliseconds since 4 November 2010, 5 datacenter bits, 5 worker bits, and a 12-bit sequence. One worker mints 4,096 ids in a millisecond, then waits for the next millisecond. A clock behind the last stamp is refused (Twitter) or waited out (the drill). The 41-bit field lasts about 69.7 years, until July 2080 for Twitter's epoch. Worker numbers are provisioned, and a duplicate pair collides.
- **Ticket Server** — one Flickr-style counter is one order and one outage. Two servers, step 2, offsets 1 and 2, issue odds and evens and stay unique. Server B can issue 6 before server A issues 1. `LAST_INSERT_ID()` has to be read on the same connection that advanced the counter.
- **Multi-Master Sequence** — three MySQL primaries use step 3 and offsets 1, 2, and 3. The series 1, 4, 7 and 2, 5, 8 and 3, 6, 9 never meet, and they are not one clock. A fourth primary needs step 4, and its next id has to sit above every id already issued.
- **ULID and Other Modern Alternatives** — a ULID is 48 timestamp bits and 80 random bits, written as 26 Crockford Base32 characters. UUID version 7 sorts as a UUID and stays 16 bytes. A 12-bit counter inside version 7 is local to one process. The 8-byte key stays a Snowflake id.
- **Base62 or Hash** — a counter in base 62 uses 3 characters for 20,000 links, because 2 characters hold only 3,844. A hash prefix of that length can collide, and the service checks, then salts again or adds a character. The shortener product stays in Classic Design Problems.
- **ID Strategy** — Snowflake for the order or tweet id, a UUID for the client's call name, ULID or UUID version 7 for a sortable 16-byte id, a ticket server for one moderate order, an offset sequence on the primaries, and Base62 or a hash for the short link.

## Example

One worker packs a Snowflake-shaped id for two sequences in millisecond offset 5 and the first sequence in millisecond offset 6. The worker field here is the 10 bits under the timestamp (datacenter and machine together). Three primaries take step 3. A shortener counts the base-62 characters for 20,000 links.

```python
def pack(ts: int, worker: int, seq: int) -> int:
    return (ts << 22) | (worker << 12) | seq


def series(offset: int, step: int, count: int) -> tuple[int, ...]:
    return tuple(offset + step * i for i in range(count))


def width(n: int, base: int = 62) -> int:
    chars = 1
    space = base
    while space < n:
        chars += 1
        space *= base
    return chars


east = series(1, 3, 3)
eu = series(2, 3, 3)
apac = series(3, 3, 3)
print(
    pack(5, 1, 0) < pack(5, 1, 1) < pack(6, 1, 0),
    len(set(east + eu + apac)) == 9,
    width(20_000),
)
# True True 3
```

Millisecond offset 6 sorts after offset 5, and inside offset 5 the sequence sorts. The three offset series are nine distinct ids. Twenty thousand links fit in 3 base-62 characters. A wall clock that steps backward is Unreliable Clocks. A repeated client call is Idempotency.

## See also

- [Interview Framework and Process](../01_Interview_Framework_and_Process/) — The Four-Step Framework. Scoping which id properties the question requires stays there.
- [Consistency and Replication](../09_Consistency_and_Replication/) — Replication Topologies and Conflict Resolution. Who accepts a write, and what happens when two primaries write one key, stays there. The offset and the step stay here.
- [Networking and Communication](../10_Networking_and_Communication/) — Idempotency. What a repeated call means stays there. A UUID the client mints can be the key.
- [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/) — schema bytes stay there. Base62 and a hash prefix for a short code live here.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Unreliable Clocks. Why a wall clock steps stays there. Refusing or waiting out a backward step on one worker stays here.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — Leader Election. A worker id written down at provision time is configuration, and every such worker mints.
- [Classic Design Problems](../24_Classic_Design_Problems/) — URL Shortener. The redirect, the cache, and the read path stay there. The short code stays here.
