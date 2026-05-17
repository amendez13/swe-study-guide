## NOT NULL

Prevents a column from accepting null values. Apply to any column where null is semantically meaningless — which is most columns.

```sql
CREATE TABLE users (
    id    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email text NOT NULL,
    name  text NOT NULL
);

-- This fails immediately
INSERT INTO users (email) VALUES ('a@b.com');
-- ERROR: null value in column "name" violates not-null constraint
```

Nullable columns complicate queries (three-valued logic), break equality comparisons, and require `COALESCE` or `IS NULL` checks everywhere they're used. Default to NOT NULL and make a column nullable only when null carries a distinct meaning (e.g., "not yet assigned").

## UNIQUE

Enforces that all values (or value combinations) in a column set are distinct. Postgres automatically creates a B-tree index to enforce uniqueness efficiently.

```sql
CREATE TABLE users (
    id    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email text NOT NULL UNIQUE
);

-- Multi-column uniqueness
CREATE TABLE enrollments (
    student_id integer REFERENCES students (id),
    course_id  integer REFERENCES courses (id),
    UNIQUE (student_id, course_id)
);
```

NULL values are considered distinct by UNIQUE constraints — two rows can both have NULL in a unique column. If you need uniqueness including nulls, use a partial unique index or `NULLS NOT DISTINCT` (Postgres 15+).

## CHECK constraints

A boolean expression evaluated on every insert and update. Use for domain rules that go beyond data type validation.

```sql
CREATE TABLE products (
    id    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name  text NOT NULL,
    price numeric(10, 2) NOT NULL CHECK (price > 0),
    stock integer NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

-- Multi-column CHECK
CREATE TABLE events (
    id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    starts_at timestamptz NOT NULL,
    ends_at   timestamptz NOT NULL,
    CHECK (ends_at > starts_at)
);
```

CHECK constraints cannot reference other tables (use triggers or application logic for cross-table validation). They run after DEFAULT values are applied but before the row is written. Named constraints produce clearer error messages:

```sql
ALTER TABLE products ADD CONSTRAINT positive_price CHECK (price > 0);
```

## DEFAULT values

Assigns a value when none is provided on insert. Can reference constants or functions like `now()`, `gen_random_uuid()`, or custom functions.

```sql
CREATE TABLE orders (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status     text NOT NULL DEFAULT 'pending',
    created_at timestamptz NOT NULL DEFAULT now(),
    ref_code   uuid NOT NULL DEFAULT gen_random_uuid()
);

-- Omit defaulted columns
INSERT INTO orders DEFAULT VALUES;
-- id=1, status='pending', created_at=<now>, ref_code=<uuid>
```

DEFAULT is evaluated at insert time, not at table creation time. `DEFAULT now()` gives each row its own timestamp. For computed columns that depend on other columns, use `GENERATED ALWAYS AS (...) STORED` instead.

## Exclusion constraints

Generalized uniqueness: no two rows may satisfy a given set of operators simultaneously. The classic use case is preventing overlapping time ranges or conflicting schedules.

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE room_bookings (
    id     integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    room   text NOT NULL,
    during tstzrange NOT NULL,
    EXCLUDE USING GIST (room WITH =, during WITH &&)
);

-- First booking succeeds
INSERT INTO room_bookings (room, during)
VALUES ('A101', '[2024-03-15 09:00, 2024-03-15 11:00)');

-- Overlapping booking for same room is rejected
INSERT INTO room_bookings (room, during)
VALUES ('A101', '[2024-03-15 10:00, 2024-03-15 12:00)');
-- ERROR: conflicting key value violates exclusion constraint
```

Exclusion constraints require a GiST index (or SP-GiST). The `btree_gist` extension enables using equality operators alongside range overlap in the same constraint. Without it, you can only exclude on GiST-native types like ranges and geometric types.

## Domain types

Named types built from a base type plus constraints. Let you define a reusable validation rule once and apply it to multiple columns across multiple tables.

```sql
-- Define a domain for positive money amounts
CREATE DOMAIN positive_money AS numeric(12, 2)
    CHECK (VALUE > 0);

-- Define a domain for email-shaped strings
CREATE DOMAIN email AS text
    CHECK (VALUE ~ '^[^@]+@[^@]+\.[^@]+$');

-- Use them like built-in types
CREATE TABLE invoices (
    id     integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    amount positive_money NOT NULL,
    billed_to email NOT NULL
);
```

Domains centralize constraint definitions: if your validation rule changes, alter the domain once instead of every column. They compose with NOT NULL and DEFAULT but cannot carry indexes (those are defined on columns, not types).
