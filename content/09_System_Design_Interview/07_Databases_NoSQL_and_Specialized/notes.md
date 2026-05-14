# Databases — NoSQL and Specialized

The complement to relational databases. NoSQL databases trade SQL's query flexibility and strong consistency for horizontal scalability, flexible schemas, and specialized access patterns. Knowing when to reach for each type is critical in system design interviews because choosing the wrong database is one of the most common — and most consequential — mistakes.

## Key Points

- **Key-value store** — get/put/delete by key. Redis for caching, sessions, leaderboards, rate limiting. Memcached for simple caching. DynamoDB for persistent key-value at scale.
- **Document store** — semi-structured JSON documents with flexible schemas. MongoDB, DynamoDB. Good when schema varies per record or data is naturally hierarchical.
- **Column-family store** — data organized by column families, optimized for write-heavy and wide-row workloads. Cassandra for globally distributed writes, HBase for Hadoop-integrated analytics.
- **Graph database** — nodes and edges for relationship-heavy queries. Neo4j, Neptune. Use for social graphs, recommendations, fraud detection. Not for bulk scans or aggregations.
- **Time-series database** — append-heavy timestamped data with downsampling and retention. InfluxDB, TimescaleDB, Prometheus. Use for metrics, monitoring, IoT.
- **SQL vs. NoSQL** — not a binary choice. SQL for strong consistency, joins, complex queries. NoSQL for horizontal scale, flexible schemas, high throughput. Many systems use both.
- **Data warehousing** — column-oriented OLAP store for analytics and reporting. Redshift, BigQuery, Snowflake. Fed by ETL/CDC from the OLTP database.

## Example

Choosing databases for a social media platform:

```text
Requirements:
  - User profiles and relationships (friends, followers)
  - Posts with text, images, and comments
  - Activity feed showing recent posts from followed users
  - Real-time metrics dashboard for internal analytics
  - Full-text search across posts

Database choices:

  PostgreSQL (relational):
    Users, friendships, comments, likes.
    ACID for friend requests, like counts, comment threads.
    Strong consistency for social graph operations.

  Redis (key-value):
    Session store, feed cache, rate limiting.
    Sorted sets for "trending posts" leaderboard.

  Cassandra (column-family):
    Activity feed storage — write-heavy, append-only.
    Partition by user_id, cluster by timestamp.
    Each user's feed is a wide row of recent posts.

  Elasticsearch (inverted index):
    Full-text search across posts.
    Not a primary store — fed by CDC from PostgreSQL.

  TimescaleDB (time-series):
    Internal metrics: DAU, posts/hour, latency percentiles.
    Automatic downsampling for dashboard queries.

Total: 5 databases, each chosen for its access pattern.
```

This multi-database approach is standard in system design interviews for complex applications. The key is justifying each choice with the specific access pattern it serves.
