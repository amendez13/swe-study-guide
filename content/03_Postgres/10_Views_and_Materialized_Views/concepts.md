## Views

Named SELECT queries stored as definitions, not data. A view executes its underlying query every time you SELECT from it — it's an alias for a query, not a cache.

```sql
CREATE VIEW active_orders AS
SELECT o.id, c.name AS customer, o.total, o.created_at
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'active';

-- Use it like a table
SELECT * FROM active_orders WHERE total > 100;
```

Views provide a stable interface over evolving schemas (rename a column in the table, update the view definition, and downstream queries don't break), hide complexity (join logic lives in the view, not in every query), and enforce access control (GRANT SELECT on the view without exposing the underlying tables).

## Updatable views

Simple views (single table, no aggregates, no DISTINCT, no GROUP BY, no UNION) are automatically updatable — you can INSERT, UPDATE, and DELETE through them.

```sql
CREATE VIEW pending_orders AS
SELECT id, customer_id, total, created_at
FROM orders
WHERE status = 'pending';

-- Direct updates through the view
UPDATE pending_orders SET total = 99.99 WHERE id = 5;
DELETE FROM pending_orders WHERE created_at < '2024-01-01';

-- WITH CHECK OPTION prevents inserts/updates that would disappear from the view
CREATE VIEW pending_orders AS
SELECT id, customer_id, total, created_at
FROM orders
WHERE status = 'pending'
WITH CHECK OPTION;
```

WITH CHECK OPTION ensures that any row inserted or updated through the view still satisfies the view's WHERE clause — preventing "invisible" writes.

## Materialized views

Store query results as physical data on disk. Fast to read (like a table) but stale until explicitly refreshed. Use for expensive queries where slight staleness is acceptable.

```sql
CREATE MATERIALIZED VIEW monthly_revenue AS
SELECT
    date_trunc('month', created_at) AS month,
    COUNT(*) AS order_count,
    SUM(total) AS revenue
FROM orders
GROUP BY 1
ORDER BY 1;

-- Fast: reads pre-computed data
SELECT * FROM monthly_revenue WHERE month >= '2024-01-01';

-- Refresh when you need fresh data (locks out readers)
REFRESH MATERIALIZED VIEW monthly_revenue;
```

Materialized views have no automatic refresh mechanism — you must call REFRESH explicitly, typically via a cron job, application trigger, or after a batch load completes.

## REFRESH MATERIALIZED VIEW CONCURRENTLY

Refreshes a materialized view without blocking concurrent readers. Requires a unique index on the materialized view.

```sql
-- Required: unique index for concurrent refresh
CREATE UNIQUE INDEX idx_monthly_revenue_month ON monthly_revenue (month);

-- Concurrent refresh: readers see old data until refresh completes
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
```

Without CONCURRENTLY, REFRESH takes an exclusive lock — all readers block until it's done. CONCURRENTLY computes the new data, diffs it against the existing data, and applies changes. It's slower to execute but keeps the view available throughout.

## When to use each

Views and materialized views solve different problems. Choosing the wrong one leads to either unnecessary staleness or unnecessary compute.

| Criterion | View | Materialized view |
|-----------|------|-------------------|
| Data freshness | Always current | Stale until refreshed |
| Read speed | Same as underlying query | Pre-computed, fast |
| Storage | Zero (stores only the definition) | Full result set on disk |
| Indexable | No (indexes go on underlying tables) | Yes (create indexes on the materialized view) |
| Use case | Abstraction, access control, simpler queries | Dashboards, reports, expensive aggregations |

Choose a view when the underlying query is fast enough and you need real-time data. Choose a materialized view when the query is expensive (multi-table joins, aggregations over millions of rows) and consumers can tolerate data that's minutes or hours old.
