## Key-Value Store

Maps keys to opaque values with a minimal API: get, put, delete. The simplicity of the interface enables extreme scalability and low latency.

```text
API:
  GET(key)          → value
  PUT(key, value)   → ok
  DELETE(key)       → ok

Use cases:
  Session storage, caching, feature flags, rate limiting counters

Examples:
  Redis    — in-memory, supports data structures (lists, sets, sorted sets)
  Memcached — in-memory, simpler, multi-threaded
  DynamoDB — managed, persistent, serverless pricing
```

In interviews, Redis is the go-to answer for any "we need a fast lookup" requirement: session store, cache, leaderboard (sorted sets), pub/sub, and rate limiter (atomic counters with TTL).

## Document Store

Stores semi-structured documents (typically JSON or BSON) where each document can have a different shape. No fixed schema — fields can vary between documents in the same collection.

```json
// MongoDB document — no fixed schema
{
  "_id": "order_789",
  "user_id": "user_42",
  "items": [
    { "product": "Keyboard", "qty": 1, "price": 79.99 },
    { "product": "Mouse", "qty": 2, "price": 29.99 }
  ],
  "shipping": { "address": "123 Main St", "method": "express" },
  "status": "shipped"
}
```

```text
When to choose:
  ✓ Schema varies per record or evolves frequently
  ✓ Data is naturally hierarchical (nested objects, arrays)
  ✓ Read pattern is "fetch one document by ID"
  ✗ Poor fit when you need joins across documents
  ✗ Poor fit when you need multi-document transactions

Examples: MongoDB, Amazon DynamoDB, Couchbase, Firestore
```

## Column-Family Store

Organizes data by column families rather than rows. Data for a single row is spread across column families, and each column family can be stored and compressed independently.

```text
Row key: user_42
  Column family "profile":  { name: "Alex", email: "alex@..." }
  Column family "activity": { last_login: "2024-03-15", posts: 142 }
  Column family "settings": { theme: "dark", language: "en" }
```

```text
When to choose:
  ✓ Write-heavy workloads (event logging, time-series, IoT)
  ✓ Wide rows with many columns
  ✓ Distributed, multi-region deployments
  ✗ Not designed for complex queries or ad-hoc joins

Examples: Apache Cassandra, HBase, Google Bigtable
```

Cassandra is the interview go-to for write-heavy, globally distributed data like activity feeds, messaging, and IoT telemetry. It uses a leaderless architecture with tunable consistency.

## Graph Database

Models data as nodes (entities) and edges (relationships). Optimized for traversal queries where the structure of relationships is more important than the properties of individual records.

```text
Nodes:  User, Post, Product, Tag
Edges:  FOLLOWS, LIKED, PURCHASED, TAGGED_WITH

Query: "Find all users who are friends of friends of User A
        who also liked Product X"
  → In SQL: multiple self-joins, slow at depth
  → In a graph DB: natural traversal, fast at any depth
```

```text
When to choose:
  ✓ Relationship-heavy queries (social graphs, recommendations)
  ✓ Variable-depth traversals (shortest path, connected components)
  ✓ Knowledge graphs, fraud detection, permission models
  ✗ Not great for aggregations, bulk scans, or OLAP

Examples: Neo4j, Amazon Neptune, JanusGraph
```

## Time-Series Database

Optimized for append-heavy, time-stamped data with fast range queries, downsampling, and retention policies. The data model is (metric_name, timestamp, value, tags).

```text
Example data points:
  cpu.usage host=web01 region=us-east  1710000000  72.5
  cpu.usage host=web01 region=us-east  1710000010  74.1
  cpu.usage host=web02 region=us-east  1710000000  45.2

Typical queries:
  "Average CPU across all hosts in us-east for the last hour"
  "95th percentile latency for /api/orders over 7 days"

Features:
  Automatic downsampling (5s granularity → hourly averages)
  Retention policies (delete data older than 90 days)
  Compression optimized for time-series patterns (delta encoding)
```

```text
Examples: InfluxDB, TimescaleDB, Prometheus, Amazon Timestream
```

Use when designing metrics monitoring, alerting, IoT dashboards, or any system that collects measurements over time.

## SQL vs. NoSQL Trade-Offs

The interview answer is always "it depends on the access pattern." Know which properties each side optimizes for.

```text
                 SQL (Relational)         NoSQL
─────────────────────────────────────────────────────────
Schema           Fixed, enforced          Flexible, per-record
Consistency      Strong (ACID)            Tunable (eventual default)
Scaling          Vertical + read replicas Horizontal (built-in)
Joins            Native, efficient        Expensive or unsupported
Query language   SQL (standardized)       Varies by database
Transactions     Multi-row, ACID          Limited (often single-doc)
Best for         Complex queries,         High throughput, flexible
                 relationships, integrity  schemas, horizontal scale
```

Many real systems use both: a relational database for transactional data (orders, users, payments) and a NoSQL store for complementary workloads (session cache in Redis, activity feed in Cassandra, search in Elasticsearch).

## Data Warehousing

A separate analytical store designed for OLAP (Online Analytical Processing) queries over large datasets. It decouples analytics from the transactional (OLTP) system so heavy analytical queries don't impact user-facing performance.

```text
OLTP (transactional):             OLAP (analytical):
  Short queries, many per second    Long queries, few per hour
  Read + write individual rows      Read millions of rows
  Latest state                      Historical trends
  Row-oriented storage              Column-oriented storage

Schema patterns:
  Star schema:      central fact table + dimension tables
  Snowflake schema: star schema with normalized dimensions
```

```text
Examples: Amazon Redshift, Google BigQuery, Snowflake, ClickHouse
```

In system design interviews, mention a data warehouse when the requirements include analytics, reporting, or dashboards over historical data. ETL pipelines or CDC streams feed data from the OLTP database to the warehouse.
