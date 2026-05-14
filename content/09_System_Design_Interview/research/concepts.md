# System Design Interview Concepts

A distilled concept reference for studying system design interviews in software engineering, synthesized from the five resources in [course_outlines.md](course_outlines.md). The focus is on transferable knowledge: building blocks, trade-offs, and reasoning patterns that survive across interview prompts and production systems.

---

## 1. Interview Framework and Process

- **Four-step framework** — the standard structure: (1) clarify requirements and scope, (2) propose a high-level design and get buy-in, (3) deep dive into critical components, (4) wrap up with bottlenecks, failure modes, and operational concerns.
- **Functional vs. non-functional requirements** — functional requirements describe what the system does (features, user stories); non-functional requirements describe how it performs (latency, availability, durability, security). Both must be elicited before drawing boxes.
- **Back-of-the-envelope estimation** — quick capacity math using powers of two, latency numbers, and QPS/storage/bandwidth formulas to ground design decisions in realistic scale before committing to an architecture.
- **Trade-off articulation** — interviewers value explicit reasoning about competing constraints (consistency vs. availability, latency vs. throughput, cost vs. durability). Naming the trade-off is often more important than picking a side.
- **Working backwards from requirements** — start from what the user needs, derive the API contract, then work inward to services and storage rather than picking technologies first.

## 2. Scalability Fundamentals

- **Vertical scaling** — adding CPU, memory, or storage to a single machine; simple but limited by hardware ceilings and single points of failure.
- **Horizontal scaling** — adding more machines to distribute load; enables near-linear throughput growth but introduces coordination complexity (state sharing, data partitioning, service discovery).
- **Stateless vs. stateful services** — stateless services store no per-request state on the server, making them trivially horizontally scalable; stateful services (caches, databases, WebSocket servers) require sticky sessions or external state management.
- **Describing load** — quantifying a system's workload using key parameters (QPS, read/write ratio, peak-to-average traffic ratio, data volume) to make scaling decisions concrete rather than hand-wavy.
- **Describing performance** — measuring system response in terms of throughput (requests/second), latency (p50, p95, p99), and tail latency; the distinction between median and tail matters because outliers often drive user experience.

## 3. High Availability and Reliability

- **Availability and the nines** — availability is the fraction of time a system is operational, expressed as nines (99.9% = three nines ≈ 8.7 hours downtime/year); composite system availability multiplies component availabilities.
- **MTBF and MTTR** — Mean Time Between Failures and Mean Time To Repair; availability = MTBF / (MTBF + MTTR); reducing MTTR (fast detection, automated failover) is often more practical than increasing MTBF.
- **Redundancy and replication** — running multiple copies of a component so that failure of one does not take down the system; applies to servers, databases, network paths, and data centers.
- **Failover strategies** — cold standby (spin up on failure, slow), warm standby (running but not serving, moderate), hot standby (active and ready, fast failover but higher cost).
- **Active-active vs. active-passive** — active-active means all replicas serve traffic simultaneously (better utilization, more complex); active-passive means one serves traffic while the standby waits.
- **SLA, SLO, SLI** — Service Level Agreement is the contract with users; Service Level Objective is the internal target (e.g., 99.95% availability); Service Level Indicator is the measured metric. SLOs drive architecture decisions.

## 4. Load Balancing

- **Load balancer** — distributes incoming requests across multiple servers to spread load and provide failover; sits between clients and application servers.
- **DNS-level load balancing** — returns different IP addresses for the same domain; simple but coarse-grained and subject to DNS caching delays.
- **Layer 4 (transport) vs. Layer 7 (application) load balancing** — L4 routes by IP/port without inspecting content (fast); L7 routes by HTTP headers, URL paths, or cookies (flexible, content-aware routing).
- **Load balancing algorithms** — round robin, weighted round robin, least connections, IP hash, consistent hashing; the choice depends on whether sessions are sticky, requests are uniform, and backends are heterogeneous.
- **Health checks** — load balancers periodically probe backends to detect unhealthy instances and stop routing traffic to them.

## 5. Caching

