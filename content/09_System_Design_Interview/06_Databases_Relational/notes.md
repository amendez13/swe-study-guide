# Databases — Relational

Relational databases are the default storage choice in system design interviews when data is structured and consistency matters. Understanding their scaling levers — indexing, replication, denormalization, and sharding — is essential because most interview problems start with "use a relational database" and then ask how to scale it.

## Key Points

- **Relational database** — tables, fixed schemas, SQL, foreign keys. Choose when data is structured, relationships matter, and you need ACID guarantees.
- **ACID** — Atomicity (all-or-nothing), Consistency (valid state transitions), Isolation (concurrent transactions don't interfere), Durability (committed data survives crashes).
- **Normalization vs. denormalization** — normalize to eliminate redundancy and maintain integrity; denormalize specific read paths when join cost becomes a bottleneck.
- **Indexing** — B-trees for range + equality queries, hash indexes for equality-only. Composite indexes must be queried by leftmost prefix. Every index slows writes.
- **Replication** — leader-follower for read scaling, multi-leader for multi-region writes, leaderless for no write SPOF. Replication lag is the primary trade-off.
- **Sharding** — split data by shard key across instances. Hash-based for even distribution, range-based for efficient range queries. Last resort after read replicas and caching.
- **Read replicas** — the first scaling step for read-heavy workloads. Route writes to leader, reads to replicas. Handle replication lag with read-after-write from leader.

## Example

Scaling a relational database for an e-commerce product catalog:

```text
Requirements:
  10M products, 50,000 reads/sec (searches, product pages)
  500 writes/sec (price updates, new listings)
  Read:Write ratio = 100:1

Step 1: Indexing
  CREATE INDEX idx_products_category ON products(category_id);
  CREATE INDEX idx_products_search ON products USING gin(to_tsvector(name));
  → Reduces query latency from 200ms to 5ms.

Step 2: Read replicas
  1 leader + 3 read replicas.
  Reads distributed across replicas: 50,000 / 3 ≈ 17,000 QPS each.
  Leader handles 500 writes/sec (well within capacity).

Step 3: Cache hot products
  Redis cache for top 100K most-viewed products.
  Cache hit rate ~90% → DB read load drops to ~5,000 QPS.

Step 4 (if needed): Denormalize search results
  Materialized view with product name, price, image URL, rating.
  Single-table scan, no joins for search result pages.

Sharding: NOT needed yet.
  500 writes/sec and 10M rows fits comfortably in one leader.
  Shard only if storage exceeds single-server capacity or
  write QPS grows 10×.
```

The scaling sequence — indexes → replicas → cache → denormalization → sharding — is the standard progression for relational databases.
