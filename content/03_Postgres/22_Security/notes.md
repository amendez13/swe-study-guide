# Security

Database security operates at multiple layers: preventing injection at the query level, restricting access via roles and privileges, isolating tenants with row-level policies, and encrypting traffic on the wire. Each layer defends against different threat vectors.

## Key Points

- **SQL injection** — never concatenate user input into queries. Parameterized queries are the only reliable defense.
- **Roles and privileges** — GRANT/REVOKE at database, schema, table, and column level. Principle of least privilege: separate DDL and DML roles.
- **Row-Level Security** — per-user row filtering enforced by the database. Transparent to the application. Prevents tenant data leaks even if app logic has bugs.
- **Prepared statements** — parameters are never interpreted as SQL. Also improve plan reuse. Note PgBouncer compatibility in transaction mode.
- **SSL/TLS** — encrypt client-server traffic. Use `verify-full` in production to prevent MITM. `require` alone doesn't verify the server's identity.

## Example

```sql
-- Multi-tenant RLS setup

CREATE TABLE tenant_data (
    id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id integer NOT NULL,
    content   text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Application role with restricted privileges
CREATE ROLE app_runtime LOGIN PASSWORD 'app_secret';
GRANT USAGE ON SCHEMA public TO app_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_data TO app_runtime;

-- Enable RLS (owner bypasses by default, so force it)
ALTER TABLE tenant_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_data FORCE ROW LEVEL SECURITY;

-- Policy: each tenant sees only their own rows
CREATE POLICY tenant_isolation ON tenant_data
    USING (tenant_id = current_setting('app.tenant_id')::integer)
    WITH CHECK (tenant_id = current_setting('app.tenant_id')::integer);

-- Application sets tenant context at the start of each request
SET app.tenant_id = '7';

-- All queries are now automatically scoped to tenant 7
SELECT * FROM tenant_data;           -- only tenant 7's rows
INSERT INTO tenant_data (tenant_id, content) VALUES (7, 'safe');  -- OK
INSERT INTO tenant_data (tenant_id, content) VALUES (9, 'hack');  -- BLOCKED by policy
```

This demonstrates defense-in-depth: the application role has minimal privileges (no DDL), RLS enforces tenant isolation at the database level regardless of application bugs, and the forced policy applies even to the table owner.
