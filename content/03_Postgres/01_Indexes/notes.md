# Indexes

Placeholder notes for Postgres Indexes.

## Key Points

- Default index type is B-tree, suitable for equality and range queries
- GIN indexes support full-text search and JSONB containment queries
- Partial indexes index only rows matching a WHERE clause, reducing size
- `EXPLAIN ANALYZE` shows whether an index is being used and actual cost

## Example

```sql
-- Partial index: only index active users
CREATE INDEX idx_users_email_active ON users(email)
WHERE active = true;

-- Check query plan
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'alex@example.com' AND active = true;
```
