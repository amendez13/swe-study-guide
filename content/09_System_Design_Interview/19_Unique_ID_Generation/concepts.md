## ID Requirements

An id requirement is the short list of properties an identifier has to keep so that many writers can create rows without agreeing on each value first. The list in this topic is uniqueness across writers, time order, local throughput, and an 8-byte key.

**Why it exists.** One `orders` table on one database can number its rows with an 8-byte auto-increment counter. The insert itself draws the next integer, the values increase, and each value appears once. That arrangement ends when a second database also inserts orders. Each database has its own counter, so both will issue `1`, then `2`, then `3`. The rest of this topic is how to keep an id meaningful after that split. Scoping which of these properties a question actually requires is The Four-Step Framework in [Interview Framework and Process](../01_Interview_Framework_and_Process/).

**How it works.** Take a checkout service that must mint 10,000 order ids a second.

1. Uniqueness: one id names one order across every datacenter that inserts.
2. Time order: a larger id is a later order, so `ORDER BY id` follows creation. The resolution used later is one millisecond.
3. Local throughput: the writer that needs the id mints it on that machine. A round trip to a shared counter is a different design.
4. Width: the value occupies 8 bytes in a clustered index.

A single MySQL primary meets all four while every insert shares its counter. Three primaries that each start at 1 fail uniqueness, because order 1 exists three times. Ten thousand ids a second is the rate the later cards are checked against. One Snowflake worker can mint 4,096,000 ids a second. A ticket server pays one database round trip for each of the 10,000.

**Trade-offs.** Drop one line and a simpler scheme fits. A client that only needs a name for a retry can use a random UUID and ignore time order and width. A public link that only needs a short code can ignore the 8-byte key. Keep the four lines and the design is a Snowflake id. An id that meets the four lines still has gaps, so the largest id is a poor count of orders. An id that appears in a URL and must be hard to guess needs a random component as well. Compact and sequential work against that.

**In an interview.** Say the four properties before you name an algorithm. Then say whether the system still has one database. One primary means auto-increment, and you stop. Several writers means you walk the schemes below and name which property each one spends.

**Recap**

- One order id names one order across every datacenter that inserts it.
- A larger id is a later order, so sorting by the id follows creation.
- Each writer mints at least 10,000 ids a second on that writer.
- The id occupies 8 bytes.
- One database auto-increment meets the list while every insert uses its counter.

