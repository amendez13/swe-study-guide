## Tables, rows, and columns

A table is a named collection of rows that all share the same column schema. Each column has a name and a data type; Postgres enforces the type on every insert and update. Rows are the individual records.

```sql
CREATE TABLE authors (
    id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL,
    bio  text
);

INSERT INTO authors (name, bio)
VALUES ('Knuth', 'Author of The Art of Computer Programming');
```

Tables live inside a schema (default `public`) inside a database. A single Postgres cluster can host many databases, each containing many schemas, each containing many tables.

## Primary keys

A column (or set of columns) that uniquely identifies every row. Postgres enforces uniqueness automatically and creates a B-tree index on the primary key so lookups by ID are fast.

```sql
-- Single-column primary key (most common)
CREATE TABLE books (
    id    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title text NOT NULL
);

-- Composite primary key on a junction table
CREATE TABLE book_authors (
    book_id   integer REFERENCES books (id),
    author_id integer REFERENCES authors (id),
    PRIMARY KEY (book_id, author_id)
);
```

Use `GENERATED ALWAYS AS IDENTITY` (SQL-standard) for auto-incrementing integer keys. The older `serial` pseudo-type still works but is considered legacy. For distributed systems, `uuid` primary keys avoid coordination between nodes.

## Foreign keys

A constraint that references a primary key (or unique column) in another table, enforcing referential integrity. Postgres rejects inserts that point to a non-existent parent row and controls what happens when the parent is deleted.

```sql
CREATE TABLE books (
    id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title     text NOT NULL,
    author_id integer REFERENCES authors (id) ON DELETE SET NULL
);
```

The three deletion behaviors to know:

| Clause | On parent delete | Use when |
|--------|-----------------|----------|
| `ON DELETE RESTRICT` (default) | Block the delete | The child row is meaningless without the parent |
| `ON DELETE CASCADE` | Delete the child too | The child is owned by the parent (e.g. order items) |
| `ON DELETE SET NULL` | Set the FK column to NULL | The child can exist independently |

Foreign keys add a check on every insert and update to the child table. On write-heavy tables with millions of rows, this cost is real — but removing the constraint trades correctness for speed, which is rarely the right trade.

## Normalization (1NF through 3NF)

The process of structuring tables to eliminate data redundancy and update anomalies. Each normal form builds on the previous one.

**1NF** — every column holds a single atomic value (no arrays or comma-separated lists as a way to store multiple values in one cell). Postgres allows array columns, but storing related entities as arrays instead of rows in a related table usually signals a normalization problem.

**2NF** — every non-key column depends on the entire primary key, not just part of it. Matters most with composite keys: if a column depends on only one of the key columns, pull it into its own table.

**3NF** — every non-key column depends only on the primary key, not on another non-key column. A classic violation: storing both `zip_code` and `city` in an orders table, where `city` is really a function of `zip_code`.

Normalization reduces storage waste and prevents conflicting updates at the cost of more joins at read time. Denormalization (storing redundant data deliberately) is a performance optimization, not a design starting point.

## Relationship types

The three fundamental ways tables relate to each other. Choosing the right relationship shape determines how many tables you need and where the foreign key lives.

**One-to-many** — the most common relationship. One parent row has many child rows. The foreign key lives on the "many" side.

```sql
-- One author has many books
CREATE TABLE books (
    id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title     text NOT NULL,
    author_id integer REFERENCES authors (id)
);
```

**Many-to-many** — both sides can have many related rows on the other side. Requires a junction table (also called a join table or bridge table) with two foreign keys.

```sql
-- A book can have many tags; a tag can apply to many books
CREATE TABLE tags (
    id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text UNIQUE NOT NULL
);

CREATE TABLE book_tags (
    book_id integer REFERENCES books (id) ON DELETE CASCADE,
    tag_id  integer REFERENCES tags (id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, tag_id)
);
```

**One-to-one** — a row in one table corresponds to exactly one row in another. Implemented with a foreign key plus a `UNIQUE` constraint on that foreign key column. Use when a subset of columns is accessed separately or has different access-control needs.

## Schemas

A namespace inside a database that groups tables, views, functions, and other objects. Every object you create without qualifying it lands in the `public` schema by default.

```sql
-- Create a schema
CREATE SCHEMA inventory;

-- Create a table inside it
CREATE TABLE inventory.products (
    id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL
);

-- Query it
SELECT * FROM inventory.products;
```

Schemas are useful for multi-tenant isolation (one schema per tenant, same table structure), separating application modules, and running parallel tests (create a throwaway schema per test worker, drop it afterward). The `search_path` setting controls which schemas Postgres looks in when a table name is unqualified:

```sql
SET search_path TO inventory, public;
-- Now "products" resolves to inventory.products
```
