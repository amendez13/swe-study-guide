# VACUUM and Maintenance

MVCC's trade-off is dead tuples: old row versions that accumulate after updates and deletes. VACUUM reclaims this space, ANALYZE keeps planner statistics fresh, and autovacuum automates both. Neglecting maintenance leads to table bloat, degraded query performance, and eventually transaction ID wraparound.

## Key Points

- **Dead tuples** — old row versions left by UPDATE/DELETE. Cause bloat, slow scans, and wasted I/O until vacuumed.
- **VACUUM** — reclaims dead tuple space for reuse. Runs concurrently (no lock). Does not shrink files on disk.
- **VACUUM FULL** — rewrites the table, returns space to OS. Requires exclusive lock — offline operation.
- **Autovacuum** — background daemon that triggers vacuum/analyze when dead tuples exceed thresholds. Tune aggressiveness; don't disable.
- **ANALYZE** — updates planner statistics. Run after bulk loads or schema changes for immediate fresh stats.
- **REINDEX** — rebuilds bloated indexes. Use CONCURRENTLY in production.
- **pg_stat_user_tables** — monitor dead tuples, last vacuum timestamps, and maintenance health.

## Example

```sql
-- Check maintenance health across all tables
SELECT
    relname,
    n_live_tup,
    n_dead_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 1) AS dead_pct,
    last_autovacuum,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Tune autovacuum for a high-write table
ALTER TABLE events SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_vacuum_threshold = 200,
    autovacuum_analyze_scale_factor = 0.02
);

-- Manual vacuum + analyze after a large bulk operation
VACUUM ANALYZE events;

-- Rebuild a bloated index without locking writes
REINDEX INDEX CONCURRENTLY idx_events_created;

-- Monitor progress of a running vacuum (PG 9.6+)
SELECT * FROM pg_stat_progress_vacuum;
```

This shows the monitoring → tuning → manual intervention workflow: identify tables with high dead tuple ratios, adjust per-table autovacuum settings for hot tables, run manual maintenance after bulk operations, and use CONCURRENTLY for production index rebuilds.
