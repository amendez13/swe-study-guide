# Backup, Recovery, and Migrations

Protecting data requires a backup strategy (what to back up and how), a recovery plan (restoring to a specific point in time), and controlled schema evolution through migrations. Getting these wrong is how you lose data or break production.

## Key Points

- **pg_dump / pg_restore** — logical backup. Custom format (-Fc) supports parallel restore and selective extraction. Works across minor versions.
- **COPY** — bulk data transfer. 10-100x faster than INSERT for large loads. Server-side (COPY) vs client-side (\copy).
- **Base backup + PITR** — physical backup with WAL archiving. Restore to any point in time for disaster recovery.
- **Schema migrations** — versioned, reversible DDL scripts. One change per migration; test downgrade paths.
- **Schema vs data migrations** — schema changes are fast (metadata); data migrations touch rows and should be batched for large tables.
- **Migration tools** — Alembic (Python), Flyway (Java), golang-migrate, node-pg-migrate. All track applied migrations.

## Example

```bash
# Daily backup workflow

# 1. Full logical backup (custom format, compressed)
pg_dump -Fc -f /backup/daily/mydb_$(date +%Y%m%d).dump mydb

# 2. Verify the backup is readable
pg_restore -l /backup/daily/mydb_$(date +%Y%m%d).dump > /dev/null

# 3. Restore to a test database for verification
createdb mydb_verify
pg_restore -d mydb_verify -j 4 /backup/daily/mydb_$(date +%Y%m%d).dump
psql mydb_verify -c "SELECT count(*) FROM orders;"
dropdb mydb_verify
```

```sql
-- Bulk data load with COPY
BEGIN;
  TRUNCATE staging_orders;
  COPY staging_orders FROM '/data/orders_export.csv' WITH (FORMAT csv, HEADER);
  -- Verify row count
  SELECT count(*) FROM staging_orders;
COMMIT;
```

This shows a backup workflow with verification (dump → list → restore to test db → spot-check), plus a transactional bulk load using COPY with a truncate-and-reload pattern.
