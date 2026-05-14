## Why Distributed ID Generation Is Hard

In a single-database system, auto-increment gives you unique, sequential IDs. In a distributed system with multiple databases, services, or shards, auto-increment breaks because there's no global counter without coordination.

```text
Requirements for distributed IDs:
  ✓ Globally unique across all nodes and shards
  ✓ Sortable by time (for range queries, feed ordering)
  ✓ High throughput (millions of IDs per second)
  ✓ Low latency (no round-trip to a central service)
  ✓ Compact (fits in 64 bits for efficient indexing)

  Not all approaches satisfy all requirements.
```

## UUID

128-bit universally unique identifier generated without coordination. Version 4 (random) is most common.

```text
Example: 550e8400-e29b-41d4-a716-446655440000

Advantages:
  ✓ No coordination needed — any node generates independently.
  ✓ Extremely low collision probability (2^122 random bits).
  ✓ Simple to implement (built into every language).

Disadvantages:
  ✗ Not sortable by time (random bits, no time component).
  ✗ 128 bits — wastes index space and cache compared to 64-bit IDs.
  ✗ Poor database index locality (random insertion points → B-tree splits).
  ✗ Not human-friendly (hard to read, debug, communicate).
```

UUID is fine for non-indexed or infrequently queried data. For primary keys in a high-throughput database, prefer a time-sortable 64-bit ID.

## Snowflake ID

A 64-bit ID encoding timestamp, datacenter, machine, and sequence number. Designed by Twitter for high-throughput, time-sortable ID generation without central coordination.

```text
Bit layout (Twitter's original):
  1 bit:  unused (sign bit)
  41 bits: millisecond timestamp (from a custom epoch)
           → covers ~69 years
  5 bits:  datacenter ID (up to 32 datacenters)
  5 bits:  machine ID (up to 32 machines per DC)
  12 bits: sequence number (up to 4096 IDs per millisecond per machine)

Result:
  Each machine generates up to 4096 unique IDs per millisecond.
  IDs are roughly time-sorted (same millisecond → same prefix).
  64-bit integer → efficient B-tree indexing.

Example ID: 1541815603606036480
  → Encodes: 2022-06-28T12:00:00Z, DC 1, machine 3, seq 0
```

```text
Advantages:
  ✓ Time-sortable (great for chronological feeds, pagination)
  ✓ 64-bit (half the size of UUID, cache-friendly)
  ✓ No central coordinator (each machine generates independently)
  ✓ ~4M IDs/sec per machine

Disadvantages:
  ✗ Requires synchronized clocks (clock skew → out-of-order IDs)
  ✗ Datacenter and machine IDs must be assigned centrally (once)
  ✗ Custom epoch means IDs aren't comparable across systems
```

Snowflake is the go-to answer for "design a distributed unique ID generator" in interviews.

## Ticket Server

A centralized (or sharded) auto-increment service. A dedicated database hands out sequential IDs.

```text
Single ticket server:
  ID service backed by a single DB with auto-increment.
  Application calls ID service → gets next ID → uses it.

  + Simple, sequential, no gaps.
  - Single point of failure.
  - Throughput limited to one DB's write capacity.

Sharded ticket servers (Flickr approach):
  Two servers with different step sizes:
    Server A: 1, 3, 5, 7, 9, ...  (start=1, step=2)
    Server B: 2, 4, 6, 8, 10, ... (start=2, step=2)

  + Eliminates single point of failure.
  + Doubles throughput.
  - IDs are not globally sorted by time (server A and B interleave).
  - Adding a third server requires changing the step size.
```

Ticket servers work for moderate scale. For Twitter/Meta-scale (millions of IDs per second), Snowflake or ULID is better.

## ULID and Other Modern Alternatives

Newer ID formats that improve on UUID and Snowflake for specific use cases.

```text
ULID (Universally Unique Lexicographically Sortable Identifier):
  128 bits: 48-bit timestamp (ms) + 80-bit random
  Encoded as 26-character Crockford Base32 string.
  Example: 01ARZ3NDEKTSV4RRFFQ69G5FAV

  ✓ Time-sortable (first 48 bits are timestamp)
  ✓ No coordination needed (random component)
  ✓ Lexicographically sortable as strings
  ✗ 128 bits (same size as UUID)

UUID v7 (proposed standard):
  128 bits with a Unix timestamp prefix.
  Time-sortable UUID that's compatible with UUID infrastructure.

Comparison:
  UUID v4:   128-bit, random, not sortable
  ULID:      128-bit, time + random, sortable
  Snowflake: 64-bit, time + machine + seq, sortable, needs config
  UUID v7:   128-bit, time + random, sortable, UUID-compatible
```

## Choosing an ID Strategy

A decision framework for system design interviews.

```text
Need time-sortable 64-bit IDs at massive scale?
  → Snowflake (or similar: Instagram's approach, Sonyflake)

Need unique IDs without any coordination or pre-configuration?
  → UUID v4 (or ULID/UUID v7 if sortability matters)

Need sequential, gap-free IDs at moderate scale?
  → Ticket server (single or sharded)

Need human-readable short IDs (URL shortener)?
  → Counter-based with Base62 encoding, or hash-based

The answer in most interviews:
  "Snowflake-style IDs for database primary keys,
   UUIDs for idempotency keys and external references."
```