- **Cache** — a fast-access storage layer that holds frequently or recently accessed data, reducing latency and backend load; effective when reads dominate writes and data access follows a power-law distribution.
- **Cache-aside (lazy loading)** — application reads cache first; on miss, reads from database and populates cache; the most common pattern for general-purpose caching.
- **Read-through and write-through** — the cache sits inline: read-through populates cache automatically on miss; write-through writes to cache and database synchronously, keeping them in sync at the cost of write latency.
- **Write-behind (write-back)** — writes go to cache immediately and are asynchronously flushed to the database; reduces write latency but risks data loss on cache failure.
- **Eviction policies** — LRU (Least Recently Used), LFU (Least Frequently Used), FIFO, TTL-based expiration; LRU is the default in most interview answers unless the access pattern suggests otherwise.
- **Cache invalidation** — the hard problem: ensuring cached data stays consistent with the source of truth; strategies include TTL, event-driven invalidation, and versioned keys.
- **CDN (Content Delivery Network)** — a globally distributed cache for static and dynamic content; edge servers serve content from locations physically close to users, reducing latency and origin load.

## 6. Databases — Relational

- **Relational database** — stores data in tables with fixed schemas, enforces relationships via foreign keys, and supports SQL for complex queries; the default choice when data is structured and consistency matters.
- **ACID properties** — Atomicity (all-or-nothing), Consistency (valid state transitions), Isolation (concurrent transactions don't interfere), Durability (committed data survives crashes); the defining guarantee of relational databases.
- **Normalization** — organizing data to eliminate redundancy and ensure referential integrity; reduces storage and update anomalies but can increase join complexity.
- **Indexing** — data structures (B-trees, hash indexes) that speed up read queries at the cost of write overhead and storage; choosing the right indexes is the single highest-leverage database optimization.
- **Database replication** — maintaining copies of data across multiple servers; leader-follower (one writer, many readers), multi-leader (multiple writers), and leaderless (quorum-based reads and writes).
- **Database sharding (partitioning)** — splitting data across multiple database instances by a shard key; distributes load and storage but complicates cross-shard queries and rebalancing.
- **Read replicas** — follower nodes that serve read traffic, scaling read throughput while the leader handles writes; introduces replication lag.

## 7. Databases — NoSQL and Specialized

- **Key-value store** — maps keys to opaque values; simple API (get, put, delete), highly scalable, used for caching (Redis, Memcached) and session storage.
- **Document store** — stores semi-structured documents (JSON/BSON); flexible schemas, good for heterogeneous data and rapid iteration (MongoDB, DynamoDB).
- **Column-family store** — organizes data by column families rather than rows; optimized for write-heavy workloads and wide-column access patterns (Cassandra, HBase).
- **Graph database** — models data as nodes and edges; efficient for relationship-heavy queries like social networks and recommendation engines (Neo4j).
- **Time-series database** — optimized for append-heavy, time-stamped data with fast range queries and downsampling (InfluxDB, TimescaleDB); used for metrics and monitoring.
- **SQL vs. NoSQL trade-offs** — SQL gives strong consistency, complex queries, and joins; NoSQL gives flexible schemas, horizontal scalability, and tunable consistency; the interview answer is always "it depends on the access pattern."
- **Data warehousing** — a separate analytical store (star/snowflake schema, column-oriented storage) designed for OLAP queries over large datasets; decouples analytics from the transactional system.

## 8. Data Partitioning and Consistent Hashing

- **Horizontal partitioning (sharding)** — distributing rows across shards by a partition key; the key choice determines data locality and hotspot risk.
- **Range partitioning** — assigns contiguous key ranges to shards; supports efficient range queries but can create hotspots if keys are not uniformly distributed.
- **Hash partitioning** — hashes the key and maps it to a shard; distributes data more uniformly but sacrifices range query efficiency.
- **Consistent hashing** — a ring-based scheme where adding or removing a node only reassigns a fraction of keys; avoids the full rehash problem of naive modular hashing.
- **Virtual nodes (vnodes)** — each physical node maps to multiple positions on the hash ring, improving load distribution and simplifying rebalancing when nodes are added or removed.
- **Rebalancing** — the process of redistributing data when the cluster grows or shrinks; must be done without downtime or significant performance degradation.
- **Request routing** — how a client finds the right shard: approaches include client-side routing (client knows the partition map), routing tier (a proxy), and gossip-based discovery.

## 9. Consistency and Replication

- **CAP theorem** — in a network partition, a distributed system must choose between consistency (every read sees the latest write) and availability (every request gets a response); practical systems operate on a spectrum.
- **PACELC theorem** — extends CAP: even when there is no partition (else), the system trades off between latency and consistency; a more practical model for everyday design decisions.
- **Strong consistency** — after a write completes, all subsequent reads reflect it; simplifies application logic but limits availability and increases latency.
- **Eventual consistency** — replicas converge to the same state eventually but may serve stale reads in the interim; the default for most globally distributed systems.
- **Read-after-write consistency** — a user always sees their own writes; achieved by routing reads for recently-written data to the leader or using timestamps.
- **Quorum reads and writes** — requiring W + R > N (where N is replica count) guarantees overlap between write and read sets; tunable consistency by adjusting W and R.
- **Conflict resolution** — when concurrent writes create divergent state: last-write-wins (simple, lossy), vector clocks (precise, complex), and application-level merge (domain-specific).
- **Linearizability** — the strongest consistency model: operations appear to take effect at a single instant between invocation and response; required for leader election and distributed locking.

## 10. Networking and Communication

- **REST** — resource-oriented API style over HTTP; stateless, cacheable, widely understood; the default for public-facing APIs.
- **RPC (Remote Procedure Call)** — calling a remote function as if local; frameworks like gRPC use Protocol Buffers for efficient serialization and support streaming.
- **REST vs. RPC** — REST is better for CRUD resources and public APIs; RPC is better for internal service-to-service communication with complex operations and strict schemas.
- **API Gateway** — a single entry point that routes requests, handles cross-cutting concerns (auth, rate limiting, logging), and abstracts backend service topology from clients.
- **Proxy vs. reverse proxy** — a forward proxy acts on behalf of clients (hiding their identity); a reverse proxy acts on behalf of servers (load balancing, SSL termination, caching).
- **Long-polling, WebSockets, SSE** — long-polling: client holds a request open until the server has data; WebSockets: persistent bidirectional channel; SSE: server pushes events over HTTP. Choose based on whether communication is unidirectional or bidirectional.
- **Idempotency** — an operation that produces the same result when called multiple times; critical for API design in distributed systems where retries are expected.

## 11. Message Queues and Asynchronous Processing

- **Message queue** — decouples producers from consumers with a buffer; enables asynchronous processing, load leveling, and fault isolation.
- **Point-to-point vs. pub/sub** — point-to-point: each message is consumed by exactly one consumer; pub/sub: each message is delivered to all subscribers of a topic.
- **Message delivery guarantees** — at-most-once (fire and forget), at-least-once (retry with potential duplicates), exactly-once (hardest, usually achieved with idempotent consumers).
- **Consumer groups** — multiple consumers sharing a topic's partitions so that each message is processed by one consumer in the group; scales consumption horizontally.
- **Backpressure** — when a consumer can't keep up, the system must slow producers, buffer messages, or drop; an explicit backpressure mechanism prevents cascading failures.
- **Dead letter queue** — messages that repeatedly fail processing are moved to a separate queue for investigation rather than blocking the main pipeline.

## 12. Microservices and System Decomposition

- **Monolith vs. microservices** — a monolith is a single deployable unit (simple, fast to start); microservices decompose functionality into independently deployable services (scalable per-service, team-aligned, but operationally complex).
- **Service boundaries** — deciding what gets its own service; align with bounded contexts (domain-driven design) to minimize cross-service coupling and data sharing.
- **Multi-tier architecture** — separating a system into presentation, application, and data tiers; the foundation for most web architectures.
- **Event-driven architecture** — services communicate through events rather than direct calls; improves decoupling, scalability, and auditability but makes the system harder to trace and debug.
- **Service discovery** — how services find each other's network locations; client-side (the caller queries a registry) or server-side (a load balancer routes to the right instance).

## 13. Storage and Data Processing at Scale

- **Object storage** — stores data as objects (key → blob + metadata) rather than files or blocks; designed for durability and scale (S3-style); the default for media, backups, and large datasets.
- **Distributed file system** — a file system spanning multiple machines (HDFS); optimized for large sequential reads and batch processing.
- **Batch processing** — processing large datasets in scheduled jobs (MapReduce, Spark); high throughput, high latency; suitable for analytics, ETL, and offline computation.
- **Stream processing** — processing events in real time as they arrive (Kafka Streams, Flink); low latency, lower throughput per event; suitable for monitoring, alerting, and real-time aggregation.
- **Lambda architecture** — combines a batch layer (accurate, slow) with a speed layer (approximate, fast) and a serving layer; addresses the latency–accuracy trade-off but doubles complexity.
- **Change data capture (CDC)** — streaming database changes as events to downstream consumers; enables derived data systems to stay in sync without polling.
- **Event sourcing** — storing every state change as an immutable event rather than overwriting current state; provides a complete audit trail and enables temporal queries.

## 14. Encoding, Serialization, and Schema Evolution

- **JSON and XML** — human-readable, widely supported, schema-optional; good for APIs and configuration; verbose and slower to parse than binary formats.
- **Protocol Buffers and Thrift** — binary serialization with explicit schemas and code generation; compact, fast, and support schema evolution with field numbering.
- **Avro** — binary format with schema stored alongside data; supports schema evolution without field numbers; used in data pipelines and Hadoop ecosystems.
- **Schema evolution** — the ability to change a data format (add fields, remove fields) without breaking readers or writers; backward and forward compatibility rules differ by format.

## 15. Distributed System Failure Modes

- **Partial failures** — in a distributed system, some components fail while others continue; the system must tolerate this rather than treating it as all-or-nothing.
- **Unreliable networks** — packets can be lost, delayed, duplicated, or reordered; timeouts are the primary detection mechanism but cannot distinguish slow from dead.
- **Unreliable clocks** — physical clocks drift and cannot be perfectly synchronized; relying on wall-clock time for ordering events across machines is unsafe without specialized protocols (NTP, TrueTime).
- **Byzantine faults** — a node behaves arbitrarily or maliciously; most internal systems assume crash-stop failures and do not defend against Byzantine behavior.
- **Split brain** — a partition where both sides believe they are the leader, causing conflicting writes; prevented by fencing tokens, quorum-based leader election, or consensus protocols.

## 16. Transactions and Concurrency Control

- **Transaction** — a unit of work that either fully completes or fully aborts; the abstraction that shields application developers from concurrency and failure complexity.
- **Isolation levels** — read committed (no dirty reads/writes), repeatable read / snapshot isolation (consistent point-in-time view), serializable (as if transactions ran one at a time); each level trades performance for safety.
- **Optimistic vs. pessimistic concurrency** — optimistic: proceed and detect conflicts at commit time (good when conflicts are rare); pessimistic: acquire locks before operating (good when conflicts are frequent).
- **Two-phase locking (2PL)** — a pessimistic protocol: acquire all locks in a growing phase, release in a shrinking phase; guarantees serializability but can deadlock.
- **Two-phase commit (2PC)** — a distributed commit protocol with a prepare phase and a commit phase; ensures atomicity across multiple nodes but blocks if the coordinator fails.
- **Consensus algorithms** — protocols (Paxos, Raft, Zab) that allow distributed nodes to agree on a value despite failures; the foundation for leader election, distributed locking, and coordination services like ZooKeeper.

## 17. Rate Limiting and Throttling

- **Rate limiter** — controls the rate of requests a client or service can make; protects against abuse, prevents cascading overload, and enforces fair usage.
- **Token bucket** — tokens accumulate at a fixed rate; each request consumes a token; allows short bursts up to the bucket capacity.
- **Leaky bucket** — requests enter a queue processed at a fixed rate; smooths bursts but may queue-delay bursty traffic.
- **Fixed window counter** — counts requests in fixed time windows; simple but allows burst at window boundaries.
- **Sliding window** — sliding window log (exact but memory-heavy) or sliding window counter (approximate but efficient); smooths the boundary problem of fixed windows.

## 18. Search, Autocomplete, and Information Retrieval

- **Inverted index** — maps terms to the documents containing them; the core data structure behind full-text search engines (Elasticsearch, Solr).
- **Trie (prefix tree)** — a tree where each path from root to node represents a prefix; the foundation for autocomplete and typeahead suggestion systems.
- **Search autocomplete system** — combines a trie (or similar prefix structure) with frequency/ranking data; a data gathering service updates the trie from query logs while a query service serves suggestions with low latency.
- **Relevance ranking** — ordering search results by relevance using signals like TF-IDF, BM25, click-through rate, and personalization.

## 19. Unique ID Generation

- **UUID** — 128-bit universally unique identifier; simple, no coordination needed, but not sortable by time and wastes index space.
- **Snowflake ID** — a 64-bit ID encoding timestamp, datacenter, machine, and sequence number; time-sortable, roughly unique, used by Twitter and derivatives.
- **Ticket server** — a centralized or sharded auto-increment service; simple and sequential but introduces a single point of failure or coordination overhead.
- **Database auto-increment** — works for single-node systems; breaks down when sharding because sequences must be coordinated or offset.

## 20. Geospatial and Location-Based Services

- **Geohash** — encodes latitude and longitude into a string where shared prefixes indicate proximity; enables range queries with standard indexes.
- **Quadtree** — recursively subdivides 2D space into quadrants; adapts resolution to data density; used for spatial indexing in proximity services.
- **Google S2** — maps the sphere to a Hilbert curve, producing 64-bit cell IDs with locality-preserving properties; used in Google Maps and similar systems.
- **Proximity service** — returns nearby points of interest; combines a geospatial index with a database of locations; read-heavy with relatively static data.

## 21. Real-Time and Notification Systems

- **Push notification system** — delivers messages to mobile and web clients via platform-specific channels (APNs, FCM); requires device token management, retry logic, and rate limiting.
- **Notification service** — a centralized system that dispatches across multiple channels (push, SMS, email) with templates, user preferences, and delivery tracking.
- **Presence / online status** — tracking which users are currently online; uses heartbeats or WebSocket connection state; must tolerate flapping connections gracefully.
- **Fan-out** — distributing an event to many recipients; fan-out on write (push to all followers at write time, fast reads) vs. fan-out on read (pull at read time, fast writes).

## 22. Content Distribution and Media

- **Video uploading and transcoding** — uploaded videos are split into chunks, transcoded into multiple resolutions and formats via a DAG processing pipeline, then stored for streaming.
- **Adaptive bitrate streaming** — the player switches between quality levels based on network conditions; requires pre-transcoded variants and a manifest file (HLS, DASH).
- **CDN cost optimization** — serving popular content from CDN, long-tail content from origin; choosing CDN tiers and regions based on traffic patterns.
- **File sync and conflict resolution** — cloud storage systems (Google Drive, Dropbox) use block-level deduplication, metadata databases, and notification services to sync files across devices; conflicts require merge or manual resolution.

## 23. Payment and Financial Systems

- **Idempotency in payments** — every payment operation must be idempotent to handle retries safely; typically implemented with idempotency keys stored on the server.
- **Payment Service Provider (PSP) integration** — the system delegates actual money movement to a PSP (Stripe, Adyen); the design focuses on the orchestration, webhook handling, and reconciliation.
- **Double-entry bookkeeping** — every transaction creates a debit and a credit entry; ensures the ledger always balances and provides a complete audit trail.
- **Reconciliation** — periodic comparison of internal records against PSP records and bank statements to detect and resolve discrepancies.

## 24. Classic Design Problems — Patterns to Recognize

- **URL shortener** — hash or counter-based short code generation, 301 vs 302 redirects, analytics; exercises hashing, storage, and read-heavy scaling.
- **Chat system** — WebSocket connections, message storage and sync, group chat fan-out, presence; exercises real-time communication and eventual consistency.
- **News feed / timeline** — fan-out on write vs. read, ranking, caching hot users; exercises the read/write trade-off at social-network scale.
- **Web crawler** — URL frontier with politeness and priority, content deduplication, BFS traversal; exercises distributed coordination and duplicate detection.
- **Distributed key-value store** — partitioning, replication, consistency model, failure detection (gossip protocol); exercises the CAP trade-off end-to-end.
- **Metrics monitoring system** — push vs. pull collection, time-series storage, alerting rules; exercises write-heavy ingestion and aggregation.
- **Ticket booking system** — concurrency control for limited inventory, overbooking policies, optimistic vs. pessimistic locking; exercises transaction isolation under contention.
- **Stock exchange / matching engine** — order book, FIFO matching, sequencer, low-latency design; exercises the extreme end of performance-sensitive architecture.

---

## Self-Check

For each concept above, verify you can:

1. **Explain it** — define the concept in one or two sentences without looking at notes.
2. **Recognize it** — identify when a design problem calls for this concept (e.g., "this is a fan-out on write problem" or "we need consistent hashing here").
3. **Apply it** — sketch how you would use it in a whiteboard design, including the trade-offs you're accepting.
4. **Compare alternatives** — name at least one alternative approach and articulate why you would or wouldn't choose it for a given scenario.
