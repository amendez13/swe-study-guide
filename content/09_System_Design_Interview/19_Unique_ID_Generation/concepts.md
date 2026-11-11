## ID Requirements

An id requirement is the short list of properties an identifier has to keep so that many writers can create rows without agreeing on each value first. One `orders` table on one database can number rows with an 8-byte auto-increment counter. The insert draws the next integer, the values increase, and each appears once. That ends when a second database also inserts orders, because each has its own counter and both issue `1`, then `2`, then `3`. The rest of this topic is how to keep an id meaningful after that split.

Take a checkout service that must mint 10,000 order ids a second. The list has four lines. Uniqueness means one id names one order across every datacenter that inserts. Time order means a larger id is a later order, so `ORDER BY id` follows creation, at a resolution of one millisecond. Local throughput means the writer that needs the id mints it on that machine, without a round trip to a shared counter. Width means the value occupies 8 bytes in a clustered index. A single MySQL primary meets all four while every insert shares its counter. Three primaries that each start at 1 fail uniqueness, because order 1 exists three times. As a yardstick for the later cards, one Snowflake worker can mint 4,096,000 ids a second, while a ticket server pays one database round trip for each of the 10,000.

Drop one line and a simpler scheme fits. A client that only needs a name for a retry can use a random UUID and ignore time order and width. A public link that only needs a short code can ignore the 8-byte key. Keep all four and the design is a Snowflake id. Even then the ids have gaps, so the largest id is a poor count of orders. An id that appears in a URL and must be hard to guess needs a random part, which works against compact and sequential. Say the four properties before naming an algorithm. Scoping which ones the question requires is The Four-Step Framework in [Interview Framework and Process](../01_Interview_Framework_and_Process/).

```text
unique        one id, one order, across every writer
time order    larger id = later order, 1 ms resolution
local         minted on the writer, 10,000 a second
width         8 bytes
one primary   auto-increment meets all four, stop there
```

