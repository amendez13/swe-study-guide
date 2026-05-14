# Storage and Data Processing at Scale

How to store and process data when it's too large for a single machine. This topic covers the spectrum from durable blob storage to real-time event processing. In system design interviews, you'll choose between these based on latency requirements, data volume, and whether the system needs results in seconds or hours.

## Key Points

- **Object storage** — key-blob store for media, backups, and data lake files. S3 is the default in interviews. 11 nines durability, unlimited scale, high first-byte latency.
- **Distributed file system** — HDFS for large sequential reads and batch processing. Largely replaced by S3 + Spark in modern architectures.
- **Batch processing** — process large datasets in scheduled jobs (Spark, MapReduce). High throughput, minutes-to-hours latency. Use for ETL, analytics, ML training.
- **Stream processing** — process events in real time (Kafka Streams, Flink). Low latency, continuous operation. Use for fraud detection, live dashboards, alerting.
- **Lambda architecture** — batch + speed layers for accuracy and freshness. Powerful but doubles code complexity. Kappa architecture (stream-only) is the simpler alternative.
- **Change data capture** — stream DB changes as events. Debezium reads WAL/binlog. Use to sync search indexes, caches, and warehouses without polling.
- **Event sourcing** — store every state change as an immutable event. Complete audit trail, temporal queries, easy to add new projections. Pairs with CQRS.

## Example

Data processing pipeline for a ride-sharing analytics platform:

```text
Real-time path (stream):
  Ride events (start, end, location updates) → Kafka
  → Flink stream processing
  → Real-time dashboard: active rides, avg wait time, surge pricing
  → Latency: seconds

Batch path:
  Nightly Spark job reads from S3 data lake
  → Computes: driver earnings, ride patterns, demand forecasting
  → Writes results to Redshift (data warehouse)
  → Latency: hours, but accurate and complete

CDC for search:
  PostgreSQL (rides, drivers) → Debezium CDC → Kafka
  → Elasticsearch consumer updates the driver search index
  → Passengers can search for nearby drivers in real-time

Storage:
  S3: ride GPS traces (100 GB/day), driver documents, receipts
  PostgreSQL: rides, users, payments (transactional data)
  Redis: active ride state, driver locations (low-latency reads)
  Redshift: historical analytics (months of aggregated data)
```

Different storage and processing choices for different latency and accuracy requirements — all feeding from the same event stream.
