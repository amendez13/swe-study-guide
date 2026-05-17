# Sharding

Sharding distributes data across multiple independent database instances when a single Postgres server can no longer handle the write volume or storage requirements. It's the most complex scaling strategy and should be the last tool you reach for.

## Key Points

- **Horizontal sharding** — rows split across independent instances by a shard key. Each shard handles a fraction of load.
- **Shard key selection** — high cardinality, query-aligned, stable. Most queries should route to a single shard.
- **Consistent hashing** — minimizes data movement when shards are added/removed. Only ~1/N of keys move vs 100% with simple modulo.
- **When to shard** — only when write volume or storage exceeds single-instance capacity. Not for read scaling (use replicas) or single-table size (use partitioning).
- **Citus** — Postgres extension for transparent distributed queries. Coordinator routes to worker shards.
- **FDW** — built-in federated queries to remote Postgres. Manual routing, no distributed transactions.

## Example

```sql
-- Using Citus to shard an orders table by customer_id

-- On the coordinator node:
CREATE TABLE orders (
    id          bigint GENERATED ALWAYS AS IDENTITY,
    customer_id integer NOT NULL,
    total       numeric(10, 2) NOT NULL,
    status      text NOT NULL DEFAULT 'pending',
    created_at  timestamptz NOT NULL DEFAULT now()
);

-- Reference table: small, replicated to all workers
CREATE TABLE customers (
    id   integer PRIMARY KEY,
    name text NOT NULL
);
SELECT create_reference_table('customers');

-- Distributed table: sharded across workers by customer_id
SELECT create_distributed_table('orders', 'customer_id');

-- Single-shard query: fast, routed to one worker
SELECT * FROM orders WHERE customer_id = 42;

-- Cross-shard aggregation: coordinator gathers from all workers
SELECT c.name, count(*) AS order_count, sum(o.total) AS revenue
FROM orders o
JOIN customers c ON c.id = o.customer_id
GROUP BY c.name
ORDER BY revenue DESC LIMIT 10;
```

Citus makes the distributed nature transparent: queries look like standard SQL. The trade-off is that cross-shard queries (those without the shard key in WHERE) require coordination and are slower than single-shard lookups.
