# Constraints and Data Integrity

Constraints are the database's way of encoding business rules into the schema itself. Rather than trusting every application and script to validate data correctly, constraints guarantee that invalid data never reaches the table — regardless of which client wrote it.

## Key Points

- **NOT NULL** — default to it. Make columns nullable only when null carries a distinct meaning. Nulls complicate comparisons and aggregates.
- **UNIQUE** — enforces distinct values and auto-creates a B-tree index. NULL values are considered distinct unless you opt into `NULLS NOT DISTINCT` (PG 15+).
- **CHECK** — arbitrary boolean expressions per row. Cannot reference other tables. Name them for clear error messages.
- **DEFAULT** — evaluated at insert time, not table creation. Use `now()`, `gen_random_uuid()`, or custom functions for dynamic defaults.
- **Exclusion constraints** — generalized uniqueness using operators (overlap, equality). Backed by GiST indexes. The standard way to prevent double-bookings.
- **Domain types** — named base-type + constraints bundles. Define a validation rule once, reuse across columns and tables.

## Example

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE DOMAIN positive_int AS integer CHECK (VALUE > 0);

CREATE TABLE shifts (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee   text NOT NULL,
    department text NOT NULL,
    during     tstzrange NOT NULL,
    headcount  positive_int NOT NULL DEFAULT 1,
    created_at timestamptz NOT NULL DEFAULT now(),

    -- No overlapping shifts for the same employee
    EXCLUDE USING GIST (employee WITH =, during WITH &&)
);

-- Valid shift
INSERT INTO shifts (employee, department, during)
VALUES ('alice', 'engineering', '[2024-03-15 09:00+00, 2024-03-15 17:00+00)');

-- Overlapping shift for alice is rejected at the database level
INSERT INTO shifts (employee, department, during)
VALUES ('alice', 'engineering', '[2024-03-15 12:00+00, 2024-03-15 20:00+00)');
-- ERROR: conflicting key value violates exclusion constraint
```

This exercises NOT NULL on every meaningful column, a DEFAULT for timestamp and headcount, a domain type for the positive integer constraint, and an exclusion constraint preventing schedule conflicts.
