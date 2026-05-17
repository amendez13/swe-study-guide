## Declarative partitioning

Split a large table into smaller physical partitions that Postgres manages transparently. Queries and inserts work against the parent table; Postgres routes rows to the correct partition automatically.

```sql
CREATE TABLE events (
    id         bigint GENERATED ALWAYS AS IDENTITY,
    event_type text NOT NULL,
    payload    jsonb NOT NULL,
    created_at timestamptz NOT NULL
) PARTITION BY RANGE (created_at);

-- Partitions are separate physical tables
CREATE TABLE events_2024_q1 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
CREATE TABLE events_2024_q2 PARTITION OF events
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
```

Introduced in Postgres 10, improved each release. Indexes and constraints defined on the parent are automatically applied to each partition. The parent table itself stores no data.

## Range partitioning

Partition by a continuous value range — most commonly dates or sequential IDs. The standard choice for time-series data.

```sql
-- Monthly partitions for a log table
CREATE TABLE access_logs (
    id         bigint GENERATED ALWAYS AS IDENTITY,
    path       text NOT NULL,
    status     integer NOT NULL,
    created_at timestamptz NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE access_logs_2024_01 PARTITION OF access_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE access_logs_2024_02 PARTITION OF access_logs
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- ... create future partitions ahead of time or automate via pg_partman
```

The FROM bound is inclusive, the TO bound is exclusive. Rows that don't fit any partition cause an error — always create partitions ahead of time or use a default partition.

## List partitioning

Partition by a discrete set of values. Use when queries naturally filter by a categorical column with a known set of values.

```sql
CREATE TABLE orders (
    id         bigint GENERATED ALWAYS AS IDENTITY,
    region     text NOT NULL,
    total      numeric(10, 2) NOT NULL,
    created_at timestamptz NOT NULL
) PARTITION BY LIST (region);

CREATE TABLE orders_us PARTITION OF orders FOR VALUES IN ('us-east', 'us-west');
CREATE TABLE orders_eu PARTITION OF orders FOR VALUES IN ('eu-west', 'eu-central');
CREATE TABLE orders_ap PARTITION OF orders FOR VALUES IN ('ap-southeast', 'ap-northeast');

-- Default partition catches any unlisted value
CREATE TABLE orders_other PARTITION OF orders DEFAULT;
```

List partitioning works well when the set of values is small and stable. If the set grows frequently, consider hash partitioning instead.

## Hash partitioning

Distribute rows evenly across N partitions by hashing a column value. Use when no natural range or list exists but you still want to spread a large table across smaller segments.

```sql
CREATE TABLE sessions (
    id      uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id integer NOT NULL,
    data    jsonb NOT NULL
) PARTITION BY HASH (id);

CREATE TABLE sessions_p0 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sessions_p1 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE sessions_p2 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE sessions_p3 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

Hash partitioning provides even data distribution but doesn't enable dropping old data by partition (unlike range). It's useful for parallel query execution and reducing lock contention on high-write tables.

## Partition pruning

The planner automatically skips partitions that cannot contain matching rows. This is what makes partitioning beneficial for query performance.

```sql
-- Only scans the Q1 partition
EXPLAIN SELECT * FROM events WHERE created_at = '2024-02-15 10:00+00';
-- Seq Scan on events_2024_q1 (other partitions pruned)

-- Scans all partitions (no filter on partition key)
EXPLAIN SELECT * FROM events WHERE event_type = 'click';
-- Append → Seq Scan on events_2024_q1 + Seq Scan on events_2024_q2 + ...
```

Pruning only works when the partition key appears in the WHERE clause with a constant or parameter. Without it, Postgres must scan all partitions. This is why the partition key should match your most common query filter.

## When to partition

Partitioning adds complexity (partition management, routing, cross-partition constraints). It's worth it only when the benefits outweigh this cost.

**Partition when:**
- Tables have hundreds of millions of rows
- Queries naturally filter on the partition key (date ranges, regions)
- You need to efficiently drop old data (`DROP TABLE events_2023_q1` instead of DELETE)
- Vacuum performance on the full table is problematic

**Don't partition when:**
- The table has fewer than ~10 million rows (indexes alone suffice)
- Queries don't filter on the partition key (all partitions scanned anyway)
- You'd need more than ~100 partitions (planner overhead increases)
- You're partitioning "just in case" without a demonstrated need

The `pg_partman` extension automates partition creation and maintenance for time-based partitioning schemes.
