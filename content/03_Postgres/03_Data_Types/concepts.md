## Integers (`smallint`, `integer`, `bigint`)

Fixed-size numeric types that store whole numbers. Choose the smallest type that fits the domain — smaller types use less disk, fit more rows per page, and improve cache efficiency.

| Type | Size | Range |
|------|------|-------|
| `smallint` | 2 bytes | -32,768 to 32,767 |
| `integer` | 4 bytes | -2.1 billion to 2.1 billion |
| `bigint` | 8 bytes | ±9.2 × 10¹⁸ |

```sql
CREATE TABLE sensors (
    id       integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reading  smallint NOT NULL,  -- values 0–1000, no need for integer
    event_id bigint              -- external system uses large IDs
);
```

`integer` is the default choice for most columns. Use `bigint` for columns that will exceed 2 billion rows or reference external systems with large IDs.

## `numeric` and `decimal`

Arbitrary-precision exact types for values where floating-point rounding is unacceptable — typically money, financial calculations, or scientific measurements requiring exact decimal representation.

```sql
CREATE TABLE line_items (
    id       integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    price    numeric(10, 2) NOT NULL,  -- up to 99,999,999.99
    quantity integer NOT NULL,
    total    numeric(12, 2) GENERATED ALWAYS AS (price * quantity) STORED
);
```

`numeric` without precision/scale stores any number of digits but is slower for arithmetic. With a scale specified, Postgres rounds on insert. Calculations between `numeric` values preserve full precision (no silent truncation like floating point).

## Floating point (`real`, `double precision`)

IEEE 754 approximate types. Fast hardware-accelerated math, but subject to rounding — `0.1 + 0.2` does not equal `0.3` exactly.

```sql
SELECT 0.1::real + 0.2::real = 0.3::real;  -- false!
SELECT 0.1::numeric + 0.2::numeric = 0.3::numeric;  -- true
```

Use `real` (4 bytes, ~6 decimal digits) or `double precision` (8 bytes, ~15 decimal digits) for scientific data, coordinates, or sensor readings where exact decimal representation isn't required. Never use for money.

## Character types (`text`, `varchar`, `char`)

`text` is the preferred general-purpose string type in Postgres — it has no length limit and no performance penalty compared to `varchar`. There is no storage difference between `text` and `varchar` internally.

```sql
CREATE TABLE users (
    name   text NOT NULL,             -- unbounded, preferred
    email  varchar(255) NOT NULL,     -- length check as documentation/validation
    code   char(3)                    -- always exactly 3 chars, padded with spaces
);
```

`varchar(n)` adds a server-side length check but is otherwise identical to `text`. `char(n)` right-pads with spaces to the declared length, which causes subtle comparison issues and is rarely what you want. If you don't need a length constraint, use `text`.

## Timestamps and time zones

`timestamptz` (timestamp with time zone) stores UTC internally and converts on display using the session's `timezone` setting. Always prefer `timestamptz` over bare `timestamp`.

```sql
-- timestamptz: stores UTC, displays in session timezone
SET timezone = 'America/New_York';
SELECT now();  -- shows Eastern time

CREATE TABLE events (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       text NOT NULL,
    starts_at  timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Insert in any timezone; Postgres normalizes to UTC
INSERT INTO events (name, starts_at)
VALUES ('Launch', '2024-03-15 09:00:00-05');
```

Bare `timestamp` (without time zone) stores whatever value you give it with no timezone conversion. This is dangerous in multi-timezone applications because the stored value is ambiguous — you don't know what timezone it represents.

## UUID

A 128-bit universally unique identifier. Good for distributed ID generation where auto-incrementing integers require coordination between nodes.

```sql
CREATE TABLE api_keys (
    id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id integer REFERENCES users (id),
    key     text NOT NULL
);

-- gen_random_uuid() is built-in since Postgres 13
SELECT gen_random_uuid();
-- e.g. 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
```

Trade-offs vs integer IDs: UUIDs are 16 bytes (vs 4 for integer), produce fragmented B-tree inserts (random values don't cluster), and are harder to communicate verbally. Use them when you need IDs generated outside the database or want to prevent enumeration attacks.

## `JSONB`

A binary, indexed JSON type that supports containment queries, key existence checks, and path-based access. The workhorse for semi-structured data in Postgres.

```sql
CREATE TABLE products (
    id       integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name     text NOT NULL,
    attrs    jsonb NOT NULL DEFAULT '{}'
);

INSERT INTO products (name, attrs)
VALUES ('Widget', '{"color": "blue", "weight_kg": 0.5, "tags": ["sale", "new"]}');

-- Access nested values
SELECT name, attrs->>'color' AS color FROM products;
SELECT name FROM products WHERE attrs @> '{"color": "blue"}';
```

Prefer `jsonb` over `json` unless you need exact text preservation (whitespace, key ordering). `jsonb` supports GIN indexes for fast containment and existence queries. Use it for flexible attributes, but don't store data in JSONB that you regularly filter or join on — promote those to proper columns.

## Arrays

Postgres columns can hold arrays of any type. Useful for small, fixed-purpose lists like tags or feature flags where a separate table would be overkill.

```sql
CREATE TABLE articles (
    id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title text NOT NULL,
    tags  text[] NOT NULL DEFAULT '{}'
);

INSERT INTO articles (title, tags) VALUES ('Intro to PG', ARRAY['postgres', 'tutorial']);

-- Contains operator
SELECT * FROM articles WHERE tags @> ARRAY['postgres'];

-- Unnest to join with array elements
SELECT id, unnest(tags) AS tag FROM articles;
```

Arrays break first normal form and make updates to individual elements awkward (you must replace the whole array). For large or frequently-queried collections, a junction table is usually better. GIN indexes support the `@>`, `<@`, and `&&` (overlap) operators on arrays.

## Enums

A user-defined type with a fixed, ordered set of labels. Useful for low-cardinality categorical columns (status, priority, role) where you want the database to enforce valid values.

```sql
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered');

CREATE TABLE orders (
    id     integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status order_status NOT NULL DEFAULT 'pending'
);

-- Only enum values are accepted
INSERT INTO orders (status) VALUES ('shipped');     -- OK
INSERT INTO orders (status) VALUES ('cancelled');   -- ERROR
```

Adding a new value is easy (`ALTER TYPE ... ADD VALUE`), but removing or renaming values requires recreating the type. For frequently-changing option sets, a lookup table with a foreign key is more flexible.

## Range types

Represent intervals of values with built-in support for containment, overlap, and adjacency operations. Paired with exclusion constraints, they prevent overlapping bookings or schedules at the database level.

```sql
CREATE TABLE reservations (
    id     integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    room   text NOT NULL,
    during tstzrange NOT NULL,
    EXCLUDE USING GIST (room WITH =, during WITH &&)
);

-- Book a room
INSERT INTO reservations (room, during)
VALUES ('A', '[2024-03-15 09:00, 2024-03-15 11:00)');

-- Overlapping booking is rejected by the exclusion constraint
INSERT INTO reservations (room, during)
VALUES ('A', '[2024-03-15 10:00, 2024-03-15 12:00)');  -- ERROR

-- Containment check
SELECT * FROM reservations WHERE during @> '2024-03-15 10:00'::timestamptz;
```

Available types: `int4range`, `int8range`, `numrange`, `tsrange`, `tstzrange`, `daterange`. The bracket notation `[` means inclusive, `)` means exclusive. GiST indexes make range operations fast.
