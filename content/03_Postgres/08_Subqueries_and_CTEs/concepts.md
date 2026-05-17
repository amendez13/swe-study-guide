## Scalar subquery

Returns a single value. Usable anywhere a single expression is expected: in SELECT lists, WHERE conditions, or as a computed column value.

```sql
-- In WHERE: books priced above the average
SELECT title, price FROM books
WHERE price > (SELECT AVG(price) FROM books);

-- In SELECT: add a computed column
SELECT
    title,
    price,
    price - (SELECT AVG(price) FROM books) AS diff_from_avg
FROM books;
```

If a scalar subquery returns more than one row, Postgres raises an error. If it returns zero rows, the result is NULL. The planner can often evaluate scalar subqueries once and cache the result if they don't reference the outer query.

## Subquery in FROM (derived table)

A subquery in the FROM clause produces a virtual table that exists only for the duration of the query. Must be aliased.

```sql
-- Pre-aggregate, then filter
SELECT category, avg_price
FROM (
    SELECT category, AVG(price) AS avg_price
    FROM products
    GROUP BY category
) AS category_stats
WHERE avg_price > 50
ORDER BY avg_price DESC;
```

Derived tables are useful when you need to filter on an aggregate (an alternative to HAVING) or when you want to join against a computed result set. The planner often flattens simple derived tables into the outer query, so there's no inherent performance penalty.

## Correlated subquery

References columns from the outer query, causing it to be re-evaluated for every outer row. Can be expensive on large tables but is sometimes the clearest way to express a condition.

```sql
-- For each customer, find their most recent order
SELECT c.name, (
    SELECT MAX(o.created_at)
    FROM orders o
    WHERE o.customer_id = c.id
) AS last_order_date
FROM customers c;

-- Equivalent to a lateral join (often clearer for multiple columns)
SELECT c.name, latest.created_at
FROM customers c
LEFT JOIN LATERAL (
    SELECT created_at FROM orders WHERE customer_id = c.id
    ORDER BY created_at DESC LIMIT 1
) AS latest ON true;
```

The planner sometimes converts correlated subqueries into joins internally. If performance is poor, try rewriting as an explicit JOIN or using a window function.

## EXISTS and NOT EXISTS

Tests whether a subquery returns any rows. EXISTS returns true as soon as the first matching row is found — it short-circuits, making it efficient even against large tables.

```sql
-- Customers who have placed at least one order
SELECT c.name FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- Customers who have never ordered (anti-join)
SELECT c.name FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);
```

EXISTS vs IN for the same logic:
- EXISTS short-circuits — it stops at the first match
- `IN (subquery)` materializes the entire result set, then checks membership
- NOT EXISTS handles NULLs correctly; `NOT IN` with NULLs in the subquery returns no rows (a common bug)

Prefer EXISTS/NOT EXISTS for anti-joins and when the subquery might return many rows.

## Common Table Expressions (CTEs)

`WITH ... AS (...)` blocks that name a subquery for readability and reuse. In Postgres 12+, the planner can inline non-recursive CTEs (optimizing them like subqueries). In older versions, CTEs are always materialized (optimization fences).

```sql
WITH monthly_revenue AS (
    SELECT
        date_trunc('month', created_at) AS month,
        SUM(total) AS revenue
    FROM orders
    WHERE created_at >= '2024-01-01'
    GROUP BY 1
),
growth AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month) AS prev_revenue
    FROM monthly_revenue
)
SELECT
    month,
    revenue,
    ROUND((revenue - prev_revenue) / prev_revenue * 100, 1) AS growth_pct
FROM growth
WHERE prev_revenue IS NOT NULL;
```

CTEs improve readability by giving intermediate result sets meaningful names. Use them when a query has multiple logical steps or when you reference the same subquery more than once.

## Recursive CTEs

`WITH RECURSIVE` for traversing hierarchical or graph data: org charts, category trees, bill-of-materials, shortest paths. Composed of a base case UNION ALL'd with a recursive step.

```sql
-- Traverse an org chart: find all reports (direct and indirect) under manager 1
WITH RECURSIVE reports AS (
    -- Base case: direct reports
    SELECT id, name, manager_id, 1 AS depth
    FROM employees
    WHERE manager_id = 1

    UNION ALL

    -- Recursive step: reports of reports
    SELECT e.id, e.name, e.manager_id, r.depth + 1
    FROM employees e
    JOIN reports r ON e.manager_id = r.id
)
SELECT id, name, depth FROM reports ORDER BY depth, name;
```

The recursive step runs repeatedly until it produces no new rows. Add a `WHERE depth < N` or `LIMIT` to prevent infinite loops on cyclic data. For cycle detection in graphs, Postgres 14+ offers `CYCLE` clause:

```sql
WITH RECURSIVE ... CYCLE id SET is_cycle USING path
```
