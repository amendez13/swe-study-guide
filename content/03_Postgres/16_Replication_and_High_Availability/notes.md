# Replication and High Availability

Replication keeps copies of your database on multiple servers for read scaling and disaster recovery. High availability adds automated failover so the system survives primary server failures without manual intervention.

## Key Points

- **Streaming replication** — primary ships WAL to standbys in real-time. Standbys are exact physical copies.
- **Sync vs async** — async is default (lower latency, small data loss window). Sync waits for standby confirmation (zero loss, higher latency).
- **WAL** — every change hits the WAL before data files. Foundation for crash recovery, replication, and PITR.
- **Hot standby** — a replica accepting read-only queries while replaying WAL. Monitor replication lag.
- **Logical replication** — row-level (not physical) replication. Selective tables, cross-version, writable subscriber. Use for migrations and data integration.
- **Failover** — promote a standby when primary fails. Patroni automates leader election and standby reconfiguration.

## Example

```sql
-- On the primary: create a publication for logical replication
CREATE PUBLICATION app_pub FOR TABLE orders, customers, products;

-- Check streaming replication status
SELECT client_addr, state, sent_lsn, write_lsn, replay_lsn,
       sent_lsn - replay_lsn AS replay_lag_bytes
FROM pg_stat_replication;

-- On a standby: verify it's in recovery mode
SELECT pg_is_in_recovery();        -- true
SELECT pg_last_wal_replay_lsn();   -- current replay position
SELECT now() - pg_last_xact_replay_timestamp() AS replay_lag;

-- On a subscriber: create subscription to selective tables
CREATE SUBSCRIPTION app_sub
    CONNECTION 'host=primary port=5432 dbname=app'
    PUBLICATION app_pub;

-- Monitor subscription status
SELECT subname, received_lsn, latest_end_lsn
FROM pg_stat_subscription;
```

This shows both monitoring streaming replication health (lag, LSN positions) and setting up logical replication for selective table synchronization between independent Postgres instances.
