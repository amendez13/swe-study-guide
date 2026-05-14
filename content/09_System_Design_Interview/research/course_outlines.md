# System Design Interview Course Outlines

Five highly rated system design interview resources with full curriculum breakdowns. These span interactive courses, books-with-platforms, and a Udemy production-architecture course, covering both the interview framework and the distributed systems knowledge that underpins strong answers.

---

## 1. Grokking the System Design Interview

**Platform:** DesignGurus.io
**Instructor(s):** Arslan Ahmad (ex-FAANG hiring manager)
**Rating:** 4.7/5 (57,763 ratings, 172,834+ learners)
**Duration:** ~20 hours study time, 83 lessons across 5 chapters
**URL:** https://www.designgurus.io/course/grokking-the-system-design-interview

### Curriculum

#### Chapter 1: Introduction to System Design Interview (5 lessons)
- What is a System Design Interview?
- Functional vs. Non-functional Requirements
- What are Back-of-the-Envelope Estimations?
- Things to Avoid During System Design Interview
- Quiz

#### Chapter 2: Glossary of System Design Basics (20 lessons)
- System Design Basics
- Key Characteristics of Distributed Systems
- Load Balancing
- Load Balancing Algorithms
- Caching
- Data Partitioning
- Indexes
- Proxies
- Redundancy and Replication
- SQL vs. NoSQL
- CAP Theorem
- PACELC Theorem
- Consistent Hashing
- Long-Polling vs WebSockets vs Server-Sent Events
- Bloom Filters
- Quorum
- Leader and Follower
- Heartbeat
- Checksum
- Quiz

#### Chapter 3: System Design Trade-offs (23 lessons)
- Importance of Discussing Trade-offs
- Strong vs Eventual Consistency
- Latency vs Throughput
- ACID vs BASE Properties in Databases
- Read-Through vs Write-Through Cache
- Batch Processing vs Stream Processing
- Load Balancer vs. API Gateway
- API Gateway vs Direct Service Exposure
- Proxy vs. Reverse Proxy
- API Gateway vs. Reverse Proxy
- SQL vs. NoSQL
- Primary-Replica vs Peer-to-Peer Replication
- Data Compression vs Data Deduplication
- Server-Side Caching vs Client-Side Caching
- REST vs RPC
- Polling vs. Long-Polling vs. WebSockets vs. Webhooks
- CDN Usage vs Direct Server Serving
- Serverless Architecture vs Traditional Server-based
- Stateful vs Stateless Architecture
- Hybrid Cloud Storage vs All-Cloud Storage
- Token Bucket vs Leaky Bucket
- Read Heavy vs Write Heavy System
- Quiz

#### Chapter 4: System Design Problems (33 lessons)
- System Design Interviews — A step by step guide
- System Design Master Template
- Designing a URL Shortening Service like TinyURL
- Designing Pastebin
- Designing Instagram
- Designing Dropbox
- Designing Facebook Messenger
- Designing Twitter
- Designing Youtube or Netflix
- Designing Typeahead Suggestion
- Designing an API Rate Limiter
- Designing Twitter Search
- Designing a Web Crawler
- Designing Facebook's Newsfeed
- Designing Yelp or Nearby Friends
- Designing Uber backend
- Designing Ticketmaster
- (Each design is followed by a quiz)
- Additional Resources

#### Chapter 5: Appendix (2 lessons)
- Contact Us
- Other courses

---

## 2. System Design Interview — An Insider's Guide (Volumes 1 & 2)

**Platform:** ByteByteGo (book + online course)
**Author(s):** Alex Xu; Sahn Lam (Volume 2 co-author)
**Rating:** 4.26/5 on Goodreads (3,463 ratings); widely cited as the standard interview-prep reference
**Duration:** 324 pages (Vol 1) + ~350 pages (Vol 2); online course adds illustrations and bonus material
**URL:** https://bytebytego.com/

### Curriculum

#### Volume 1 — Foundations and Classic Problems

