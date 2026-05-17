# Indexes

Indexes are the primary tool for making queries fast. They trade write performance and storage space for dramatically faster reads — but only when the query planner can use them and the selectivity justifies the lookup overhead.

## Key Points

- **B-tree** — the default. Supports equality and range queries. Created automatically for PKs and UNIQUE constraints.
- **Heap, pages, tuples** — table data is unordered in 8 kB pages. Indexes store sorted keys + CTIDs pointing to heap locations.
- **Composite indexes** — column order matters. The index only helps queries that filter on a leading prefix of the key columns.
- **Covering indexes (INCLUDE)** — include non-key columns so queries avoid heap fetches entirely (index-only scan).
- **Partial indexes** — index a subset of rows. Smaller, faster, and cheaper to maintain for queries that always filter the same way.
- **Expression indexes** — index a function result. The query expression must match the index expression exactly.
- **GIN** — inverted index mapping elements to rows. Powers JSONB containment, array operations, and full-text search.
- **GiST** — generalized search tree for range overlap, spatial queries, and exclusion constraints.
- **CREATE INDEX CONCURRENTLY** — non-blocking index builds for production use. Cannot run inside a transaction.
- **Selectivity** — indexes help when they eliminate most rows. Low-selectivity columns (booleans, status flags) benefit more from partial indexes.

## Example

```sql
-- Table with various query patterns
CREATE TABLE orders (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id integer NOT NULL REFERENCES customers (id),
    status      text NOT NULL DEFAULT 'pending',
    total       numeric(10, 2) NOT NULL,
    email       text NOT NULL,
    tags        text[] NOT NULL DEFAULT '{}',
    created_at  timestamptz NOT NULL DEFAULT now()
);

-- Composite index for customer lookups with date ranges
CREATE INDEX idx_orders_cust_date ON orders (customer_id, created_at);

-- Partial index for the hot path: pending orders
CREATE INDEX idx_orders_pending ON orders (created_at) WHERE status = 'pending';

-- Expression index for case-insensitive email search
CREATE INDEX idx_orders_email ON orders (lower(email));

-- GIN index for array containment
CREATE INDEX idx_orders_tags ON orders USING GIN (tags);

-- Covering index to avoid heap fetch for dashboard query
CREATE INDEX idx_orders_dashboard ON orders (customer_id) INCLUDE (total, status);

-- Verify which indexes the planner chooses
EXPLAIN ANALYZE SELECT total, status FROM orders WHERE customer_id = 42;
```

This creates a realistic set of indexes for a single table, each targeting a different query pattern. Use EXPLAIN ANALYZE to confirm the planner actually uses them.
