# Data Partitioning and Consistent Hashing

How to split data across multiple machines when a single database can't hold it all or handle the write load. Partitioning is the scaling strategy of last resort for databases — after indexing, caching, and read replicas — but it's a core concept in almost every system design interview because interviewers test at scales that require it.

## Key Points

- **Sharding** — split rows across database instances by partition key. Scales writes and storage but complicates cross-shard queries and transactions.
- **Shard key choice** — the most critical partitioning decision. Must distribute evenly and align with query patterns. Bad keys create hotspots.
- **Range partitioning** — contiguous key ranges per shard. Efficient range queries, but prone to hotspots with non-uniform data.
- **Hash partitioning** — `hash(key) % N` for even distribution. No range query support. Changing N rehashes everything unless you use consistent hashing.
- **Consistent hashing** — keys and servers on a ring. Adding/removing a node only moves ~1/N of keys. Used in DynamoDB, Cassandra, Memcached.
- **Virtual nodes** — each physical node maps to many ring positions. Fixes uneven distribution and makes rebalancing smoother.
- **Rebalancing** — redistributing data when the cluster changes. Fixed partitions, dynamic splitting, or consistent hashing with vnodes.
- **Request routing** — client-side (knows the map), proxy tier (extra hop but simple clients), or gossip-based (any node forwards).

## Example

Designing a sharding strategy for a chat message store:

```text
Requirements:
  1B messages/day, 5 years retention
  Primary query: "get messages for chat_id X, ordered by time"
  Secondary query: "get all chats for user_id Y"

Shard key analysis:
  message_id — even distribution, but "get messages for chat X"
               would scatter across all shards. Bad.
  user_id    — even distribution, but group chats have multiple
               users, so the same chat's messages live on
               different shards. Bad for the primary query.
  chat_id    — all messages for a chat are co-located.
               Primary query hits one shard. Good!

  Concern: celebrity group chats could create hotspots.
  Mitigation: monitor shard sizes, split hot partitions.

Chosen strategy:
  Hash partitioning on chat_id.
  256 fixed partitions across 8 shards (32 per shard).
  Adding a 9th shard moves ~32 partitions, no data re-hashing.

  Primary query: hash(chat_id) → single shard, range scan by time.
  Secondary query: maintain a user_id → [chat_ids] lookup table
                   (separate, small, fits in one node or cache).
```

The pattern is: optimize the partition key for the dominant query, then solve secondary queries with a separate lookup or index.
