## JSON vs JSONB

Two JSON storage types with fundamentally different trade-offs. `jsonb` is the right choice in almost all cases.

| Aspect | `json` | `jsonb` |
|--------|--------|---------|
| Storage | Exact text (preserves whitespace, key order, duplicate keys) | Decomposed binary (no whitespace, sorted keys, deduplicated) |
| Parse cost | Re-parsed on every access | Parsed once on insert |
| Indexable | No | Yes (GIN, B-tree expressions) |
| Operators | Text-level only | Containment, existence, path queries |
| Use case | Audit logs where exact text preservation matters | Everything else |

```sql
-- jsonb normalizes on insert
SELECT '{"b": 2, "a": 1}'::jsonb;
-- {"a": 1, "b": 2}  (keys sorted, whitespace removed)

SELECT '{"b": 2, "a": 1}'::json;
-- {"b": 2, "a": 1}  (exact text preserved)
```

## JSON operators (`->`, `->>`, `#>`, `#>>`)

Navigate JSON structures. The single-arrow operators return JSON; double-arrow operators return text.

```sql
CREATE TABLE events (
    id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data jsonb NOT NULL
);

INSERT INTO events (data) VALUES (
    '{"type": "purchase", "amount": 99.50, "user": {"name": "Alice", "id": 42}}'
);

-- -> returns jsonb (preserves type)
SELECT data->'amount' FROM events;          -- 99.50 (jsonb number)
SELECT data->'user'->'name' FROM events;    -- "Alice" (jsonb string, with quotes)

-- ->> returns text (casts to string)
SELECT data->>'type' FROM events;           -- purchase (plain text, no quotes)
SELECT data->'user'->>'name' FROM events;   -- Alice

-- #> and #>> navigate nested paths with an array
SELECT data #>> '{user,name}' FROM events;  -- Alice
```

Use `->>` when you need the value as text for comparison or display. Use `->` when chaining access or when you need the typed jsonb value.

## Containment (`@>`) and existence (`?`)

Operators that check structure and keys rather than extracting values. Both are indexable with GIN.

```sql
-- @> containment: does the document contain this structure?
SELECT * FROM events WHERE data @> '{"type": "purchase"}';
SELECT * FROM events WHERE data @> '{"user": {"name": "Alice"}}';

-- ? key existence: does the top-level key exist?
SELECT * FROM events WHERE data ? 'amount';

-- ?| any of these keys exist
SELECT * FROM events WHERE data ?| array['refund', 'discount'];

-- ?& all of these keys exist
SELECT * FROM events WHERE data ?& array['type', 'amount', 'user'];
```

These operators are the bread and butter of JSONB queries. A default GIN index supports all of them without any additional configuration.

## `jsonb_each`, `jsonb_array_elements`, `jsonb_to_recordset`

Expand JSON objects and arrays into relational rows. Essential for joining, aggregating, or filtering individual elements within a JSON structure.

```sql
-- Expand object keys into rows
SELECT key, value FROM events, jsonb_each(data) WHERE id = 1;
-- key: 'type',   value: '"purchase"'
-- key: 'amount', value: '99.50'
-- key: 'user',   value: '{"name": "Alice", "id": 42}'

-- Expand array elements
SELECT elem FROM jsonb_array_elements('[1, 2, 3]'::jsonb) AS elem;

-- Convert JSON array of objects to a typed record set
SELECT * FROM jsonb_to_recordset(
    '[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]'::jsonb
) AS t(name text, age integer);
-- name  | age
-- Alice | 30
-- Bob   | 25
```

These functions bridge the gap between JSON and relational operations. Use them when you need to JOIN, GROUP BY, or WHERE-filter on individual elements inside a JSON value.

## Updating JSONB (`jsonb_set`, `||` operator)

Modify nested values or merge objects. Important: Postgres replaces the entire JSONB column value on every update — there is no in-place modification of individual keys.

```sql
-- jsonb_set: set a nested path
UPDATE events
SET data = jsonb_set(data, '{user,email}', '"alice@example.com"')
WHERE id = 1;

-- || merge operator: add or overwrite top-level keys
UPDATE events
SET data = data || '{"processed": true, "amount": 109.50}'
WHERE id = 1;

-- Remove a key with the - operator
UPDATE events SET data = data - 'processed' WHERE id = 1;

-- Remove a nested path with #-
UPDATE events SET data = data #- '{user,email}' WHERE id = 1;
```

For high-frequency updates to specific keys, consider promoting those keys to proper columns. JSONB updates always rewrite the full column value, which means WAL and TOAST overhead scales with document size, not change size.

## Indexing JSONB

A default GIN index supports containment (`@>`), existence (`?`, `?|`, `?&`), and path queries. For specific key lookups, B-tree expression indexes are more selective.

```sql
-- Default GIN: supports @>, ?, ?|, ?& operators
CREATE INDEX idx_events_data ON events USING GIN (data);

-- jsonb_path_ops: smaller index, supports only @> (no ? operators)
CREATE INDEX idx_events_data_paths ON events USING GIN (data jsonb_path_ops);

-- B-tree expression index: fast equality/range on a specific key
CREATE INDEX idx_events_type ON events ((data->>'type'));

-- Use the expression index
SELECT * FROM events WHERE data->>'type' = 'purchase';

-- Partial GIN index: only index documents of a certain type
CREATE INDEX idx_purchase_events ON events USING GIN (data)
    WHERE data->>'type' = 'purchase';
```

Choose `jsonb_path_ops` when you only need `@>` — it's 2-3x smaller than the default GIN opclass. Use B-tree expression indexes when you always filter on a specific key with `=` or range operators.