![ID Requirements](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-1-id-requirements.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 1.*

## UUID

A UUID is a 128-bit value any process can mint without asking another process. Version 4, the usual random form, draws 122 bits from a random source, and the other 6 bits record the version and variant. A phone, browser, or app server often needs a name before a database is involved. The client can put a UUID on a create-order call and resend the same value if the response is lost. What the server does with that repeat is Idempotency in [Networking and Communication](../10_Networking_and_Communication/).

Postgres `gen_random_uuid()` returns a version-4 UUID. It is 16 bytes as binary and 36 characters as hyphenated hex text, so store the 16 bytes. A collision means two minters drew the same 122 bits. Among a million UUIDs the chance is about 1 in 10^25, by the birthday approximation n² / 2^123, so at normal table sizes collisions are the wrong thing to plan around. The real costs show up in the index. InnoDB stores the row in the primary-key B-tree and repeats that key inside every secondary index, so a 16-byte key widens all of them. A random key also lands on a random leaf, which splits, and later inserts keep landing somewhere else. A time-ordered key appends at the right edge. Sorting by a version-4 UUID follows the random draw, not creation time.

Version 4 needs no coordinator, worker number, or clock. It spends time order, index locality, and 8 extra bytes compared with a Snowflake id. UUID version 7 and ULID keep the local mint and put a timestamp in the high bits, still at 16 bytes. Use version 4 for a client-generated retry name. For the clustered key of a large time-ordered table, move to Snowflake, or to version 7 when the column is already a UUID.

```text
v4         122 random bits + 6 version and variant bits
size       16 bytes binary, 36 characters as text
collision  about 1 in 10^25 at a million rows
real cost  wider indexes, random leaf splits, no time order
```

![UUID](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-2-uuid.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 2.*

## Snowflake ID

A Snowflake id is a 64-bit integer that a writer mints locally by packing a millisecond timestamp, a worker number, and a sequence. Twitter introduced the layout for tweet ids. It meets the whole order-id bar: the mint stays on the writer, the value fits a signed 64-bit integer, and time sits in the high bits, so a larger id is a later millisecond. Twitter's `IdWorker` keeps bit 63 at 0, then uses 41 bits of milliseconds since a chosen epoch, 5 bits of datacenter, 5 of worker, and 12 of sequence. The pack is `(timestamp << 22) | (datacenter << 17) | (worker << 12) | sequence`.

Twitter's epoch is 1288834974657, which is 4 November 2010, 01:42:54.657 UTC. 41 bits of milliseconds cover about 69.7 years, so that epoch runs out in July 2080. A new system picks an epoch near its launch, and ids under different epochs do not compare as wall time. Each generator is provisioned with its datacenter and worker numbers, giving 32 × 32 = 1,024 generators. Two live processes given the same pair silently emit the same ids. That is config assignment, not Leader Election in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). On each mint the worker reads the clock and subtracts the epoch. If the clock is behind the last timestamp it issued, it must not stamp that earlier millisecond. Twitter refuses the call, and some ports wait for the clock to catch up, which is the policy the Clock Backward drill uses. Why clocks jump is Unreliable Clocks in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). A new millisecond starts the sequence at 0, and the same millisecond adds 1. That allows 4,096 ids per millisecond, or 4,096,000 a second. The 4,097th waits for the next millisecond.

Ids sort by millisecond, then datacenter, worker, and sequence. Inside one millisecond, worker 7 sorts after worker 3 even if worker 3's call came later, and clock skew moves that boundary. The series has gaps, so the largest id is a poor count. JavaScript's `Number` stops being exact at 2^53 − 1, so APIs return these ids as strings. A right shift of 22 recovers the timestamp, so the id is a weak secret. You operate the worker assignment, a per-process counter, and an epoch with an end date.

```text
layout     0 | 41 ms | 5 datacenter | 5 worker | 12 sequence
epoch      Twitter's 2010 epoch, about 69.7 years, ends July 2080
rate       4,096 per ms per worker, then wait for the next ms
backward   refuse or wait, never stamp an earlier ms
workers    1,024 pairs, a repeated pair collides silently
```

![Snowflake ID](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-3-snowflake-id.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 3.*

## Ticket Server

A ticket server is a database whose only job is the next integer. The application asks for a number, then stores the order in whichever database owns it. Flickr used ticket servers to keep photo ids unique across many MySQL shards. Once orders are spread out, each database's auto-increment repeats `1`, `2`, `3`. A single counter restores one sequence, and putting it on its own machine keeps its write load off the order databases.

Flickr's table is one row, an auto-increment id plus a unique stub column. The client replaces that row, then reads the new id on the same connection:

```sql
REPLACE INTO tickets64 (stub) VALUES ('a');
SELECT LAST_INSERT_ID();
```

`LAST_INSERT_ID()` belongs to the connection, so a pool that splits the two statements returns someone else's id. One server issues 1, 2, 3, which is one increasing order, one outage, and one write ceiling. A client that receives 42 and crashes before inserting leaves a gap. The next id is still 43, so uniqueness holds but the high-water mark overcounts. Two servers with step 2 remove the single outage, the split Flickr ran. Server A issues 1, 3, 5 and server B issues 2, 4, 6. Each residue belongs to one server, so the pair stays unique even when one gets ahead, and while B is down the evens simply never appear. They no longer share one timeline, so B can hand out 6 before A hands out 1, and the smaller id is the later order. A third server has no free residue until the step changes.

The integers are compact, debuggable, and good for a clustered index. Every mint is a round trip, though, so 10,000 ids a second means 10,000 writes a second on the ticket database, on the request path. Snowflake mints without that round trip, at the cost of a worker id and a custom epoch. The same step and offset on the databases that store the rows is Multi-Master Sequence.

```text
one server    1, 2, 3: one order, one outage, one write limit
lost ticket   a gap, the next id is still larger
two servers   1, 3, 5 and 2, 4, 6, unique but no single timeline
third server  change the step first
```

![Ticket Server](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-4-ticket-server.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 4.*

## Multi-Master Sequence

A multi-master sequence gives each database primary its own residue of one integer series, and the primary assigns that number as it inserts the row. MySQL exposes the knobs as `auto_increment_increment` (the step) and `auto_increment_offset` (the residue). A ticket server is an extra hop in front of every insert. If the primary that stores the order can mint a non-overlapping id itself, the insert carries its own key and the ticket database goes away.

Three primaries take step 3 with offsets 1, 2, and 3. They issue 1, 4, 7, then 2, 5, 8, then 3, 6, 9. The residues never meet, so the nine ids are 1 through 9, but the series does not record creation order across primaries. Offset 2 can commit 8 while offset 1 is still at 4. Offset 1's next order then gets 7, and sorting by id shows it first even though it came later. A fourth primary has no free residue modulo 3. Walking offset 4 with the old step gives 4, 7, 10, and 4 and 7 already exist. MySQL ignores an offset greater than the step anyway. Before the new primary mints, the step becomes 4 and each primary takes a distinct offset in 1..4. Each next id must exceed the largest issued and stay on its own residue, so after 1 through 9 the first ids are 13, 10, 11, and 12.

There is no ticket hop, and the key stays an 8-byte integer that a clustered index appends in per-primary bursts. A down primary leaves its residue as a gap, and adding a primary is a coordinated step change done before it issues anything. Snowflake puts time in the high bits so different writers still sort by millisecond, while this scheme only keeps the residues apart. Use it when the system already runs multi-master MySQL and wants integer keys. Which nodes accept writes and how conflicts resolve are Replication Topologies and Conflict Resolution in [Consistency and Replication](../09_Consistency_and_Replication/).

```text
step 3      1, 4, 7 / 2, 5, 8 / 3, 6, 9
order       a smaller id can be the later insert
4th, step 3 repeats 4 and 7
step 4      next ids 13, 10, 11, 12
```

![Multi-Master Sequence](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-5-multi-master-sequence.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 5.*

## ULID and Other Modern Alternatives

A ULID is a 128-bit id with a Unix millisecond timestamp in front and random bits after it. UUID version 7 is the IETF form of the same idea in RFC 9562. Teams want new rows to insert in time order, and they want any process to mint ids without a datacenter registry. Version 4 is local and unordered. Snowflake is ordered and 8 bytes but needs the registry. ULID and version 7 sit in the middle: local, time-ordered, and 16 bytes.

A ULID uses 48 bits of Unix milliseconds, which last until about the year 10889, and 80 random bits. Its text form is 26 characters of Crockford's Base32, the digits and letters without I, L, O, and U, so a person can read it aloud. The string sorts like the bits, with 10 characters of time and a 16-character random tail. Two ULIDs in the same millisecond sort by their random draw, unless a monotonic generator bumps the tail inside one process. That bump is local, and it is not a worker id. UUID version 7 lays out 48 bits of `unix_ts_ms`, a version nibble of 7, 12 bits of `rand_a`, 2 variant bits, and 62 bits of `rand_b`. RFC 9562 lets `rand_a` count ids within a millisecond, but that counter lives in one process, so uniqueness across processes still comes from the random bits. Snowflake's 4,096 sequence is different, because it is unique by construction, with the worker packed into the same id.

There is no worker table to get wrong. The key is as wide as a version-4 UUID, so InnoDB still carries 16 bytes in every index. Inserts land on the right edge, which is the locality you wanted, and that edge becomes a hot page under one hard-writing process. A same-millisecond collision needs two generators to draw the same 80-bit tail, which is far beyond a normal table. Choose a ULID or version 7 when the column is already 16 bytes and rows should insert in time order. Choose Snowflake when the key must be 8 bytes or a worker must guarantee 4,096 distinct ids per millisecond.

```text
ULID      48 ms + 80 random, 26 Crockford Base32 characters
UUIDv7    48 ms | ver 7 | 12 rand_a | variant | 62 rand_b
counter   local to one process, not a worker id
both      16 bytes, the 8-byte key stays Snowflake
```

![ULID and Other Modern Alternatives](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-6-ulid-and-other-modern-alternatives.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 6.*

## Base62 or Hash

A short code is a few characters that name a long URL. Base62 writes an integer in a 62-character alphabet, and a hash path writes a prefix of a digest in that same alphabet. A Snowflake id is too long for a link a person will retype. This card is only how the code is chosen. The redirect, cache, and read path are URL Shortener in [Classic Design Problems](../24_Classic_Design_Problems/), and growing the stored field is in [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/).

Every writer uses one alphabet in one order: here the 10 digits, then 26 lowercase letters, then 26 uppercase letters. One character covers 62 codes, two cover 3,844, three cover 238,328, and four cover 14,776,336. A counter path takes the next integer and encodes it. For 20,000 links, two characters fall short and three are enough. The code is unique because the counter was, so no lookup is needed. Counter 1 becomes `1` and counter 2 becomes `2`, so a reader who has seen one link can try its neighbors. A hash path hashes the destination or internal id and keeps a prefix. Three characters have the same 238,328 slots, filled out of order, and two destinations can land on one prefix. The service looks the code up, and on a clash it adds a new salt or one more character and checks again.

Base64 uses `+`, `/`, and `=`, which need escaping in a URL, and Base62 drops them. Base58 also drops look-alike characters, so it needs more characters for the same volume. Counter codes stay short and walkable, and they need a shared counter such as an auto-increment, a ticket server, or an encoded Snowflake id. Hash codes hide the next link only as well as their length allows, and each new code costs a read. Public links can be guessable. Unlisted documents need the hash path or a random code of the same width.

```text
62^2 = 3,844        too few for 20,000 links
62^3 = 238,328      enough
counter path        unique, no lookup, neighbors are guessable
hash path           look up, retry with a salt or one more character
```

![Base62 or Hash](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-7-base62-or-hash.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 7.*

## ID Strategy

The order row, the client's retry key, and the public short code are three different ids, each chosen from the property it has to keep. One scheme that satisfies the strictest job overpays on the others. A version-4 UUID on every order widens the clustered index and scatters inserts. A Snowflake id as a retry name forces the phone to hold a worker number. A three-character base62 counter is the right width for a public link and the wrong width for a global order id.

Match the job, then the scheme. While one database takes every insert, auto-increment keeps all four requirements. An order or tweet id that needs time order, 8 bytes, and a local mint is Snowflake. A name the client puts on a call it may send twice is UUID version 4, which it can mint without a worker number. A sortable 16-byte id with no registry is a ULID or UUID version 7. One moderate sequence that can afford a round trip is a ticket server, with a single order until a second server joins. Each primary numbering its own rows, with no ticket hop, is a multi-master sequence. A few characters in a public URL are a Base62 counter or a hash prefix, and only the hash path looks the code up.

Change one requirement and the answer changes. Drop the 8-byte limit and a ULID can be the order id. A client that must mint order ids offline can use version 4, and `ORDER BY id` then follows random bits. These ids all leave gaps, so a gapless order count is a query over the rows. Name the scheme and the requirement the runner-up misses. A ULID sorts but is 16 bytes, and offset sequences stay unique but lose a single timeline. Repeat calls are Idempotency in [Networking and Communication](../10_Networking_and_Communication/), write ownership is Replication Topologies in [Consistency and Replication](../09_Consistency_and_Replication/), and the shortener is URL Shortener in [Classic Design Problems](../24_Classic_Design_Problems/).

```text
one database        auto-increment
order or tweet id   Snowflake
client retry name   UUID v4
sortable, 16 bytes  ULID or UUID v7
moderate sequence   ticket server
per-primary rows    multi-master sequence
public short link   Base62 counter or hash prefix
```

![ID Strategy](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-8-id-strategy.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 8.*