##### Chapter 1: Scale From Zero To Millions Of Users
- Single server setup
- Database selection (SQL vs NoSQL)
- Vertical vs horizontal scaling
- Load balancer introduction
- Database replication
- Cache tier and CDN
- Stateless web tier
- Data center architecture
- Message queues
- Logging, metrics, automation

##### Chapter 2: Back-of-the-Envelope Estimation
- Power of two table
- Latency numbers every programmer should know
- Availability and SLA calculations
- Estimating QPS, storage, bandwidth

##### Chapter 3: A Framework For System Design Interviews
- Step 1 — Understand the problem and establish design scope
- Step 2 — Propose high-level design and get buy-in
- Step 3 — Design deep dive
- Step 4 — Wrap up (bottlenecks, error handling, operational concerns)

##### Chapter 4: Design A Rate Limiter
- Token bucket, leaking bucket, fixed window counter, sliding window log, sliding window counter algorithms
- High-level architecture with rate limiter middleware
- Distributed rate limiter considerations

##### Chapter 5: Design Consistent Hashing
- The rehashing problem
- Consistent hashing ring
- Virtual nodes
- Real-world use cases (Amazon DynamoDB, Apache Cassandra)

##### Chapter 6: Design A Key-Value Store
- Single server vs distributed key-value store
- Data partitioning, replication, consistency
- Inconsistency resolution with versioning and vector clocks
- Failure detection (gossip protocol) and handling

##### Chapter 7: Design A Unique ID Generator In Distributed Systems
- Multi-master replication, UUID, ticket server, Twitter Snowflake approaches

##### Chapter 8: Design A URL Shortener
- API design, URL redirecting (301 vs 302)
- Hash function selection, hash collision resolution
- Database schema and deep dive

##### Chapter 9: Design A Web Crawler
- Seed URLs, URL frontier, HTML downloader, DNS resolver
- Content seen detection, URL extraction, URL deduplication
- BFS traversal, politeness, priority, freshness

##### Chapter 10: Design A Notification System
- Push notification, SMS, email
- Contact info gathering, notification sending/receiving flow
- Reliability, rate limiting, retry mechanism

##### Chapter 11: Design A News Feed System
- Feed publishing and newsfeed building
- Fanout on write vs fanout on read
- Cache architecture and notification

##### Chapter 12: Design A Chat System
- WebSocket communication
- 1-on-1 chat and group chat flows
- Online presence indicator
- Message synchronization and storage

##### Chapter 13: Design A Search Autocomplete System
- Trie data structure and optimizations
- Data gathering service and query service
- Trie operations: create, update, delete
- Storage and scaling

##### Chapter 14: Design YouTube
- Video uploading and streaming flows
- Directed Acyclic Graph (DAG) model for video processing
- Video transcoding architecture
- CDN and cost optimization

##### Chapter 15: Design Google Drive
- File upload (resumable upload), download, sync
- Block-level storage, metadata database
- Notification service and sync conflict resolution

##### Chapter 16: The Learning Continues
- Real-world systems as study material
- Distributed systems papers and engineering blogs

#### Volume 2 — Advanced and Specialized Problems

##### Chapter 1: Proximity Service
- Geospatial indexing (geohash, quadtree, Google S2)
- Location-based service architecture

##### Chapter 2: Nearby Friends
- Real-time location sharing
- WebSocket fan-out vs pub/sub
- Redis pub/sub for location updates

##### Chapter 3: Google Maps
- Map tile serving and rendering
- Routing algorithms (Dijkstra, A*)
- ETA estimation and navigation

##### Chapter 4: Distributed Message Queue
- Message models (point-to-point, pub/sub)
- Broker, partition, consumer group design
- Message delivery guarantees (at-least-once, exactly-once)

##### Chapter 5: Metrics Monitoring
- Push vs pull data collection models
- Time-series database design
- Alerting system architecture

##### Chapter 6: Ad Click Event Aggregation
- Real-time event aggregation pipeline
- MapReduce-style processing
- Data reconciliation and exactly-once processing

