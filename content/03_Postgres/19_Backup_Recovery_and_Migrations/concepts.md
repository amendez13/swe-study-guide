## `pg_dump` and `pg_restore`

Logical backup and restore. `pg_dump` exports a database (or selected tables) as SQL statements or a custom-format archive. `pg_restore` reloads it. Works across minor versions and supports selective restore.

```bash
# Dump entire database in custom format (compressed, supports parallel restore)
pg_dump -Fc -f backup.dump mydb

# Dump specific tables as plain SQL
pg_dump -t orders -t customers --format=plain mydb > orders.sql

# Restore from custom format
pg_restore -d mydb backup.dump

# Parallel restore (faster on multi-core)
pg_restore -d mydb -j 4 backup.dump

# List contents of a dump without restoring
pg_restore -l backup.dump
```

Custom format (`-Fc`) is preferred over plain SQL because it's compressed, supports parallel restore, and allows selective table/schema restore. Plain SQL (`-Fp`) is useful when you need a human-readable script or want to pipe into `psql`.

## COPY command

Bulk data transfer between tables and files. Orders of magnitude faster than row-by-row INSERT for loading large datasets.

```sql
-- Export to CSV
COPY orders TO '/tmp/orders.csv' WITH (FORMAT csv, HEADER true);

-- Import from CSV
COPY orders (customer_id, total, status)
FROM '/tmp/orders.csv' WITH (FORMAT csv, HEADER true);

-- From stdin (useful with psql or client libraries)
COPY products (name, price) FROM stdin WITH (FORMAT csv);
Widget,9.99
Gadget,19.99
\.
```

`COPY` is a server-side command (reads/writes files on the server). `\copy` in psql does the same but transfers data through the client connection — necessary when you don't have filesystem access to the server.

For very large loads, disable indexes and constraints first, then COPY, then rebuild indexes. Wrap in a transaction for atomicity.

## Base backups and Point-In-Time Recovery

`pg_basebackup` takes a physical snapshot of the entire cluster. Combined with WAL archiving, you can restore to any point in time — recovering from accidental data deletion or corruption.

```bash
# Take a base backup
pg_basebackup -D /backup/base -Ft -z -P

# Continuous WAL archiving (in postgresql.conf)
# archive_mode = on
# archive_command = 'cp %p /backup/wal/%f'
```

```mermaid
flowchart LR
    A[Base backup<br/>Monday 2am] --> B[WAL archive<br/>Mon-Wed]
    B --> C[Restore to<br/>Wednesday 3:47pm]
```

PITR restore: copy the base backup, configure `recovery_target_time`, point to the WAL archive, and start Postgres. It replays WAL from the backup to the target time, giving you the exact database state at that moment.

## Schema migrations

Versioned, reversible scripts that evolve the database schema alongside application code. Each migration has an upgrade and downgrade path, runs exactly once, and is tracked in a migrations table.

```python
# Alembic migration example
def upgrade():
    op.add_column('orders', sa.Column('shipped_at', sa.DateTime))
    op.create_index('idx_orders_shipped', 'orders', ['shipped_at'])

def downgrade():
    op.drop_index('idx_orders_shipped')
    op.drop_column('orders', 'shipped_at')
```

Migration best practices:
- One schema change per migration (easier to debug and roll back)
- Test both upgrade and downgrade paths
- Use `CREATE INDEX CONCURRENTLY` in migrations against production databases
- Never mix schema changes and data changes in the same migration

## Schema vs data migrations

Schema migrations change structure (ADD COLUMN, CREATE TABLE, CREATE INDEX). Data migrations transform existing data. They have different risk profiles and execution patterns.

```sql
-- Schema migration: fast, metadata-only in many cases
ALTER TABLE users ADD COLUMN email_verified boolean DEFAULT false;

-- Data migration: touches every row, generates WAL, can be slow
UPDATE users SET email_verified = true
WHERE verified_at IS NOT NULL;
```

For large tables, data migrations should run in batches to avoid long-running transactions, WAL spikes, and lock contention:

```sql
-- Batch update pattern
DO $$
DECLARE
    batch_size integer := 10000;
    updated integer;
BEGIN
    LOOP
        UPDATE users SET email_verified = true
        WHERE id IN (
            SELECT id FROM users
            WHERE verified_at IS NOT NULL AND email_verified IS NULL
            LIMIT batch_size
        );
        GET DIAGNOSTICS updated = ROW_COUNT;
        RAISE NOTICE 'Updated % rows', updated;
        EXIT WHEN updated = 0;
        COMMIT;  -- requires a procedure (PG 11+) or external batching
    END LOOP;
END $$;
```

## Migration tools

Choose a migration tool that matches your stack. All follow the same pattern: numbered migrations, a tracking table, and upgrade/downgrade commands.

| Tool | Ecosystem | Key feature |
|------|-----------|-------------|
| **Alembic** | Python / SQLAlchemy | Auto-generates migrations from model diffs |
| **Flyway** | Java / JVM | SQL-based, no ORM dependency |
| **golang-migrate** | Go | Database-agnostic, CLI-driven |
| **node-pg-migrate** | Node.js | JS-based migrations, simple API |
| **Django migrations** | Python / Django | Tightly integrated with Django ORM |

```bash
# Alembic
alembic upgrade head
alembic downgrade -1

# Flyway
flyway migrate
flyway undo

# golang-migrate
migrate -path ./migrations -database $DB_URL up
migrate -path ./migrations -database $DB_URL down 1
```
