## SQL injection

Constructing queries by string concatenation lets attackers inject arbitrary SQL — reading, modifying, or deleting data they shouldn't access.

```python
# VULNERABLE: string concatenation
query = f"SELECT * FROM users WHERE email = '{user_input}'"
# If user_input = "'; DROP TABLE users; --"
# Executes: SELECT * FROM users WHERE email = ''; DROP TABLE users; --'

# SAFE: parameterized query
cur.execute("SELECT * FROM users WHERE email = %s", (user_input,))
```

Parameterized queries send the SQL structure and values separately. The database never interprets parameter values as SQL code. This is the only reliable defense — input sanitization and escaping are fragile and error-prone.

Every database client library supports parameterized queries. There is never a legitimate reason to concatenate user input into SQL strings.

## Roles and privileges

Postgres uses roles for both users and groups. Privileges are granted at the database, schema, table, column, and function level using GRANT/REVOKE.

```sql
-- Create a role for the application
CREATE ROLE app_user LOGIN PASSWORD 'secret';

-- Grant connect and schema usage
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;

-- Table-level: read and write
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Column-level: restrict sensitive columns
GRANT SELECT (id, name, email) ON users TO reporting_role;
-- reporting_role cannot SELECT password_hash

-- Role inheritance (group roles)
CREATE ROLE readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
GRANT readonly TO app_user;  -- app_user inherits readonly privileges
```

Principle of least privilege: grant only what each role needs. The application role shouldn't have DROP TABLE or CREATE permissions if it only does CRUD. Use separate roles for migrations (DDL) and application runtime (DML).

## Row-Level Security (RLS)

Policies that filter rows per-user at the database level. Enables multi-tenant isolation without application-side WHERE clauses — even if the application has a bug that omits the tenant filter, the database enforces it.

```sql
-- Enable RLS on the table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy: users can only see their own documents
CREATE POLICY user_documents ON documents
    USING (owner_id = current_setting('app.current_user_id')::integer);

-- Policy: users can only insert documents they own
CREATE POLICY user_insert ON documents
    FOR INSERT
    WITH CHECK (owner_id = current_setting('app.current_user_id')::integer);

-- Application sets the user context before queries
SET app.current_user_id = '42';
SELECT * FROM documents;  -- automatically filtered to owner_id = 42
```

RLS policies are transparent — the application queries the table normally and Postgres silently appends the policy condition. Table owners bypass RLS by default; use `ALTER TABLE ... FORCE ROW LEVEL SECURITY` to apply policies to owners too.

## Prepared statements

Pre-compiled query templates with parameter placeholders. Prevent injection (parameters are never interpreted as SQL) and can improve performance by reusing query plans.

```sql
-- SQL-level prepared statement
PREPARE get_user (integer) AS
    SELECT id, name, email FROM users WHERE id = $1;

EXECUTE get_user(42);
EXECUTE get_user(99);

DEALLOCATE get_user;
```

In practice, prepared statements are managed by client libraries automatically:

```python
# psycopg2/3 uses server-side prepared statements automatically
# for repeated queries with the same SQL structure
cur.execute("SELECT * FROM orders WHERE customer_id = %s", (42,))
# Internally: PREPARE + EXECUTE (or extended query protocol)
```

Prepared statements also prevent plan-caching issues: in PgBouncer transaction mode, named prepared statements don't work because each transaction may use a different backend connection. Use protocol-level prepared statements or avoid named prepares with PgBouncer.

## SSL/TLS connections

Encrypt client-server traffic to prevent eavesdropping and man-in-the-middle attacks.

```bash
# Client connection with SSL verification
psql "host=db.example.com dbname=mydb sslmode=verify-full sslrootcert=/path/to/ca.pem"
```

| sslmode | Encryption | Server verification | Use case |
|---------|-----------|-------------------|----------|
| `disable` | No | No | Testing only |
| `require` | Yes | No (trusts any cert) | Better than nothing |
| `verify-ca` | Yes | Checks CA signature | Internal PKI |
| `verify-full` | Yes | CA + hostname match | Production |

Always use `verify-full` in production — `require` encrypts traffic but doesn't prevent MITM attacks (an attacker can present their own certificate). Configure `ssl = on` in `postgresql.conf` and provide a valid TLS certificate on the server.
