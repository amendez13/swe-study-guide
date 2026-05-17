# Data Types

PostgreSQL has a rich type system that goes far beyond the standard SQL types. Choosing the right type gives you validation at the storage layer, better query performance, and operators that express domain logic directly in SQL.

## Key Points

- **Integers** — `smallint` (2B), `integer` (4B), `bigint` (8B). Use the smallest that fits; `integer` is the default workhorse.
- **Numeric/decimal** — exact arbitrary-precision arithmetic. Mandatory for money. Slower than float but never rounds silently.
- **Floating point** — fast approximate math. Never use for money; fine for coordinates and sensor data.
- **Character types** — prefer `text` always. `varchar(n)` adds a length check; `char(n)` pads with spaces and is rarely correct.
- **Timestamps** — always use `timestamptz`. It stores UTC and converts on display. Bare `timestamp` is ambiguous.
- **UUID** — 128-bit random IDs. Built-in `gen_random_uuid()` since PG 13. Use for distributed systems or to prevent ID enumeration.
- **JSONB** — binary indexed JSON. Supports containment, existence, path access, and GIN indexes. Use for flexible attributes, not for data you JOIN on.
- **Arrays** — store small lists in a single column. Support containment and overlap operators with GIN indexes. Break 1NF, so use judiciously.
- **Enums** — fixed set of ordered labels enforced by the type system. Easy to add values, hard to remove them.
- **Range types** — intervals with containment, overlap, and adjacency operators. Pair with exclusion constraints to prevent double-booking.

## Example

```sql
CREATE TYPE priority AS ENUM ('low', 'medium', 'high', 'critical');

CREATE TABLE incidents (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title       text NOT NULL,
    priority    priority NOT NULL DEFAULT 'medium',
    metadata    jsonb NOT NULL DEFAULT '{}',
    tags        text[] NOT NULL DEFAULT '{}',
    window      tstzrange,
    reported_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO incidents (title, priority, metadata, tags, window)
VALUES (
    'Database CPU spike',
    'high',
    '{"region": "us-east-1", "cluster": "prod-2"}',
    ARRAY['database', 'performance'],
    '[2024-03-15 14:00+00, 2024-03-15 14:45+00)'
);

SELECT title, priority, metadata->>'region' AS region
FROM incidents
WHERE tags @> ARRAY['database']
  AND window @> now();
```

This exercises most of the topic's types in a single realistic table: an enum for priority, JSONB for flexible metadata, an array for tags, a range for the incident time window, and `timestamptz` for the report time.
