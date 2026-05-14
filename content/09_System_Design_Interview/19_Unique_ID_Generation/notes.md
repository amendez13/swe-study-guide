# Unique ID Generation

How to generate globally unique identifiers in a distributed system where there's no single auto-increment counter. This is both a standalone interview question and a building block for any system that needs unique keys across multiple services or shards.

## Key Points

- **The problem** — auto-increment breaks when you have multiple databases or shards. Distributed IDs need uniqueness, sortability, high throughput, and compactness.
- **UUID** — 128-bit random ID. No coordination, but not sortable, wastes index space, and causes poor B-tree locality.
- **Snowflake ID** — 64-bit: timestamp + datacenter + machine + sequence. Time-sortable, no coordinator needed, ~4M IDs/sec per machine. The default interview answer.
- **Ticket server** — centralized auto-increment service. Simple and sequential, but SPOF. Sharded variant (Flickr) trades strict ordering for availability.
- **ULID / UUID v7** — 128-bit with timestamp prefix for sortability. Good when you want UUID compatibility with time ordering.
- **Choosing** — Snowflake for primary keys at scale, UUID for idempotency keys, ticket server for sequential IDs at moderate scale.

## Example

Designing the ID strategy for a social media platform:

```text
Posts:
  Snowflake ID (64-bit)
  Why: billions of posts, need time-sorted feeds, efficient indexing.
  Feed query: SELECT * FROM posts WHERE user_id = X ORDER BY id DESC LIMIT 20
  → Snowflake IDs are time-sorted, so ORDER BY id = ORDER BY time. ✓

Idempotency keys (for create-post API):
  UUID v4 (128-bit)
  Why: client generates it, no coordination, used only for dedup.
  POST /posts  Idempotency-Key: 550e8400-e29b-41d4-...

Short URLs (for sharing):
  Counter + Base62
  Why: human-readable, short. Counter from ticket server or Snowflake.
  Post ID 738291 → Base62 → "3d7H"
  Share link: https://social.app/p/3d7H

Direct message IDs:
  Snowflake ID within each conversation partition.
  Partitioned by conversation_id, so IDs are conversation-local.
  Messages within a conversation are strictly ordered by ID.
```