##### Chapter 7: Hotel Reservation
- Concurrency and race conditions
- Optimistic vs pessimistic locking
- Overbooking and inventory management

##### Chapter 8: Distributed Email Service
- Email sending/receiving protocols (SMTP, IMAP, POP)
- Email deliverability and spam handling
- Search and storage at scale

##### Chapter 9: S3-like Object Storage
- Object storage vs block storage vs file storage
- Data durability and erasure coding
- Metadata and bucket management

##### Chapter 10: Real-time Gaming Leaderboard
- Sorted sets (Redis ZSET)
- Write-heavy vs read-heavy leaderboard patterns
- Sharding for scale

##### Chapter 11: Payment System
- Pay-in and pay-out flows
- Payment Service Provider (PSP) integration
- Idempotency and reconciliation

##### Chapter 12: Digital Wallet
- In-memory transaction processing
- Event sourcing and CQRS
- Audit and correctness guarantees

##### Chapter 13: Stock Exchange
- Matching engine architecture
- Order book data structures
- Sequencer and market data publisher
- Low-latency design considerations

---

## 3. Mastering the System Design Interview

**Platform:** Udemy
**Instructor(s):** Frank Kane (ex-Amazon hiring manager / "bar raiser")
**Rating:** Udemy bestseller; instructor interviewed 1,000+ candidates at Amazon
**Duration:** ~5 hours on-demand video, 9 sections
**URL:** https://www.udemy.com/course/system-design-interview-prep/

### Curriculum

#### Section 1: Introduction
- Course Intro
- Get your Copy of the Slides

#### Section 2: Designing Systems that Scale (15 lectures)
- Scalability: Introduction
- Horizontal vs. Vertical Scaling
- Failover Strategies
- Sharding Databases / NoSQL
- Data Lakes
- ACID compliance and the CAP theorem
- Using CAP to Choose a Database
- Caching: Introduction
- Caching Technologies
- Eviction Strategies for Caching
- Content Distribution Networks (CDNs)
- Resiliency: Introduction
- Designing for Resiliency
- Scaling your Data: Introduction
- Distributed Storage Solutions
- HDFS Architecture
- Quiz: System Design

#### Section 3: Algorithms and Data Structures (6 lectures)
- Algorithms Introduction
- Linked Lists
- Binary Trees and Hashes
- Graphs and Graph Traversal
- Search Algorithms
- Sort Algorithms
- Information Retrieval
- Quiz: Algorithms and Data Structures

#### Section 4: Working with Big Data (4 lectures)
- Message Queues
- Data Analytics Intro
- Apache Spark
- Cloud Computing Intro
- Cloud Computing: A Brief Overview
- Quiz: Big Data

#### Section 5: Designing Generative AI Systems (4 lectures)
- Introduction: Generative AI Design
- Intro to Large Language Model APIs and Context
- Retrieval-Augmented Generation (RAG)
- Agentic AI, and Integrating AI Into Larger Systems

#### Section 6: Design Interview Strategies (3 lectures)
- Interview Strategy Intro
- Working Backwards
- Defining Requirements
- Design Strategies

#### Section 7: Mock Design Interviews (6 mock interviews, 4 lessons each)
- URL Shortening Service (Q&A → Try It Yourself → System Design → Debrief)
- Restaurant Reservation System (Q&A → Try It Yourself → System Design → Debrief)
- Web Crawler (Q&A → Try It Yourself → System Design → Debrief)
- Top-Sellers (Q&A → Try It Yourself → System Design → Debrief)
- Video Sharing Service (Q&A → Try It Yourself → System Design → Debrief)
- Search Engine (Q&A → Try It Yourself → System Design → Debrief)

#### Section 8: General Tech Interview Tips (8 lectures)
- Tech Interview Intro
- Demonstrating Perseverance
- What your Interviewer is Looking For
- Demonstrating Independence
- Coding at the Whiteboard
- Keeping Up your Stamina; Asking Questions
- Think Big and Be Nice
- Do Your Research

#### Section 9: Good Luck on Your Interview!
- Wrapping Up
- Learning More

