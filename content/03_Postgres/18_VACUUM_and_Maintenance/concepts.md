## Dead tuples and bloat

MVCC leaves old row versions behind after updates and deletes. These dead tuples consume space, slow sequential scans, and bloat indexes until they are vacuumed.

```sql
-- See dead tuple count for a table
SELECT relname, n_live_tup, n_dead_tup,
       ROUND(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 1) AS dead_pct
FROM pg_stat_user_tables
WHERE relname = 'orders';
```

An UPDATE in Postgres creates a new tuple and marks the old one as dead (sets `xmax`). A DELETE marks the tuple as dead without creating a new one. Neither operation reclaims space immediately — that's VACUUM's job.

High dead tuple ratios cause: larger table size on disk, more pages to scan for sequential operations, slower index lookups (indexes point to dead tuples that must be skipped), and increased I/O.

## VACUUM

Reclaims space from dead tuples and updates the visibility map. Does not return space to the OS or shrink the file on disk — it marks pages as available for reuse by future inserts.

```sql
-- Vacuum a specific table
VACUUM orders;

-- Vacuum with verbose output to see what happened
VACUUM VERBOSE orders;
-- INFO: "orders": removed 15023 dead row versions in 412 pages
-- INFO: "orders": found 15023 removable row versions in 850 pages

-- VACUUM FULL: rewrites the entire table, returns space to OS
-- WARNING: takes an exclusive lock for the duration!
VACUUM FULL orders;
```

Regular VACUUM runs concurrently (no lock), is lightweight, and should happen frequently. VACUUM FULL is an offline operation that rewrites the table and compacts it — use only when bloat is severe and you can afford the downtime.

## Autovacuum

A background process that automatically vacuums and analyzes tables based on configurable thresholds. It monitors dead tuple accumulation and triggers vacuum when a table exceeds its threshold.

```sql
-- Default trigger: vacuum when dead tuples > (threshold + scale_factor * live_tuples)
-- Default: 50 + 0.2 * live_tuples

-- Check autovacuum activity
SELECT relname, last_autovacuum, last_autoanalyze, autovacuum_count
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;

-- Tune per-table for hot tables
ALTER TABLE events SET (
    autovacuum_vacuum_scale_factor = 0.05,    -- trigger at 5% dead (vs default 20%)
    autovacuum_vacuum_threshold = 100,
    autovacuum_analyze_scale_factor = 0.02
);
```

Autovacuum should rarely be disabled. If it's "too slow," tune it to be more aggressive (more workers, lower thresholds, less sleep between rounds) rather than turning it off. Disabled autovacuum leads to transaction ID wraparound — a critical failure mode.

## ANALYZE

Updates table statistics in `pg_statistic` so the query planner makes good cost estimates. Without current statistics, the planner may choose sequential scans over index scans or wrong join strategies.

```sql
-- Analyze a specific table
ANALYZE orders;

-- Analyze specific columns (useful for very wide tables)
ANALYZE orders (customer_id, status, created_at);

-- Check when stats were last updated
SELECT relname, last_analyze, last_autoanalyze
FROM pg_stat_user_tables;
```

Run ANALYZE manually after: bulk INSERTs/COPY, large DELETEs, schema changes that add columns, or any operation that significantly changes the data distribution. Autovacuum also runs ANALYZE periodically, but a manual run after a big load gives the planner fresh stats immediately.

## REINDEX

Rebuilds an index from scratch. Necessary when index bloat accumulates (dead entries from updated/deleted rows) and the index becomes much larger than the live data justifies.

```sql
-- Rebuild a specific index
REINDEX INDEX idx_orders_customer;

-- Rebuild all indexes on a table
REINDEX TABLE orders;

-- Non-blocking rebuild (Postgres 12+)
REINDEX INDEX CONCURRENTLY idx_orders_customer;
```

Index bloat is harder to detect than table bloat. Compare the index size to what a fresh build would produce:

```sql
-- Estimate index bloat using pgstattuple extension
CREATE EXTENSION pgstattuple;
SELECT * FROM pgstatindex('idx_orders_customer');
-- avg_leaf_density < 50% suggests significant bloat
```

REINDEX CONCURRENTLY (like CREATE INDEX CONCURRENTLY) doesn't lock the table for writes. Use it in production.

## `pg_stat_user_tables`

The primary system view for monitoring table maintenance health. Shows vacuum counts, dead tuples, and timestamps of the last vacuum/analyze operations.

```sql
SELECT
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;
```

Key metrics to monitor:
- `n_dead_tup` — tables with high counts need more aggressive vacuum
- `last_autovacuum` — NULL or very old timestamps indicate autovacuum is not keeping up
- ratio of `n_dead_tup` to `n_live_tup` — above 20% suggests vacuum is falling behind

Pair with `pg_stat_user_indexes` to find unused indexes (which waste write performance) and `pg_stat_activity` to spot long-running transactions that block vacuum.
