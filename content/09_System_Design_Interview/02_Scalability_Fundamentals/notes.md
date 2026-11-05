# Scalability Fundamentals

How a system grows from one machine to a large fleet. The skill is naming the next bottleneck and the one lever that removes it. A diagram that already contains every later stage is answering a bigger problem than the one in front of you.

## Key Points

- **Vertical scaling** — a bigger machine, same code. Right first move for the app and for a database primary. The largest instance and a single failure domain are the stop signs.
- **Horizontal scaling** — more machines. The web tier needs a load balancer and a plan for state. Databases stay stateful and scale by replication and partitioning.
- **Stateless vs. stateful** — a stateless web process can be cloned because the request carries the identifier and the record lives elsewhere. Databases, caches, and connection state are stateful on purpose.
- **Shared session store** — sticky sessions pin a user to the worker that holds the session in memory. A shared store lets any worker load that session. The store is then a dependency with a TTL and, if logins must survive a restart, its own replica.
- **Describing load** — average and peak QPS, read/write ratio, working set, payload size, and growth. The ratio picks cache and replicas versus write partitioning.
- **Describing performance** — throughput is completed work per second; latency is one request's wait. p99 is the usual page. More servers raise throughput; a shorter path raises the tail.
- **Scale cube** — X clones a service, Y splits by function, Z splits by data. Name the axis that matches the measured limit.
- **Zero to millions** — single server, separate database, vertical then horizontal, load balancer, replication, cache, CDN for static bytes, stateless web tier, multi-data-center when one region is the ceiling, queues for slow work, logs and metrics to operate it, then further database scale. Stop at the stage the numbers require.

## Example

A read-heavy social feed. The day length is 86,400 seconds. A 3× peak is an assumption you would say out loud.

```python
SECONDS_PER_DAY = 86_400
DAU = 50_000_000
READS_PER_USER = 20
WRITES_PER_USER = 2
PEAK = 3

read_qps = DAU * READS_PER_USER / SECONDS_PER_DAY
write_qps = DAU * WRITES_PER_USER / SECONDS_PER_DAY
print(round(read_qps), round(read_qps * PEAK), round(write_qps), round(read_qps / write_qps))
# 11574 34722 1157 10


def feed_plan(read_qps: float, write_qps: float) -> list[str]:
    ratio = read_qps / write_qps
    plan = [
        "stateless web tier behind a load balancer",
        "sessions in a shared store, separate key prefix from the feed cache",
    ]
    if ratio >= 10:
        plan.append("cache the feed; a few read replicas for the misses")
    if write_qps < 5_000:
        plan.append("one write leader; partitioning waits")
    plan.append("CDN only for shared static assets, not per-user feed JSON")
    return plan


print(feed_plan(read_qps, write_qps))
```

About 12,000 average read QPS, about 35,000 at the peak, about 1,200 write QPS, and a 10:1 read/write ratio. That justifies a stateless web tier, a shared session store, a feed cache, and a few read replicas. It does not justify sharding the write path. Feed JSON is per-user, so it stays on the cache and database path; a CDN is for the shared images and scripts. A second region shows up only if distant users are part of the requirement. The signals you would alert on are cache hit ratio, replica lag, and feed p99. The logging pipeline is the Observability topic.

## Stage choice

| What you measured | Stage you add | Where the deep dive lives |
| --- | --- | --- |
| App and database comfortable on one host | Single server | This topic |
| Database CPU fighting the app | Separate the database | This topic, then the database topics for the engine |
| Largest instance, or the host must be allowed to die | Horizontal web tier and a load balancer | Load Balancing |
| Reads dominate, one leader | Replicas, then a cache | Relational Databases, Consistency, Caching |
| Shared images served far from users | CDN for those bytes | Caching; media pipelines in Content Distribution |
| Login dies with a web process | Shared session store | This topic |
| Distant users or one region as a disaster domain | Multi-data-center | High Availability |
| Request path waits on slow work | Queue | Message Queues |
| No signal after the new tier | Logs, metrics, automation | Observability |
| One primary's writes or disk are full | Partition | Data Partitioning |

## See also

- [Interview Framework and Process](../01_Interview_Framework_and_Process/) — the QPS and storage arithmetic these decisions start from.
- [High Availability and Reliability](../03_High_Availability_and_Reliability/) — multi-region failure and failover. There is no dedicated multi-data-center card yet.
- [Load Balancing](../04_Load_Balancing/) — algorithms, health checks, and how sticky sessions are implemented.
- [Caching](../05_Caching/) — cache patterns and the foundational CDN card.
- [Databases Relational](../06_Databases_Relational/) — replication, read replicas, and the primary's vertical ceiling.
- [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/) — when the data model is not relational, including a key-value session store.
- [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/) — shard keys and rebalancing.
- [Consistency and Replication](../09_Consistency_and_Replication/) — lag, quorums, and read-your-writes.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — taking slow work off the request path.
- [Content Distribution and Media](../22_Content_Distribution_and_Media/) — transcoding, adaptive bitrate, and CDN cost. Basic CDN stays in Caching.
- [Observability](../25_Observability/) — logs, metrics, and one deploy pipeline. This topic only names the stage.
