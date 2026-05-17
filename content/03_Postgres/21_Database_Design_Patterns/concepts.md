## Upsert (`INSERT ... ON CONFLICT`)

Atomically insert a row or update it if a uniqueness conflict occurs. Eliminates the read-then-decide race condition that plagues application-level "does it exist?" logic.

```sql
-- Insert or update based on unique email
INSERT INTO users (email, name, last_seen)
VALUES ('alice@example.com', 'Alice', now())
ON CONFLICT (email)
DO UPDATE SET
    name = EXCLUDED.name,
    last_seen = EXCLUDED.last_seen;

-- Insert or do nothing (ignore duplicates)
INSERT INTO tags (name) VALUES ('postgres')
ON CONFLICT (name) DO NOTHING;

-- With a RETURNING clause to know what happened
INSERT INTO counters (key, value)
VALUES ('page_views', 1)
ON CONFLICT (key)
DO UPDATE SET value = counters.value + EXCLUDED.value
RETURNING key, value;
```

`EXCLUDED` refers to the row that would have been inserted. ON CONFLICT requires a unique constraint or index to detect the conflict.

## RETURNING clause

Returns the affected rows from INSERT, UPDATE, or DELETE — eliminating the need for a follow-up SELECT to see what happened.

```sql
-- Get the auto-generated ID after insert
INSERT INTO orders (customer_id, total)
VALUES (42, 99.99)
RETURNING id, created_at;

-- See what was updated
UPDATE orders SET status = 'shipped'
WHERE status = 'pending' AND created_at < '2024-01-01'
RETURNING id, customer_id;

-- See what was deleted
DELETE FROM sessions WHERE expires_at < now()
RETURNING user_id, session_id;
```

RETURNING saves a round-trip and avoids race conditions (between an INSERT and a subsequent SELECT, another transaction could modify the row). Use it whenever you need to know the result of a mutation.

## Soft deletes

Mark rows as deleted instead of physically removing them. Preserves history and enables undo, but complicates every query that needs to see only active records.

```sql
CREATE TABLE documents (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title      text NOT NULL,
    content    text NOT NULL,
    deleted_at timestamptz  -- NULL = active
);

-- "Delete" a document
UPDATE documents SET deleted_at = now() WHERE id = 5;

-- Every query must remember to filter
SELECT * FROM documents WHERE deleted_at IS NULL;

-- Use a view to make this transparent
CREATE VIEW active_documents AS
SELECT * FROM documents WHERE deleted_at IS NULL;
```

Trade-offs: soft deletes keep history (audit, undo) and prevent FK cascade issues, but they leak into every query, bloat tables, and make unique constraints harder (need partial unique indexes on `WHERE deleted_at IS NULL`). Consider using a separate archive table instead if you rarely need to query deleted records.

## Polymorphic associations

One table references rows in multiple other tables. Three approaches with different trade-offs.

```sql
-- Approach 1: Separate join tables (cleanest, uses real FKs)
CREATE TABLE comment_on_post (
    comment_id integer REFERENCES comments (id),
    post_id    integer REFERENCES posts (id),
    PRIMARY KEY (comment_id)
);
CREATE TABLE comment_on_photo (
    comment_id integer REFERENCES comments (id),
    photo_id   integer REFERENCES photos (id),
    PRIMARY KEY (comment_id)
);

-- Approach 2: Type + ID pattern (flexible but no FK enforcement)
CREATE TABLE likes (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     integer NOT NULL REFERENCES users (id),
    target_type text NOT NULL CHECK (target_type IN ('post', 'comment', 'photo')),
    target_id   integer NOT NULL
    -- Cannot create a real FK to multiple tables
);

-- Approach 3: Nullable foreign keys (simple for few targets)
CREATE TABLE notifications (
    id       integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id  integer NOT NULL REFERENCES users (id),
    post_id  integer REFERENCES posts (id),
    photo_id integer REFERENCES photos (id),
    CHECK (num_nonnulls(post_id, photo_id) = 1)
);
```

Prefer separate join tables when referential integrity matters. The type+id pattern is popular with ORMs but sacrifices FK enforcement at the database level.

## Star schema and denormalization

Analytical workloads benefit from denormalized fact and dimension tables. A star schema has a central fact table (measurements/events) surrounded by dimension tables (attributes for filtering and grouping).

```sql
-- Fact table: one row per sale event
CREATE TABLE fact_sales (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_key    integer NOT NULL REFERENCES dim_date (key),
    product_key integer NOT NULL REFERENCES dim_product (key),
    store_key   integer NOT NULL REFERENCES dim_store (key),
    quantity    integer NOT NULL,
    revenue     numeric(12, 2) NOT NULL
);

-- Dimension table: denormalized for fast filtering
CREATE TABLE dim_product (
    key           integer PRIMARY KEY,
    sku           text NOT NULL,
    name          text NOT NULL,
    category      text NOT NULL,
    subcategory   text NOT NULL,
    brand         text NOT NULL
);

-- Analytical query: fast because dimensions are pre-joined
SELECT d.category, s.city, SUM(f.revenue)
FROM fact_sales f
JOIN dim_product d ON d.key = f.product_key
JOIN dim_store s ON s.key = f.store_key
GROUP BY d.category, s.city;
```

Denormalization trades write complexity (keep dimension data in sync) for read speed. This is the right trade-off for reporting and analytics; it's the wrong trade-off for OLTP systems where write consistency matters more.
