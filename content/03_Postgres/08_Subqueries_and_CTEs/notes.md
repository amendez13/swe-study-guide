# Subqueries and Common Table Expressions

Subqueries and CTEs let you compose complex queries from simpler building blocks. They express multi-step logic within a single SQL statement — filtering against aggregates, traversing hierarchies, or structuring queries for readability.

## Key Points

- **Scalar subquery** — returns one value. Usable in SELECT, WHERE, or as a column expression. Returns NULL if no rows match.
- **Derived table (FROM subquery)** — produces a virtual table. Must be aliased. The planner often flattens it into the outer query.
- **Correlated subquery** — references the outer query. Re-evaluated per outer row. Consider rewriting as a LATERAL join if performance is poor.
- **EXISTS / NOT EXISTS** — short-circuits at the first match. Handles NULLs correctly, unlike NOT IN. Prefer for anti-joins.
- **CTEs** — named WITH blocks for readability. PG 12+ inlines non-recursive CTEs by default (no longer optimization fences).
- **Recursive CTEs** — WITH RECURSIVE for tree/graph traversal. Base case UNION ALL'd with a recursive step that runs until no new rows are produced.

## Example

```sql
-- Recursive CTE: compute the category breadcrumb path for each category

CREATE TABLE categories (
    id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name      text NOT NULL,
    parent_id integer REFERENCES categories (id)
);

INSERT INTO categories (name, parent_id) VALUES
    ('Electronics', NULL),
    ('Computers', 1),
    ('Laptops', 2),
    ('Gaming Laptops', 3);

WITH RECURSIVE breadcrumb AS (
    -- Base case: start from leaf categories
    SELECT id, name, parent_id, name AS path
    FROM categories
    WHERE id = 4  -- Gaming Laptops

    UNION ALL

    -- Walk up the tree
    SELECT c.id, c.name, c.parent_id, c.name || ' > ' || b.path
    FROM categories c
    JOIN breadcrumb b ON c.id = b.parent_id
)
SELECT path FROM breadcrumb WHERE parent_id IS NULL;
-- Result: 'Electronics > Computers > Laptops > Gaming Laptops'
```

This recursive CTE walks from a leaf node up to the root, building a breadcrumb string at each step. The recursion terminates when no more parent rows are found.