---

## 4. Software Architecture & Design of Modern Large Scale Systems

**Platform:** Udemy
**Instructor(s):** Michael Pogrebinsky (ex-Google, iSAQB-certified architect)
**Rating:** 4.7/5 (14,189 ratings)
**Duration:** ~7 hours on-demand video, 31 sections
**URL:** https://www.udemy.com/course/software-architecture-design-of-modern-large-scale-systems/

### Curriculum

#### Section 1: Introduction
- Software architecture definitions and role of the architect

#### Section 2: Requirements Gathering & Analysis
- Classifying requirements: features, quality attributes, system constraints

#### Section 3: Functional Requirements — Use Cases & User Flows
- Capturing functional requirements through use cases and sequence diagrams

#### Section 4: Quality Attributes (Non-Functional Requirements)
- Performance, scalability, reliability as measurable characteristics

#### Section 5: System Constraints
- Technical, business, and legal constraints

#### Section 6: Performance Metrics
- Response time (processing + waiting time), throughput

#### Section 7: Scalability
- Vertical, horizontal, and organizational scaling

#### Section 8: High Availability
- MTBF, MTTR, availability percentages (nines)

#### Section 9: Fault Tolerance
- Failure prevention, detection, and recovery
- Active-active vs active-passive replication

#### Section 10: SLA, SLO, and SLI
- Service Level Agreements, Objectives, and Indicators

#### Section 11: API Design
- Public, private, and partner APIs; usability and idempotency

#### Section 12: Remote Procedure Calls (RPC)
- RPC architecture, gRPC, stub generation

#### Section 13: RESTful APIs
- Resource-oriented design, statelessness, cacheability

#### Section 14: Load Balancers
- DNS, network (L4), application (L7), hardware load balancers
- Load balancing strategies and health checks

#### Section 15: Message Brokers
- Asynchronous architectures, producers, consumers, topics, queues

#### Section 16: API Gateway
- Abstracting backend services, rate limiting, authentication, routing

#### Section 17: Content Delivery Networks (CDNs)
- Globally distributed caching, edge servers, cache invalidation

#### Section 18: Relational Databases
- Table-based storage, normalization, ACID transactions

#### Section 19: Non-Relational (NoSQL) Databases
- Key/value stores, document stores, graph databases, column-family stores

#### Section 20: Database Performance Optimization
- Indexing, replication, sharding techniques

#### Section 21: CAP Theorem
- Consistency, Availability, Partition Tolerance trade-offs

#### Section 22: Unstructured Data Storage
- Distributed file systems, object stores (S3-style)

#### Section 23: Multi-Tier Architecture
- Three-Tier Architecture (Presentation, Application, Data)

#### Section 24: Microservices Architecture
- Monolith vs microservices, independent deployment, service boundaries

#### Section 25: Event-Driven Architecture
- Event-based asynchronous communication, event sourcing

#### Section 26: Big Data Processing Introduction
- Volume, variety, velocity characteristics

#### Section 27: Batch vs. Stream Processing
- Scheduled batch jobs vs real-time stream processing

#### Section 28: Lambda Architecture
- Batch layer, speed layer, serving layer

#### Section 29: Real-World System Design — Discussion Forum
- Requirements capture, service decomposition, database schema

#### Section 30: Forum Architecture Implementation
- API design, database structures for posts, comments, votes

#### Section 31: E-Commerce Marketplace Design
- Sequence diagrams, service architecture, scalability patterns

---

## 5. Designing Data-Intensive Applications

**Platform:** O'Reilly (book)
**Author:** Martin Kleppmann
**Rating:** Widely regarded as the definitive distributed systems reference for practitioners
**Duration:** 616 pages / ~20 hours (audiobook); 12 chapters across 3 parts
**URL:** https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/

### Curriculum

#### Part I: Foundations of Data Systems

##### Chapter 1: Reliable, Scalable, and Maintainable Applications
- Thinking About Data Systems
- Reliability (Hardware Faults, Software Errors, Human Errors)
- Scalability (Describing Load, Describing Performance, Coping Approaches)
- Maintainability (Operability, Simplicity, Evolvability)

