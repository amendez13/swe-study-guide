# Query Optimization

Placeholder notes for Postgres query optimization.

## Key Points

- The query planner chooses between sequential scan, index scan, and bitmap scan based on statistics
- `ANALYZE` updates planner statistics; `VACUUM` reclaims dead tuples
- CTEs (`WITH`) are optimization fences in older Postgres; use subqueries for inline optimization
- `pg_stat_statements` tracks slow queries across the server

## Example

```sql
-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```
