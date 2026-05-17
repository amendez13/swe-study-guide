## SELECT, INSERT, UPDATE, DELETE

The four CRUD operations that account for nearly every data-manipulation statement you'll write. DDL (CREATE, ALTER, DROP) changes structure; DML changes data.

```sql
-- Read
SELECT title, price FROM books WHERE price > 20;

-- Create
INSERT INTO books (title, price) VALUES ('DDIA', 45.00);

-- Update
UPDATE books SET price = 39.99 WHERE title = 'DDIA';

-- Delete
DELETE FROM books WHERE title = 'DDIA';
```

Every statement runs inside a transaction (implicit single-statement transaction if you don't explicitly BEGIN). A failed statement rolls back automatically in this implicit mode.

## WHERE clause

Filters rows before they reach the result set. Without WHERE, a SELECT returns every row in the table; an UPDATE or DELETE affects every row.

```sql
-- Comparison and boolean combinators
SELECT * FROM orders
WHERE status = 'shipped'
  AND total > 100
  AND created_at > '2024-01-01';

-- IN for set membership
SELECT * FROM products WHERE category IN ('books', 'electronics');

-- Pattern matching
SELECT * FROM customers WHERE email LIKE '%@gmail.com';

-- NULL checks (= does not work for NULL)
SELECT * FROM users WHERE deleted_at IS NULL;
```

Common mistake: `WHERE status != 'active'` does not match rows where `status` is NULL. NULL is not equal to anything, including itself. Use `IS DISTINCT FROM` if you need NULL-safe inequality.

## ORDER BY, LIMIT, OFFSET

Controls result ordering and pagination. Without ORDER BY, Postgres makes no guarantee about row order — even if rows happened to come back sorted last time.

```sql
-- Sort by price descending, break ties alphabetically
SELECT title, price FROM books
ORDER BY price DESC, title ASC
LIMIT 20 OFFSET 40;
```

OFFSET-based pagination degrades on large tables because Postgres must scan and discard all skipped rows. For deep pages, prefer keyset (cursor-based) pagination:

```sql
-- Keyset pagination: "give me the next 20 after this ID"
SELECT id, title, price FROM books
WHERE id > 1042
ORDER BY id
LIMIT 20;
```

The keyset approach uses an indexed column (here `id`) so the database can seek directly to the starting point instead of scanning from the beginning.

## JOINs (INNER, LEFT, RIGHT, FULL, CROSS)

Combine rows from multiple tables based on a related column. The join type controls what happens when a row on one side has no match on the other.

```sql
-- INNER: only rows with matches on both sides
SELECT o.id, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id;

-- LEFT: all orders, even those with no customer (customer columns NULL)
SELECT o.id, c.name
FROM orders o
LEFT JOIN customers c ON c.id = o.customer_id;

-- CROSS: every combination (rarely intentional with real data)
SELECT s.name, c.color
FROM sizes s CROSS JOIN colors c;
```

| Join type | Unmatched left row | Unmatched right row |
|-----------|-------------------|---------------------|
| INNER | Excluded | Excluded |
| LEFT | Kept (right cols NULL) | Excluded |
| RIGHT | Excluded | Kept (left cols NULL) |
| FULL | Kept (right cols NULL) | Kept (left cols NULL) |

In practice, INNER and LEFT cover 95% of cases. If you're reaching for a RIGHT JOIN, swapping the table order and using LEFT is usually clearer.

## GROUP BY and aggregate functions

Collapses rows into groups and computes summary values per group. Every column in the SELECT must either appear in GROUP BY or be wrapped in an aggregate function.

```sql
-- Total revenue per customer
SELECT customer_id, COUNT(*) AS order_count, SUM(total) AS revenue
FROM orders
GROUP BY customer_id
ORDER BY revenue DESC;
```

The core aggregates:

| Function | Returns |
|----------|---------|
| `COUNT(*)` | Number of rows in the group |
| `COUNT(col)` | Non-NULL values in that column |
| `SUM(col)` | Total of numeric values |
| `AVG(col)` | Mean (returns numeric, not integer) |
| `MIN(col)` / `MAX(col)` | Smallest / largest value |

`COUNT(DISTINCT col)` counts unique values. Combining aggregates in one query avoids multiple table scans.

## HAVING

Filters groups after aggregation — the GROUP BY equivalent of WHERE for individual rows. You cannot reference aggregates in a WHERE clause because WHERE runs before grouping.

```sql
-- Customers who have placed more than 5 orders
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
HAVING COUNT(*) > 5;
```

Execution order: FROM → WHERE (filter rows) → GROUP BY (form groups) → HAVING (filter groups) → SELECT (compute output) → ORDER BY → LIMIT.

A common mistake is putting aggregate conditions in WHERE instead of HAVING, which produces a syntax error.

## DISTINCT and set operations

DISTINCT eliminates duplicate rows from a result set. Set operations combine the results of two queries.

```sql
-- Remove duplicate rows
SELECT DISTINCT city FROM customers;

-- UNION: combine results, remove duplicates
SELECT name FROM employees
UNION
SELECT name FROM contractors;

-- UNION ALL: combine results, keep duplicates (faster)
SELECT product_id FROM orders_2023
UNION ALL
SELECT product_id FROM orders_2024;

-- INTERSECT: rows appearing in both queries
SELECT customer_id FROM orders
INTERSECT
SELECT customer_id FROM returns;

-- EXCEPT: rows in the first query but not the second
SELECT customer_id FROM newsletter_subscribers
EXCEPT
SELECT customer_id FROM unsubscribed;
```

Both queries in a set operation must return the same number of columns with compatible types. UNION without ALL forces a sort to deduplicate, so prefer UNION ALL when you know there are no duplicates or don't care about them.

## Subqueries in WHERE and FROM

A subquery is a SELECT nested inside another statement. Useful when a value or row set depends on another query.

```sql
-- Scalar subquery: find books priced above average
SELECT title, price FROM books
WHERE price > (SELECT AVG(price) FROM books);

-- IN subquery: customers who have placed an order
SELECT name FROM customers
WHERE id IN (SELECT customer_id FROM orders);

-- EXISTS: often faster than IN for large sets
SELECT name FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- Derived table (subquery in FROM)
SELECT category, avg_price
FROM (
    SELECT category, AVG(price) AS avg_price
    FROM products
    GROUP BY category
) AS category_stats
WHERE avg_price > 50;
```

EXISTS short-circuits: it stops as soon as one matching row is found. For anti-joins ("customers with no orders"), `NOT EXISTS` typically outperforms `LEFT JOIN ... WHERE right.id IS NULL` because it can stop early.
