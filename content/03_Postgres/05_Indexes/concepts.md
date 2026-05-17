## B-tree index

The default and most common index type. Supports equality (`=`) and range queries (`<`, `>`, `BETWEEN`, `IN`) on ordered data. Created automatically for primary keys and UNIQUE constraints.

```sql
-- Explicit B-tree index
CREATE INDEX idx_orders_created ON orders (created_at);

-- Postgres uses it for range scans
EXPLAIN SELECT * FROM orders WHERE created_at > '2024-01-01';
-- Index Scan using idx_orders_created
```

B-trees work well for high-cardinality columns (many distinct values). They store sorted keys with pointers to heap tuples, enabling both forward and backward scans.

## Heap, pages, and tuples

Postgres stores table data in a heap — an unordered collection of 8 kB pages. Each row is a tuple within a page. An index stores sorted keys plus CTIDs (physical tuple addresses: block number + offset within the block).

```text
Table "orders" (heap):
┌──────────────────────────────────────────┐
│ Page 0: [tuple0, tuple1, tuple2, ...]    │
│ Page 1: [tuple3, tuple4, tuple5, ...]    │
│ Page 2: [tuple6, tuple7, ...]            │
└──────────────────────────────────────────┘

B-tree index on "created_at":
  key: 2024-01-01 → CTID (0, 2)
  key: 2024-01-15 → CTID (1, 0)
  key: 2024-02-01 → CTID (0, 1)
```

An index lookup finds the key, reads the CTID, then fetches the heap tuple. This "index scan + heap fetch" is fast for selective queries but adds random I/O per row. When selectivity is poor, Postgres prefers a sequential scan (reading pages in order).

## Composite indexes

Indexes on multiple columns. Column order is critical: the index is useful for queries that filter on a leading prefix of the index columns.

```sql
CREATE INDEX idx_orders_customer_date ON orders (customer_id, created_at);

-- Uses the index (leading prefix match)
SELECT * FROM orders WHERE customer_id = 42;
SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2024-01-01';

-- Cannot use the index efficiently (skips leading column)
SELECT * FROM orders WHERE created_at > '2024-01-01';
```

Think of a composite index like a phone book sorted by (last name, first name). You can look up all Smiths, or all Smith Johns, but you can't efficiently find all Johns without scanning the entire book.

## Covering indexes (INCLUDE)

Add non-key columns to an index so queries can be answered entirely from the index without visiting the heap (index-only scan).

```sql
CREATE INDEX idx_orders_covering ON orders (customer_id)
    INCLUDE (total, status);

-- Index-only scan: all needed columns are in the index
EXPLAIN SELECT total, status FROM orders WHERE customer_id = 42;
-- Index Only Scan using idx_orders_covering
```

Included columns are stored in the index leaf pages but are not part of the search key — they don't help with filtering or sorting, only with avoiding heap fetches. This trades write performance and index size for faster reads.

## Partial indexes

An index with a WHERE clause that only covers a subset of rows. Saves space and speeds up queries that always include the same filter condition.

```sql
-- Only index unshipped orders (the ones we query most)
CREATE INDEX idx_orders_pending ON orders (created_at)
    WHERE status = 'pending';

-- Uses the partial index
SELECT * FROM orders WHERE status = 'pending' AND created_at > '2024-01-01';

-- Cannot use it (different status)
SELECT * FROM orders WHERE status = 'shipped' AND created_at > '2024-01-01';
```

Partial indexes are powerful for tables where queries overwhelmingly filter on a specific subset — active users, unprocessed jobs, recent records. The index is smaller, faster to scan, and cheaper to maintain.

## Expression indexes

Index the result of an expression or function rather than the raw column value. Required when queries filter on a transformed column.

```sql
-- Queries use lower(email) for case-insensitive lookup
CREATE INDEX idx_users_email_lower ON users (lower(email));

-- Now this uses the index
SELECT * FROM users WHERE lower(email) = 'alice@example.com';

-- Date extraction
CREATE INDEX idx_events_year ON events ((extract(year FROM starts_at)));
```

The expression in the index must exactly match the expression in the query for the planner to use it. Wrapping the expression in extra parentheses in CREATE INDEX is required when it's not a simple function call.

## GIN index (Generalized Inverted Index)

Maps each element (array element, JSON key, lexeme) to the set of rows containing it. Essential for full-text search, JSONB containment, and array operations.

```sql
-- JSONB containment queries
CREATE INDEX idx_products_attrs ON products USING GIN (attrs);
SELECT * FROM products WHERE attrs @> '{"color": "blue"}';

-- Array overlap/containment
CREATE INDEX idx_articles_tags ON articles USING GIN (tags);
SELECT * FROM articles WHERE tags @> ARRAY['postgres'];

-- Full-text search
CREATE INDEX idx_docs_search ON documents USING GIN (search_vector);
SELECT * FROM documents WHERE search_vector @@ to_tsquery('postgres & replication');
```

GIN indexes are larger and slower to build and update than B-trees, but they make containment, existence (`?`, `?|`, `?&`), and full-text match operations fast on columns that would otherwise require full table scans.

## GiST index (Generalized Search Tree)

Supports geometric, range, and full-text queries. Backs exclusion constraints, PostGIS spatial lookups, and nearest-neighbor searches.

```sql
-- Range overlap queries
CREATE INDEX idx_bookings_during ON bookings USING GIST (during);
SELECT * FROM bookings WHERE during && '[2024-03-15, 2024-03-16)';

-- PostGIS spatial queries
CREATE INDEX idx_places_location ON places USING GIST (location);
SELECT * FROM places
WHERE ST_DWithin(location, ST_MakePoint(-73.98, 40.75)::geography, 1000);
```

GiST is more general-purpose than GIN: it handles types that need spatial relationships (containment, overlap, proximity) rather than exact element membership. It's the required index type for exclusion constraints.

## `CREATE INDEX CONCURRENTLY`

Builds an index without locking the table for writes. Slower to build but essential in production where you can't afford to block inserts and updates for minutes.

```sql
-- Non-blocking index creation
CREATE INDEX CONCURRENTLY idx_orders_email ON orders (email);

-- Regular CREATE INDEX holds a write lock for the entire build
-- CONCURRENTLY scans the table twice but allows writes between scans
```

Caveats: CONCURRENTLY cannot run inside a transaction block, and if it fails partway through (e.g., unique violation on a new UNIQUE index), it leaves an INVALID index that you must drop and retry. Check with `\d tablename` or `pg_indexes` for invalid indexes.

## Index selectivity and when indexes don't help

Selectivity is the fraction of rows an index lookup returns. High selectivity (few rows) makes indexes effective; low selectivity (many rows) makes a sequential scan cheaper.

```sql
-- High selectivity: index scan is fast
SELECT * FROM users WHERE id = 42;            -- 1 row out of millions

-- Low selectivity: sequential scan wins
SELECT * FROM users WHERE active = true;      -- 90% of rows match

-- Check column statistics
SELECT tablename, attname, n_distinct, most_common_vals
FROM pg_stats WHERE tablename = 'users' AND attname = 'active';
```

Rules of thumb: a B-tree index helps when it eliminates >90% of rows. For boolean or low-cardinality columns, consider a partial index on the minority value (`WHERE active = false`) rather than indexing the entire column.
