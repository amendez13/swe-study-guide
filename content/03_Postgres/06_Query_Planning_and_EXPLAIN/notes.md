# Query Planning and EXPLAIN

Understanding how Postgres chooses a query plan is the key to performance tuning. The planner estimates costs for different execution strategies and picks the cheapest one — but it can only be as good as its statistics. EXPLAIN is how you see what it chose and why.

## Key Points

- **Query pipeline** — parser → rewriter → planner → executor. The planner is the performance-critical stage.
- **EXPLAIN** — shows the planned strategy without running the query. Displays cost estimates and expected row counts.
- **EXPLAIN ANALYZE** — runs the query and shows actual times and rows. Add BUFFERS to see I/O hits vs disk reads.
- **Scan nodes** — Sequential Scan (full table), Index Scan (index + heap fetch), Index Only Scan (index alone), Bitmap Scan (medium selectivity).
- **Cost model** — startup cost (before first row) vs total cost (all rows). Costs are based on seq_page_cost and random_page_cost settings.
- **Join strategies** — Nested Loop (small outer + indexed inner), Hash Join (equality, larger sets), Merge Join (pre-sorted inputs).
- **Statistics** — the planner uses `pg_statistic` to estimate row counts. Run ANALYZE after large data changes. Bad stats cause bad plans.

## Example

```sql
-- Create a table and load data
CREATE TABLE events (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id    integer NOT NULL,
    event_type text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_events_user ON events (user_id);
CREATE INDEX idx_events_date ON events (created_at);

-- After loading data, update statistics
ANALYZE events;

-- Diagnose a query: see what plan the planner chose and whether estimates match
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT user_id, count(*) AS event_count
FROM events
WHERE created_at > now() - interval '7 days'
GROUP BY user_id
ORDER BY event_count DESC
LIMIT 10;
```

Read the output bottom-up: the Index Scan on `created_at` feeds into a HashAggregate (GROUP BY), then a Sort (ORDER BY), then a Limit. Compare estimated rows to actual rows at each node — large discrepancies point to stale statistics or correlated columns.
