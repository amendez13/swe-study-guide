# SQL Fundamentals

The core DML operations that make up nearly every interaction with a PostgreSQL database. Mastering these statements — and understanding the logical execution order behind them — is the prerequisite for everything from query optimization to schema design.

## Key Points

- **SELECT, INSERT, UPDATE, DELETE** — the four CRUD verbs. Every statement runs inside a transaction, even without an explicit BEGIN.
- **WHERE** — filters rows before aggregation. NULL requires IS NULL / IS NOT NULL checks; equality operators don't match NULL.
- **ORDER BY, LIMIT, OFFSET** — controls result ordering and pagination. OFFSET degrades on deep pages; keyset pagination scales better.
- **JOINs** — combine tables. INNER returns only matches; LEFT keeps all left rows; FULL keeps everything. RIGHT is just a flipped LEFT.
- **GROUP BY and aggregates** — collapse rows into groups with summary values. Every selected column must be grouped or aggregated.
- **HAVING** — filters groups after aggregation, where WHERE cannot reach.
- **DISTINCT and set operations** — deduplicate results or combine/compare two query result sets (UNION, INTERSECT, EXCEPT).
- **Subqueries** — nest a SELECT inside WHERE, FROM, or SELECT. EXISTS short-circuits and is usually the fastest anti-join pattern.

## Example

```sql
-- "Top 3 customers by total spend who have more than 2 orders"
-- Exercises: JOIN, GROUP BY, aggregates, HAVING, ORDER BY, LIMIT

SELECT
    c.name,
    COUNT(*)       AS order_count,
    SUM(o.total)   AS total_spent
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.status != 'cancelled'
GROUP BY c.id, c.name
HAVING COUNT(*) > 2
ORDER BY total_spent DESC
LIMIT 3;
```

This single query touches most of the topic: it joins two tables, filters with WHERE (before grouping), groups and aggregates, filters groups with HAVING, orders the result, and limits output. The logical execution order is FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT.