##### Chapter 2: Data Models and Query Languages
- Relational Model vs. Document Model
- NoSQL emergence and the object-relational mismatch
- Many-to-One and Many-to-Many Relationships
- Query Languages for Data (SQL, MapReduce)
- Graph-Like Data Models (Cypher, SPARQL, Datalog)

##### Chapter 3: Storage and Retrieval
- Hash Indexes, SSTables, LSM-Trees
- B-Trees and comparison with LSM-Trees
- Transaction Processing vs. Analytics
- Data Warehousing (star schema, column-oriented storage, compression)

##### Chapter 4: Encoding and Evolution
- Formats: JSON, XML, Thrift, Protocol Buffers, Avro
- Schema evolution and compatibility
- Dataflow: REST, RPC, message-passing architectures

#### Part II: Distributed Data

##### Chapter 5: Replication
- Leaders and Followers
- Synchronous vs. Asynchronous Replication
- Handling Node Outages and Replication Lag
- Multi-Leader and Leaderless Replication
- Quorums and concurrent write detection

##### Chapter 6: Partitioning
- Key-range vs. hash partitioning
- Secondary index partitioning (local vs. global)
- Rebalancing strategies and request routing

##### Chapter 7: Transactions
- ACID meaning and isolation levels
- Read committed, snapshot isolation, serializable isolation
- Write skew, phantoms
- Serial execution, two-phase locking, serializable snapshot isolation

##### Chapter 8: The Trouble with Distributed Systems
- Unreliable networks (timeouts, congestion)
- Unreliable clocks (time-of-day vs. monotonic, clock synchronization)
- Process pauses, Byzantine faults
- System models and correctness guarantees

##### Chapter 9: Consistency and Consensus
- Linearizability and ordering guarantees
- Sequence number ordering and total order broadcast
- Two-phase commit and distributed transactions
- Consensus algorithms (Raft, Paxos, Zab)
- Membership and coordination services (ZooKeeper)

#### Part III: Derived Data

##### Chapter 10: Batch Processing
- Unix philosophy and MapReduce
- Distributed filesystems (HDFS)
- Join strategies (sort-merge, broadcast, partitioned hash)
- Beyond MapReduce (Spark, Flink, materialization)

##### Chapter 11: Stream Processing
- Messaging systems (direct, broker-based)
- Change data capture and event sourcing
- Stream joins (stream-stream, stream-table, table-table)
- Fault tolerance in stream processing

##### Chapter 12: The Future of Data Systems
- Data integration and unbundling databases
- Batch and stream processing unification
- Correctness and end-to-end guarantees
- Ethical considerations of data systems

---

## Summary Comparison

| Course | Platform | Duration | Level | Price Model | Focus |
|--------|----------|----------|-------|-------------|-------|
| Grokking the System Design Interview | DesignGurus.io | ~20 hrs, 83 lessons | Beginner–Intermediate | Subscription | Interview framework + 15 classic design problems with quizzes; strong trade-off coverage |
| System Design Interview (Vol 1 & 2) | ByteByteGo (book + online) | ~670 pages across 2 volumes | Beginner–Advanced | One-time purchase / subscription | 28 end-to-end system designs with 4-step framework; visual, illustration-heavy |
| Mastering the System Design Interview | Udemy | ~5 hrs video | Beginner–Intermediate | One-time purchase | 6 mock interviews with debrief; Gen AI systems section; interview strategy coaching |
| Software Architecture & Design of Modern Large Scale Systems | Udemy | ~7 hrs video | Intermediate | One-time purchase | Production architecture fundamentals (31 sections); SLA/SLO/SLI; real-world case studies |
| Designing Data-Intensive Applications | O'Reilly (book) | 616 pages / ~20 hrs | Intermediate–Advanced | One-time purchase / O'Reilly subscription | Deep distributed systems theory: replication, partitioning, transactions, consensus; the "why" behind every building block |