![ID Requirements](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-1-id-requirements.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 1.*

## UUID

A UUID is a 128-bit value any process can mint without asking another process. Version 4, the usual random form, draws 122 of those bits from a random source. The other 6 bits record the version and the variant.

**Why it exists.** A phone, a browser, or an app server often needs a name before a database is involved. The client can put a UUID on a create-order call and send that same value again if the response is lost. The database can store the value as a primary key with no shared counter and no worker registry. What the server does when the same call arrives again is Idempotency in [Networking and Communication](../10_Networking_and_Communication/).

**How it works.** Postgres `gen_random_uuid()` returns a version-4 UUID. Stored as binary it is 16 bytes. Stored as the usual hex text it is 36 characters, hyphens included. Prefer the 16 bytes in the index.

A collision means two minters drew the same 122 bits. Among a million version-4 UUIDs the chance of that is about 1 in 10^25, because the birthday approximation is n² / 2^123. At the size of a normal orders table, a collision is the wrong thing to plan around.

The costs show up in the index. InnoDB stores the row in the primary-key B-tree, and it stores that primary key again inside every secondary index. A 16-byte key makes the clustered index and those secondary indexes wider than an 8-byte key. A random key also lands on a random leaf. The leaf splits, and later inserts keep landing somewhere else. A key that grows with time appends at the right edge of the same tree. Sorting the UUID reproduces the random draw. `ORDER BY id` follows that draw. Creation time is a different sequence.

**Trade-offs.** Version 4 needs no coordinator, no worker number, and no clock. It spends time order, index locality, and 8 extra bytes against a Snowflake id. UUID version 7 and a ULID keep the local mint and put a timestamp in the high bits. They are still 16 bytes. A ticket server and a multi-master sequence return compact integers and need a database round trip or a configured offset.

**In an interview.** When the worry in the room is collisions, give the scale: a million rows is far below where 122 random bits meet. Then give the costs you would actually design for: 16 bytes, random leaf splits, and a sort that ignores creation time. Use version 4 for a client-generated retry name. For the clustered primary key of a large time-ordered table, move to Snowflake, or to UUID version 7 when the column is already a UUID.

**Recap**

- Version 4 is 122 random bits plus 4 version bits and 2 variant bits.
- The binary key is 16 bytes. The hex text form is 36 characters.
- A million rows are far too few for a collision to be the design risk.
- InnoDB pays the 16 bytes in the clustered index and again in every secondary index.
- New rows land on random leaves, and sorting by the id ignores creation order.
- A client can mint one and send it as the name of a call.

![UUID](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-2-uuid.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 2.*

## Snowflake ID

A Snowflake id is a 64-bit integer a writer mints locally by packing a millisecond timestamp, a worker number, and a sequence. Twitter introduced the layout for tweet ids. A configured worker mints without taking a number from a shared counter, and the timestamp sits in the high bits.

**Why it exists.** The order-id bar asks for uniqueness, time order, 10,000 local mints a second, and 8 bytes. A shared auto-increment counter is a round trip and a single outage. A version-4 UUID is local and 16 random bytes. Snowflake keeps the mint on the writer, keeps the value in a signed 64-bit integer, and puts the time in the high bits so a larger id is a later millisecond.

**How it works.** Twitter's published generator (`IdWorker`) lays the bits out like this. The high bit stays 0 so the value stays positive in a signed 64-bit integer.

| Bits | Width | What it holds |
| --- | --- | --- |
| 63 | 1 | Always 0 |
| 62–22 | 41 | Milliseconds since a chosen epoch |
| 21–17 | 5 | Datacenter, 0–31 |
| 16–12 | 5 | Worker, 0–31 |
| 11–0 | 12 | Sequence, 0–4095 |

The pack is `(timestamp << 22) | (datacenter << 17) | (worker << 12) | sequence`.

Twitter's epoch is 1288834974657, which is 4 November 2010, 01:42:54.657 UTC. A 41-bit millisecond field covers about 69.7 years, so that epoch runs out in July 2080. A new system picks an epoch near its own launch and gets its own 69.7-year window. An id minted under a different epoch is a different timeline. Comparing the integers does not compare wall-clock time.

Each generator stores the datacenter and worker it was given when it was provisioned. Five plus five bits name 32 × 32 = 1,024 generators. Two live processes that were given the same pair can emit the same id. Writing those numbers into a config file assigns the generator, and every assigned worker mints. Leader Election in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) is the separate problem of choosing a node that may act for the cluster.

One worker then does this on every mint:

1. Read the clock in milliseconds and subtract the epoch.
2. If the clock reads earlier than the last timestamp this worker issued, the generator must not stamp that earlier millisecond. The new id would sort ahead of ids already handed out, and sequence 0 at the old millisecond may already be in use. Twitter's generator refuses the call. Some ports wait until the clock catches up, then continue. The Clock Backward drill uses the wait policy. Why a wall clock jumps is Unreliable Clocks in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/).
3. A new millisecond starts the sequence at 0. The same millisecond adds 1. The sequence holds 0 through 4095, which is 4,096 ids in that millisecond and 4,096,000 in one second. That clears a 10,000-per-second bar with room to spare.
4. The 4,097th mint in that millisecond has no free sequence value. The generator waits until the clock reaches the next millisecond, then emits sequence 0 there. Emitting sequence 0 again inside the same millisecond repeats an id this worker already returned.

Ids from different milliseconds sort by the timestamp. Inside one millisecond they sort by datacenter, then worker, then sequence. On the same datacenter, worker 7 sorts after worker 3 in that millisecond even when worker 3's call happened later. Clocks that disagree across machines move the boundary by the size of the skew. The series also has gaps. A gap is an unused sequence value or a refused millisecond, and the largest id is still a poor count of tweets.

**Trade-offs.** You operate a worker-id assignment, a monotonic counter inside each process, and an epoch with an end date. JavaScript's `Number` cannot represent every integer past 2^53 − 1. A current Twitter id is wider than that, so an API returns these ids as strings. The timestamp is recoverable with a right shift of 22, so the id is a weak secret. A UUID version 7 or a ULID removes the worker registry and costs 16 bytes. A ticket server removes the bit layout and adds a round trip.

**In an interview.** Draw the 1 / 41 / 5 / 5 / 12 split and compute 4,096 ids per millisecond before you discuss coordination. Then say the two clock cases: a full sequence waits for the next millisecond, and a backward step is refused or waited out. Say how a worker id is assigned, and that a duplicate assignment is a silent collision. Name the epoch and its end, about 69.7 years out, July 2080 for Twitter's constant.

**Recap**

- The high bit stays 0. Then 41 timestamp bits, 5 datacenter bits, 5 worker bits, and 12 sequence bits.
- Twitter's epoch is 4 November 2010. The 41-bit field lasts about 69.7 years, until July 2080 for that epoch.
- One worker mints 4,096 ids in one millisecond, then waits for the next millisecond.
- A clock behind the last issued timestamp is refused, or waited out. It is not stamped.
- Worker numbers are provisioned. One thousand twenty-four distinct pairs are available, and a repeated pair collides.
- The id sorts by millisecond, then by machine. It is an 8-byte integer, and clients should treat it as a string.

![Snowflake ID](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-3-snowflake-id.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 3.*

## Ticket Server

A ticket server is a database whose job is the next integer. The application asks for a number, then stores the order in whichever database owns that order. Flickr used ticket servers so photo ids stayed unique across many MySQL shards.

**Why it exists.** Once orders are spread across databases, each database's auto-increment repeats `1`, `2`, `3`. A single counter restores one sequence. Putting that counter on its own machine keeps the counter's write load off the databases that store the orders.

**How it works.** Flickr's table is one row: an auto-increment id and a unique stub column. The client advances it by replacing that row, then reads the new id on the same database connection. `LAST_INSERT_ID()` belongs to the connection, so a pooled connection that splits the two statements returns someone else's id.

```sql
REPLACE INTO tickets64 (stub) VALUES ('a');
SELECT LAST_INSERT_ID();
```

One server issues 1, then 2, then 3. That is one increasing order. It is also one outage and one write ceiling. An order that needs an id during the outage waits. A client that receives 42 and crashes before the insert leaves a gap. The next id is still 43. Uniqueness holds, and the high-water mark counts gaps as if they were orders.

Two servers remove the single outage. Both use a step of 2 and take different offsets, which is the split Flickr ran. Server A starts at 1 and issues 1, 3, 5. Server B starts at 2 and issues 2, 4, 6. Each residue belongs to one server, so the pair stays unique even when one server is ahead. While B is down, A keeps issuing odds and the evens never appear. The numbers are a unique set. They share no single timeline. B can hand out 6 before A has handed out 1, and the smaller id is the later order.

A third server has no free residue while the step stays 2. The step changes first. These machines only mint. The same step and offset on the databases that store the rows is Multi-Master Sequence.

**Trade-offs.** The integers are compact, debuggable, and friendly to a clustered index. Every mint is a round trip, so 10,000 ids a second is 10,000 writes a second on the ticket database, on the request path. One server keeps a single order and a single outage. Two servers keep uniqueness through the outage and lose that single order. Snowflake mints without the round trip and sorts by millisecond. It costs a worker id and a custom epoch.

**In an interview.** Offer one ticket server when the rate is moderate and a short mint outage can block creates. When the question turns to that outage, split the number space with a step and an offset, and say that issuance order and numeric order can disagree. Keep this service separate from the database that stores the order.

**Recap**

- One ticket server issues 1, 2, 3. That is one order, one outage, and one write limit.
- A ticket that is never stored leaves a gap. The next ticket is still larger.
- Two servers with step 2 issue 1, 3, 5 and 2, 4, 6. Each residue belongs to one server.
- Server B can issue 6 before server A issues 1, so the smaller id can be the later order.
- A third server needs a new step before it mints.
- The servers only mint. They are not the databases that store the orders.

![Ticket Server](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-4-ticket-server.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 4.*

## Multi-Master Sequence

A multi-master sequence gives each database primary its own residue of one integer series, and the primary assigns that number as it inserts the row. MySQL exposes the knobs as `auto_increment_increment` (the step) and `auto_increment_offset` (the residue).

**Why it exists.** A ticket server is an extra hop in front of the insert. If the primary that stores the order can mint a non-overlapping id, the insert carries its own key and the ticket database disappears. The numbering scheme is this card. Which nodes accept writes, how a primary ships its log, and what happens when two primaries write one key are Replication Topologies and Conflict Resolution in [Consistency and Replication](../09_Consistency_and_Replication/).

**How it works.** Three primaries take step 3 and a distinct offset.

- Offset 1 issues 1, 4, 7.
- Offset 2 issues 2, 5, 8.
- Offset 3 issues 3, 6, 9.

The three residues never meet, so the nine ids are 1 through 9. The series does not record creation order across primaries. Offset 2 can commit 8 while offset 1 is still at 4. Offset 1's next order receives 7, and a query that sorts by id shows 7 first.

A fourth primary has no free residue modulo 3. Walking offset 4 with the old step produces 4, 7, 10, and 4 and 7 are already stored. MySQL will not do that walk for you: it ignores an offset greater than the step. Before the new primary mints, the step becomes 4 and each primary takes a distinct offset in 1..4. Every next id has to be greater than the largest id already issued, and it has to stay on its own residue. After 1 through 9, those first ids are 13, 10, 11, and 12.

**Trade-offs.** There is no ticket hop, and the key stays an 8-byte integer that a clustered index can append in per-primary bursts. Numeric order across primaries follows the residue arithmetic. Offset 2 can commit 8 before offset 1 commits 7, so the smaller id is the later order. A down primary leaves its residue as a gap. Adding a primary is a coordinated change of the step, done before the new primary issues anything. Snowflake puts a timestamp in the high bits, so ids from different writers still sort by millisecond. This scheme separates the residues and leaves cross-primary time order out.

**In an interview.** Use it when the system already runs multi-master MySQL and wants integer keys without a ticket service. Walk step 3 for three primaries, then show offset 4 colliding on 4 and 7, so it is obvious the new node does not keep the old step. Leave failover and write ownership in the replication topic.

**Recap**

- Step 3 with offsets 1, 2, and 3 produces 1, 4, 7 and 2, 5, 8 and 3, 6, 9.
- Those nine ids are distinct. Their sort order is the residue arithmetic, so a smaller id can be the later insert.
- A fourth primary on the old step repeats 4 and 7.
- The step becomes 4 first. The next ids above 9 are 13, 10, 11, and 12.
- The offset decides the id. Replication topology decides who may write.

![Multi-Master Sequence](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-5-multi-master-sequence.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 5.*

## ULID and Other Modern Alternatives

A ULID is a 128-bit id with a Unix millisecond timestamp in front and random bits after it. UUID version 7 is the IETF form of that idea (RFC 9562): a Unix millisecond timestamp, then the version and variant bits a UUID parser already expects, then random bits.

**Why it exists.** Teams want new rows to insert in time order, and they want any process to mint the id without a datacenter registry. Version 4 is local and unordered. Snowflake is ordered and 8 bytes, and it needs the registry. A ULID or a UUID version 7 is the middle: local, time-ordered, and 16 bytes.

**How it works.** A ULID uses 48 bits for Unix time in milliseconds and 80 bits of randomness. The 48-bit field lasts until about the year 10889. The text form is 26 characters of Crockford's Base32. That alphabet is the digits, plus the letters A–Z, without I, L, O, and U, so a person can read a code aloud. The string sorts in the same order as the 128 bits. The first 10 characters are the time and the last 16 are the random tail.

Two ULIDs in the same millisecond differ in that random tail, so their sort order is the draw. A monotonic generator bumps the tail inside one process so that process's ids increase inside the millisecond. The bump is local to that process. Another process has its own tail. The bump does not allocate a worker id. Snowflake's sequence of 4,096 is a different counter: it is unique for one worker inside one millisecond because the worker number is packed into the same id.

UUID version 7 lays the same width out for existing UUID columns:

| Field | Width | Role |
| --- | --- | --- |
| `unix_ts_ms` | 48 | Milliseconds since 1 January 1970 UTC |
| version | 4 | Fixed to 7 |
| `rand_a` | 12 | Random, or a counter local to one generator |
| variant | 2 | Fixed to the RFC 4122 variant |
| `rand_b` | 62 | Random bits that keep generators apart |

RFC 9562 allows `rand_a` to count ids inside one millisecond. That counter lives in the process that holds it. A second process can use the same count in the same millisecond. Uniqueness across processes still comes from the random bits. The counter does not name a datacenter. The whole value stays 16 bytes. Both forms let a process mint with no worker number. The 8-byte key stays a Snowflake id.

**Trade-offs.** There is no worker table to get wrong. The key is as wide as a version-4 UUID, so InnoDB still carries 16 bytes in the clustered index and in every secondary index. Inserts for the current millisecond land on the right edge, which is the locality you wanted, and that edge is a hot page while one writer is inserting hard. Eighty random bits make a same-millisecond collision a matter of two generators drawing the same tail. That bar is still far above a normal table. A pure counter encoded for a URL is shorter and guessable. Snowflake is the choice when the key has to be 8 bytes or one writer must guarantee 4,096 distinct ids in a millisecond by construction.

**In an interview.** Choose a ULID or UUID version 7 when the column is already 16 bytes and new rows should insert in time order. Say that a 12-bit counter inside UUID version 7 orders one process inside a millisecond and does not name a datacenter. Choose Snowflake when you need the 8-byte key or a per-worker sequence that does not depend on a random draw.

**Recap**

- A ULID is 48 timestamp bits plus 80 random bits, written as 26 Crockford Base32 characters.
- Inside one millisecond the random tail breaks the tie, unless one process bumps its own tail.
- UUID version 7 is 48 timestamp bits, a version nibble of 7, 12 bits that some generators use as a local counter, a variant, and 62 random bits.
- That local counter stays inside one process. It does not name a worker, and it is separate from Snowflake's sequence of 4,096.
- Both forms are 16 bytes. The 8-byte key remains a Snowflake id.

![ULID and Other Modern Alternatives](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-6-ulid-and-other-modern-alternatives.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 6.*

## Base62 or Hash

A short code is a few characters that name a long URL. Base62 writes an integer in a 62-character alphabet. A hash path writes a prefix of a digest in that same alphabet.

**Why it exists.** A Snowflake id is a long integer. A link a person will retype needs a shorter public name. The redirect, the cache, and the read path of that product are URL Shortener in [Classic Design Problems](../24_Classic_Design_Problems/). This card is only how the code is chosen. How a stored field grows when the code gets longer stays in [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/).

**How it works.** Every writer uses one alphabet, in one order. This topic uses the 10 digits, then the 26 lowercase letters, then the 26 uppercase letters.

- One character covers 62 codes.
- Two characters cover 62² = 3,844 codes.
- Three characters cover 62³ = 238,328 codes.
- Four characters cover 62⁴ = 14,776,336 codes.

A counter path takes the next integer and encodes it. For 20,000 links, two characters fall short at 3,844, and three characters are enough. The code is unique because the counter was. The service can skip the lookup that asks whether the code is free. In this alphabet, counter 1 encodes as `1` and counter 2 encodes as `2`. The next integer is the next code, so a reader who has seen one link can try the neighbors.

A hash path hashes the destination, or the internal id, and keeps a prefix of the digest written in the same alphabet. A prefix of three characters has the same 238,328 slots and fills them out of order. Two destinations can land on one prefix. The service looks the code up. When another row holds it, the service mixes in a new salt and hashes again, or it keeps one more character, and it checks again. The counter path has no lookup of that kind.

**Trade-offs.** Base64 uses `+`, `/`, and `=`, which need extra escaping in a URL. Base62 leaves those characters out. Base58 also drops characters that look like digits, and the smaller alphabet means the same volume needs more characters. Counter codes stay short and walkable, and they need a shared counter: an auto-increment, a ticket server, or a Snowflake id that you then encode. Hash codes hide the next link only as well as the prefix is long, and each new code costs a read to confirm the slot is free. A public short link can live with a guessable code. An unlisted document needs the hash path, or a random draw of the same width.

**In an interview.** Ask whether a stranger may guess the next code. Public links can use the counter. Unlisted links use a hash or a random code plus a collision check. Compute the width out loud, 62ⁿ against the number of links, and say which path you picked. Leave the redirect, the cache, and the click log in the URL shortener discussion unless the interviewer asks you to switch.

**Recap**

- The alphabet here is 10 digits, 26 lowercase letters, and 26 uppercase letters, in that fixed order.
- Two characters hold 3,844 codes. Three hold 238,328. Twenty thousand links use three characters on the counter path.
- The counter path is unique because the integer was unique. Neighboring integers become neighboring codes.
- A hash prefix of the same length can collide. The service looks it up, then retries with a new salt or one more character.
- The redirect and the cache live with the URL shortener. The choice of code lives here.

![Base62 or Hash](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-7-base62-or-hash.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 7.*

## ID Strategy

The order row, the client's retry key, and the public short code are three different ids. Each one is chosen from the property it has to keep.

**Why it exists.** One scheme that satisfies the strictest job overpays on the others. A version-4 UUID on every order widens the clustered index and scatters inserts. A Snowflake id as a retry name forces the phone to hold a worker number. A three-character base62 counter is the right width for a public link and the wrong width for a global order id.

**How it works.** Match the job, then the scheme.

| Job | Scheme | What you are keeping |
| --- | --- | --- |
| One database still takes every insert | Auto-increment | All four requirements, from a single counter |
| Order or tweet id: time order, 8 bytes, minted on the writer | Snowflake | The full bar, including a local mint |
| The client names a call it may send twice | UUID version 4 | A name the client can mint with no worker number |
| Sortable 16-byte id, no worker registry | ULID or UUID version 7 | Time order at UUID width |
| One sequence, moderate rate, a round trip is fine | Ticket server | Compact integers and one order, until a second server |
| Each primary numbers the rows it stores | Multi-master sequence | Unique integers, no ticket hop, separate per-primary series |
| A few characters in a public URL | Base62 counter, or a hash prefix | A short code. The hash path is the one that looks the code up |

**Trade-offs.** Change one cell and the row changes. Drop the 8-byte limit and a ULID can be the order id. A gapless count of orders is a query over the rows, because these ids leave gaps. A client that must mint the order id while offline can use version 4, and `ORDER BY id` then follows the random bits. Two ticket servers keep uniqueness and give up the single timeline.

**In an interview.** Repeat the requirement, name the scheme, and name the requirement a runner-up would miss. A ULID sorts and is still 16 bytes, so it misses an 8-byte order key. An offset sequence on three primaries stays unique and gives each primary its own series, so the order log has no single timeline. What a repeated client call means is Idempotency in [Networking and Communication](../10_Networking_and_Communication/). Which primary accepts a write is Replication Topologies in [Consistency and Replication](../09_Consistency_and_Replication/). The shortener product is URL Shortener in [Classic Design Problems](../24_Classic_Design_Problems/).

**Recap**

- Use Snowflake for an order or tweet id that is time-ordered, 8 bytes, and minted on the writer.
- Use a UUID for the name a client puts on a call it may send twice.
- Use a ULID or UUID version 7 for a sortable 16-byte id with no worker number.
- Use a ticket server for one moderate sequence that can pay a round trip.
- Use a multi-master offset when each primary numbers its own rows.
- Use Base62, or a hash prefix, for a few characters in a public URL.

![ID Strategy](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id-8-id-strategy.png)

*Source: [`diagrams/unique-id.drawio`](/content/09_System_Design_Interview/19_Unique_ID_Generation/diagrams/unique-id.drawio), page 8.*
