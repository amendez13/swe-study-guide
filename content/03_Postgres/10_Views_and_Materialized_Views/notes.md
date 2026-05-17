# Views and Materialized Views

Views abstract complex queries behind a simple name; materialized views trade freshness for speed by caching query results on disk. Together they let you build stable, performant interfaces over schemas that evolve underneath.

## Key Points

- **Views** — stored query definitions, not data. Always return current results. Zero storage cost.
- **Updatable views** — simple single-table views support INSERT/UPDATE/DELETE. Use WITH CHECK OPTION to enforce the view's filter on writes.
- **Materialized views** — store computed results. Fast reads but stale until refreshed. Can be indexed like tables.
- **REFRESH CONCURRENTLY** — non-blocking refresh. Requires a unique index. Readers see old data until the refresh completes.
- **When to use each** — views for abstraction and access control; materialized views for expensive aggregations where staleness is acceptable.

## Example

```sql
-- Materialized view for a dashboard: total orders and revenue per product category

CREATE MATERIALIZED VIEW category_stats AS
SELECT
    p.category,
    COUNT(DISTINCT o.id)   AS order_count,
    SUM(li.quantity)       AS units_sold,
    SUM(li.price * li.quantity) AS revenue
FROM line_items li
JOIN products p ON p.id = li.product_id
JOIN orders o ON o.id = li.order_id
WHERE o.status = 'completed'
GROUP BY p.category;

-- Index for fast lookups and to enable CONCURRENTLY
CREATE UNIQUE INDEX idx_cat_stats_category ON category_stats (category);

-- Dashboard query: instant, no multi-table join at read time
SELECT * FROM category_stats ORDER BY revenue DESC;

-- Refresh after nightly batch completes
REFRESH MATERIALIZED VIEW CONCURRENTLY category_stats;
```

The materialized view pre-computes an expensive three-table join with aggregations. The dashboard reads from the materialized view (fast index scan) and a cron job refreshes it after new data lands.
