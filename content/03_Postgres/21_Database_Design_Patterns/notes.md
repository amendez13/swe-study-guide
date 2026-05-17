# Database Design Patterns

Patterns that come up repeatedly in application development: atomic upserts, returning mutation results, representing deletion without data loss, polymorphic references, and denormalization for analytics. Each has clear trade-offs.

## Key Points

- **Upsert (ON CONFLICT)** — atomic insert-or-update. Use EXCLUDED to reference the proposed row. Requires a unique constraint.
- **RETURNING** — get affected rows from INSERT/UPDATE/DELETE without a follow-up SELECT. Saves a round-trip and avoids races.
- **Soft deletes** — `deleted_at` timestamp preserves history but leaks into every query. Use views or a separate archive table to manage complexity.
- **Polymorphic associations** — separate join tables for FK integrity, type+id for flexibility, nullable FKs for simplicity. Choose based on whether you need database-enforced integrity.
- **Star schema** — denormalized fact + dimension tables for analytics. Fast reads, complex writes. Right for reporting, wrong for OLTP.

## Example

```sql
-- Upsert + RETURNING: idempotent API key registration
CREATE TABLE api_keys (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    client_id  text UNIQUE NOT NULL,
    key_hash   text NOT NULL,
    last_used  timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Register or refresh a client's API key
INSERT INTO api_keys (client_id, key_hash, last_used)
VALUES ('service-A', 'sha256:abc123', now())
ON CONFLICT (client_id)
DO UPDATE SET
    key_hash = EXCLUDED.key_hash,
    last_used = EXCLUDED.last_used
RETURNING id, client_id, created_at,
    (xmax = 0) AS was_inserted;
-- was_inserted: true if new row, false if updated existing

-- Soft delete with partial unique index
CREATE TABLE invitations (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email      text NOT NULL,
    team_id    integer NOT NULL,
    deleted_at timestamptz
);
-- Unique only among non-deleted rows
CREATE UNIQUE INDEX idx_invitations_active
    ON invitations (email, team_id) WHERE deleted_at IS NULL;
```

This shows upsert with RETURNING (including a trick to detect insert vs update using `xmax = 0`), and a soft delete pattern with a partial unique index that allows re-inviting previously soft-deleted entries.
