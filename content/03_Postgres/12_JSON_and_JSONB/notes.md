# JSON and JSONB

JSONB gives Postgres native support for semi-structured data with full indexing and query capabilities. It's the bridge between relational strictness and document-store flexibility — letting you store variable-shape data alongside typed columns without sacrificing query performance.

## Key Points

- **JSON vs JSONB** — always prefer JSONB. It stores binary, is indexable, and supports rich operators. JSON is only for exact text preservation.
- **Access operators** — `->` returns jsonb, `->>` returns text. `#>` and `#>>` navigate nested paths.
- **Containment and existence** — `@>` checks structure; `?` checks key presence. Both are GIN-indexable.
- **Expansion functions** — `jsonb_each`, `jsonb_array_elements`, `jsonb_to_recordset` bridge JSON into relational operations.
- **Updates** — `jsonb_set` for paths, `||` for merge, `-` for removal. Always rewrites the full column value.
- **Indexing** — default GIN for general queries; `jsonb_path_ops` for smaller @>-only index; B-tree expression indexes for specific key equality.

## Example

```sql
CREATE TABLE api_logs (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    endpoint   text NOT NULL,
    payload    jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- GIN index for flexible querying
CREATE INDEX idx_logs_payload ON api_logs USING GIN (payload);
-- Expression index for a hot-path filter
CREATE INDEX idx_logs_status ON api_logs ((payload->>'status'));

-- Insert structured log
INSERT INTO api_logs (endpoint, payload) VALUES (
    '/api/orders',
    '{"status": "error", "code": 422, "errors": ["invalid_sku", "qty_exceeded"], "user_id": 7}'
);

-- Containment query (uses GIN)
SELECT * FROM api_logs WHERE payload @> '{"status": "error"}';

-- Expression index query
SELECT * FROM api_logs WHERE payload->>'status' = 'error';

-- Expand errors array for aggregation
SELECT error, COUNT(*) FROM api_logs,
    jsonb_array_elements_text(payload->'errors') AS error
WHERE payload->>'status' = 'error'
GROUP BY error ORDER BY count DESC;
```

This shows JSONB used for flexible API log storage with both GIN (structure queries) and B-tree expression (specific key lookup) indexes, plus array expansion for aggregation.
