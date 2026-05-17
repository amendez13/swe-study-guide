# Table Partitioning

Partitioning splits a large table into smaller physical segments that Postgres manages transparently. The primary benefits are query performance (partition pruning eliminates irrelevant data), efficient bulk deletion (drop a partition instead of DELETE), and per-partition vacuum/maintenance.

## Key Points

- **Declarative partitioning** — define PARTITION BY on the parent; create child partitions for each range/list/hash bucket. Transparent to queries.
- **Range** — continuous values (dates, IDs). Most common for time-series. FROM is inclusive, TO is exclusive.
- **List** — discrete categorical values. Use a DEFAULT partition to catch new values.
- **Hash** — even distribution across N partitions. Good for spreading writes; doesn't help with dropping old data.
- **Partition pruning** — planner skips irrelevant partitions when the partition key is in the WHERE clause. This is the performance win.
- **When to partition** — hundreds of millions of rows, queries filter on partition key, need to drop old data efficiently. Don't partition small tables or when queries don't filter on the key.

## Example

```sql
-- Time-series event log with monthly range partitions

CREATE TABLE metrics (
    id         bigint GENERATED ALWAYS AS IDENTITY,
    sensor_id  integer NOT NULL,
    value      double precision NOT NULL,
    recorded_at timestamptz NOT NULL
) PARTITION BY RANGE (recorded_at);

-- Create three months of partitions
CREATE TABLE metrics_2024_01 PARTITION OF metrics
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE metrics_2024_02 PARTITION OF metrics
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
CREATE TABLE metrics_2024_03 PARTITION OF metrics
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- Index on the parent applies to all partitions
CREATE INDEX idx_metrics_sensor ON metrics (sensor_id, recorded_at);

-- Query prunes to a single partition
EXPLAIN SELECT avg(value) FROM metrics
WHERE sensor_id = 7 AND recorded_at >= '2024-02-01' AND recorded_at < '2024-03-01';

-- Drop old data instantly (vs DELETE which generates WAL and dead tuples)
DROP TABLE metrics_2024_01;
```

This shows the full lifecycle: create a partitioned parent, add monthly partitions, index across all partitions, demonstrate pruning, and drop old data without expensive DELETE operations.
