# PostgreSQL Concepts

A distilled concept reference for a student of PostgreSQL, synthesized from the five course outlines in [course_outlines.md](course_outlines.md). Each item names a concept worth being able to explain, recognize in code, and apply in practice. Setup logistics (installing Postgres, choosing a GUI client, generic Git usage) are excluded — the focus is on durable PostgreSQL, SQL, and database engineering knowledge.

---

## 1. Relational Model Foundations

- **Tables, rows, and columns** — the basic storage abstraction: a table is a named collection of rows that share a column schema. Postgres enforces types per column.
- **Primary keys** — a column or set of columns that uniquely identifies every row. Postgres enforces uniqueness and creates a B-tree index automatically.
- **Foreign keys** — a constraint that references a primary key in another table, enforcing referential integrity. Understand ON DELETE CASCADE, SET NULL, and RESTRICT.
- **Normalization** — the process of structuring tables to eliminate redundancy (1NF through 3NF). Reduces update anomalies at the cost of more joins.
- **One-to-many, many-to-many, one-to-one** — the three fundamental relationship types. Many-to-many requires a junction (join) table with two foreign keys.
- **Schema** — a namespace inside a database that groups tables, views, and functions. The default is `public`; use schemas to isolate tenants, modules, or test environments.

## 2. SQL Fundamentals

- **SELECT, INSERT, UPDATE, DELETE** — the four CRUD operations. Every SQL interaction is one of these (or DDL/DCL).
- **WHERE clause** — filters rows before they reach the result set. Supports comparison operators, BETWEEN, IN, LIKE, IS NULL, and boolean combinators (AND, OR, NOT).
- **ORDER BY, LIMIT, OFFSET** — control result ordering and pagination. OFFSET-based pagination degrades on large tables; prefer keyset (cursor-based) pagination.
- **JOINs (INNER, LEFT, RIGHT, FULL, CROSS)** — combine rows from multiple tables. INNER returns only matches; LEFT keeps all rows from the left table; CROSS produces the Cartesian product.
- **GROUP BY and aggregate functions** — collapse rows into groups. Aggregates (COUNT, SUM, AVG, MIN, MAX) compute summary values per group.
- **HAVING** — filters groups after aggregation, analogous to WHERE for individual rows.
- **DISTINCT** — eliminates duplicate rows from a result set.
- **Set operations (UNION, INTERSECT, EXCEPT)** — combine result sets of two queries. UNION ALL preserves duplicates; UNION deduplicates.

## 3. Data Types

- **Integers (smallint, integer, bigint)** — fixed-size numeric types. Choose the smallest type that fits the domain to reduce storage and improve cache efficiency.
- **Numeric and decimal** — arbitrary-precision exact types for financial data where floating-point rounding is unacceptable.
- **Floating point (real, double precision)** — IEEE 754 approximate types. Faster than numeric but subject to rounding; avoid for money.
- **Character types (text, varchar, char)** — `text` is the preferred general-purpose string type in Postgres; `varchar(n)` adds a length check; `char(n)` pads with spaces.
- **Boolean** — true/false/null. Postgres accepts multiple literal forms (TRUE, 't', 'yes', '1') on input.
- **Timestamps and time zones** — `timestamptz` stores UTC internally and converts on display using the session's time zone. Always prefer `timestamptz` over `timestamp`.
- **Dates, times, and intervals** — `date` stores calendar dates; `time` stores time of day; `interval` stores durations and supports arithmetic with timestamps.
- **UUID** — 128-bit universally unique identifier. Good for distributed ID generation; use `gen_random_uuid()` (built-in since PG 13).
- **Enum** — user-defined type with a fixed set of labels. Useful for low-cardinality categorical columns; harder to modify than a lookup table.
- **Serial, identity, and sequences** — auto-incrementing integer generation. `GENERATED ALWAYS AS IDENTITY` (SQL standard) is preferred over the legacy `serial` pseudo-type.
- **JSON and JSONB** — `jsonb` is the binary, indexable form; `json` preserves formatting but is slower to query. Use `jsonb` unless you need exact text preservation.
- **Arrays** — Postgres columns can hold arrays of any type. Useful for tags or small lists but breaks first normal form.
- **Ranges** — represent intervals of values (int4range, tsrange, daterange). Support containment, overlap, and adjacency operators; pair with exclusion constraints.
- **Network types (inet, cidr, macaddr)** — specialized types for IP addresses and MAC addresses with built-in validation and operators.
- **Composite types** — user-defined row types. Created implicitly for every table; can be used as column types or function return types.
- **Bit strings** — fixed or variable-length sequences of 0s and 1s. Niche; useful for bitmask columns.

## 4. Constraints and Data Integrity

- **NOT NULL** — prevents a column from accepting null values. Apply to any column where null is meaningless.
- **UNIQUE** — enforces that all values (or value combinations) in a column set are distinct. Automatically creates an index.
- **CHECK** — a boolean expression evaluated on insert/update. Use for domain rules like `price > 0` or `status IN ('active', 'inactive')`.
- **DEFAULT** — assigns a value when none is provided on insert. Can reference functions like `now()` or `gen_random_uuid()`.
- **Exclusion constraints** — generalized uniqueness: no two rows may have overlapping ranges, conflicting schedules, etc. Backed by a GiST index.
- **Domain types** — named data types built from a base type plus constraints. Reuse a CHECK constraint across multiple columns without repeating it.

## 5. Indexes

- **B-tree index** — the default and most common index type. Supports equality and range queries on ordered data.
- **Heap, blocks, and tuples** — Postgres stores table data in a heap (unordered pages). Each row is a tuple; each page is an 8 kB block. Understanding this explains why indexes matter.
- **CTIDs** — the physical address of a tuple (block number, offset). The index stores CTIDs to locate heap rows.
- **Primary key index vs secondary index** — the primary key index is created automatically and enforces uniqueness; secondary indexes are added manually for query performance.
- **Composite indexes** — indexes on multiple columns. Column order matters: the index is useful for queries that filter on a leading prefix of the index columns.
- **Covering indexes (INCLUDE)** — add non-key columns to an index so the query can be answered from the index alone (index-only scan) without visiting the heap.
- **Partial indexes** — an index with a WHERE clause that only indexes a subset of rows. Saves space and speeds up queries that always include the same filter.
- **Functional indexes** — index the result of an expression (e.g., `lower(email)`). Required when queries filter on a transformed column.
- **Index selectivity and cardinality** — selectivity is the fraction of rows an index lookup returns. High cardinality (many distinct values) makes B-tree indexes effective; low cardinality does not.
- **Hash indexes** — equality-only lookups, no range support. Rarely better than B-tree in modern Postgres.
- **GIN index (Generalized Inverted Index)** — maps each element (array element, JSON key, lexeme) to the set of rows containing it. Essential for full-text search, JSONB containment, and array operations.
- **GiST index (Generalized Search Tree)** — supports geometric, range, and full-text queries. Backs exclusion constraints and PostGIS spatial lookups.
- **Index ordering and NULL placement** — B-tree indexes can be ASC or DESC with NULLS FIRST or NULLS LAST, which matters for ORDER BY queries that need an index scan.
- **Duplicate and redundant indexes** — having two indexes that serve the same queries wastes write performance and storage. Audit with `pg_stat_user_indexes`.
- **CREATE INDEX CONCURRENTLY** — builds an index without locking the table for writes. Slower to build but essential in production.

## 6. Query Planning and EXPLAIN

- **Query processing pipeline** — parser → rewriter → planner/optimizer → executor. The planner chooses the cheapest execution plan.
- **EXPLAIN** — shows the planned execution strategy without running the query. Displays node types, estimated costs, and row counts.
- **EXPLAIN ANALYZE** — actually runs the query and reports real execution times and row counts alongside estimates. Use for performance diagnosis.
- **Scan nodes** — Sequential Scan (full table), Index Scan (traverse index then fetch heap), Index Only Scan (answer from index alone), Bitmap Index Scan (build a bitmap of matching pages, then fetch).
- **Cost model (startup cost vs total cost)** — startup cost is the work before the first row is returned; total cost is the work for all rows. Costs propagate up through the plan tree.
- **Join strategies** — Nested Loop (good for small outer sets), Hash Join (good for equality joins on larger sets), Merge Join (good for pre-sorted inputs).
- **Row estimates and statistics** — the planner relies on `pg_statistic` (populated by ANALYZE). Bad statistics → bad plans. Run ANALYZE after large data changes.

## 7. Transactions and Concurrency

- **ACID properties** — Atomicity (all or nothing), Consistency (constraints hold), Isolation (concurrent transactions don't interfere), Durability (committed data survives crashes).
- **BEGIN, COMMIT, ROLLBACK** — explicit transaction control. Without BEGIN, each statement runs in its own implicit transaction.
- **Transaction isolation levels** — Read Uncommitted, Read Committed (Postgres default), Repeatable Read, Serializable. Each level trades performance for stricter guarantees.
- **MVCC (Multi-Version Concurrency Control)** — Postgres keeps old row versions so readers never block writers. Each transaction sees a snapshot of the database at its start (or statement start, depending on isolation level).
- **Row-level locking** — SELECT FOR UPDATE locks selected rows to prevent concurrent modification. Use to prevent double-booking and lost updates.
- **Deadlocks** — occur when two transactions each hold a lock the other needs. Postgres detects and aborts one. Minimize by acquiring locks in a consistent order.
- **Optimistic vs pessimistic concurrency control** — pessimistic locks rows up front (SELECT FOR UPDATE); optimistic checks at commit time (version columns, serializable isolation). Choose based on contention frequency.

## 8. Subqueries and Common Table Expressions

- **Scalar subquery** — returns a single value; usable in SELECT, WHERE, or as a column expression.
- **Subquery in FROM** — produces a derived table (inline view). Must be aliased.
- **Correlated subquery** — references columns from the outer query. Re-evaluated per outer row; can be expensive.
- **EXISTS and NOT EXISTS** — tests whether a subquery returns any rows. Often more efficient than IN for large sets.
- **Common Table Expressions (CTEs)** — `WITH ... AS (...)` blocks that name a subquery for readability. In PG 12+, the planner can inline non-recursive CTEs.
- **Recursive CTEs** — `WITH RECURSIVE` for tree/graph traversal: org charts, category hierarchies, shortest paths. Composed of a base case UNION ALL'd with a recursive step.

## 9. Window Functions

- **OVER clause** — defines a window (partition + order) over which a function computes. Does not collapse rows like GROUP BY.
- **PARTITION BY** — divides the result set into partitions; the window function resets for each partition.
- **ROW_NUMBER, RANK, DENSE_RANK** — numbering functions. ROW_NUMBER is unique per partition; RANK leaves gaps on ties; DENSE_RANK does not.
- **LAG, LEAD** — access a row before or after the current row within the window. Useful for computing deltas (today vs yesterday).
- **Frame clauses (ROWS BETWEEN)** — control which rows relative to the current row are included in the window. Default is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW.
- **NTILE, PERCENT_RANK, CUME_DIST** — distribution functions for ranking and bucketing.
- **Aggregate functions as window functions** — SUM, AVG, COUNT, etc. can be used with OVER to compute running totals or moving averages without collapsing rows.

## 10. Views and Materialized Views

- **Views** — named SELECT queries stored as definitions (not data). Simplify complex queries and provide a stable interface over evolving schemas.
- **Updatable views** — simple views (single table, no aggregates, no DISTINCT) are auto-updatable. For complex views, use INSTEAD OF triggers.
- **Materialized views** — store query results as physical data. Fast to read but stale until explicitly refreshed with `REFRESH MATERIALIZED VIEW`.
- **REFRESH MATERIALIZED VIEW CONCURRENTLY** — refreshes without locking out readers, but requires a unique index on the materialized view.
- **When to use each** — views for abstraction with no performance gain; materialized views for expensive queries (dashboards, reports) where slight staleness is acceptable.

## 11. Full-Text Search

- **tsvector** — a sorted list of lexemes (normalized words) with positional information. Created from text with `to_tsvector()`.
- **tsquery** — a search query composed of lexemes combined with boolean operators (&, |, !). Created with `to_tsquery()` or `plainto_tsquery()`.
- **websearch_to_tsquery()** — parses Google-like search syntax (quoted phrases, minus for NOT) into a tsquery.
- **Text search configuration and dictionaries** — control stemming, stop words, and language. The default `english` configuration handles most English text.
- **ts_rank and ts_rank_cd** — score how well a document matches a query. Use for ORDER BY relevance.
- **ts_headline** — generates a text snippet with matching terms highlighted. Useful for search result display.
- **GIN index on tsvector** — makes full-text search fast. Store a tsvector column (possibly as a generated column) and index it.
- **LIKE and ILIKE vs full-text search** — LIKE does substring matching (no stemming, no ranking); full-text search understands language. Use LIKE for simple patterns, FTS for search.

## 12. JSON and JSONB

- **JSON vs JSONB** — `json` stores exact text; `jsonb` stores a decomposed binary form that is faster to query and indexable. Always prefer `jsonb` unless exact formatting matters.
- **JSON operators (->  ->>  #>  #>>)** — `->` returns JSON; `->>` returns text. `#>` and `#>>` navigate nested paths.
- **Containment (@>) and existence (?)** — `@>` checks if a JSONB value contains another; `?` checks if a key exists. Both leverage GIN indexes.
- **jsonb_each, jsonb_array_elements, jsonb_to_recordset** — expand JSON objects and arrays into relational rows for joining and aggregation.
- **Updating JSONB (jsonb_set, || operator)** — modify nested values or merge objects. Note: this replaces the entire JSONB column value (no in-place update).
- **Indexing JSONB** — a default GIN index supports containment and existence. For specific key lookups, a B-tree expression index on `(data->>'key')` is more selective.

## 13. Stored Procedures and PL/pgSQL

- **Functions vs procedures** — functions return a value and can be used in SELECT; procedures (PG 11+) can manage transactions (COMMIT/ROLLBACK inside the body).
- **PL/pgSQL** — Postgres's default procedural language. Supports variables, control flow (IF/THEN, LOOP, FOR, WHILE), exception handling, and dynamic SQL.
- **RETURNS TABLE / RETURNS SETOF** — functions that return multiple rows, usable as a FROM source.
- **RAISE NOTICE / RAISE EXCEPTION** — logging and error signaling inside PL/pgSQL. EXCEPTION aborts the current transaction.
- **Other procedural languages** — PL/Python, PL/Perl, PL/Tcl, PL/v8 (JavaScript). Each has trade-offs in sandboxing, performance, and library access.

## 14. Triggers and Rules

- **Triggers** — functions fired automatically before or after INSERT, UPDATE, DELETE, or TRUNCATE on a table. Use for audit logging, enforcing cross-table constraints, and derived data.
- **Row-level vs statement-level triggers** — row-level fires once per affected row; statement-level fires once per statement regardless of row count.
- **BEFORE vs AFTER triggers** — BEFORE can modify or reject the incoming row; AFTER sees the final row and is used for side effects (audit, notification).
- **INSTEAD OF triggers** — fire on views to make non-updatable views writable.
- **Rules** — an older mechanism that rewrites queries before execution. Largely superseded by triggers; still used for some view rewriting.
- **Triggers vs application logic** — triggers guarantee consistency regardless of client but make debugging harder. Prefer application logic for complex business rules; use triggers for cross-cutting concerns.

## 15. Table Partitioning

- **Declarative partitioning** — split a large table into smaller physical partitions by range, list, or hash. Introduced in PG 10, improved each release.
- **Range partitioning** — partition by a continuous value range (dates, IDs). Most common for time-series data.
- **List partitioning** — partition by a discrete set of values (region, status).
- **Hash partitioning** — distribute rows evenly across N partitions by hashing a column. Useful when no natural range exists.
- **Partition pruning** — the planner skips partitions that cannot contain matching rows. Only works when the partition key appears in the WHERE clause.
- **When to partition** — tables with hundreds of millions of rows where queries naturally filter on the partition key. Premature partitioning adds complexity without benefit.

## 16. Replication and High Availability

- **Streaming replication** — the primary sends WAL (Write-Ahead Log) records to standby servers in near-real-time. Standbys can serve read queries.
- **Synchronous vs asynchronous replication** — synchronous waits for standby confirmation before committing (zero data loss, higher latency); asynchronous commits immediately (small data loss window, lower latency).
- **WAL (Write-Ahead Log)** — every change is written to the WAL before being applied to data files. Provides crash recovery and is the basis for replication.
- **Hot standby** — a replica that accepts read-only queries while replaying WAL. Useful for read scaling and reporting.
- **Logical replication** — publishes changes at the row level (INSERT/UPDATE/DELETE) rather than physical WAL blocks. Enables selective table replication, cross-version replication, and data integration.
- **Failover and promotion** — when the primary fails, a standby is promoted to primary. Tools like Patroni, pg_auto_failover, and cloud-managed services automate this.

## 17. Sharding

- **Horizontal sharding** — distributing rows across multiple independent database instances by a shard key. Each shard holds a subset of the data.
- **Consistent hashing** — a hashing strategy that minimizes data movement when shards are added or removed.
- **When to shard** — only when a single Postgres instance cannot handle the write or storage volume. Sharding adds complexity (cross-shard queries, distributed transactions).
- **Citus and other extensions** — Citus adds transparent sharding to Postgres. Foreign Data Wrappers (FDW) can query remote Postgres instances.

## 18. VACUUM, Autovacuum, and Maintenance

- **Dead tuples and bloat** — MVCC leaves old row versions behind after updates and deletes. These dead tuples waste space and slow scans until vacuumed.
- **VACUUM** — reclaims space from dead tuples and updates the visibility map. Does not return space to the OS (use VACUUM FULL for that, but it locks the table).
- **Autovacuum** — a background process that automatically vacuums tables based on configurable thresholds. Should rarely be disabled; tune its aggressiveness instead.
- **ANALYZE** — updates table statistics in `pg_statistic`. Run after large data changes so the planner makes good decisions.
- **REINDEX** — rebuilds an index from scratch. Useful when index bloat accumulates. Use REINDEX CONCURRENTLY in production.
- **pg_stat_user_tables** — system view showing vacuum and analyze counts, dead tuple counts, and last vacuum/analyze times. Essential for monitoring maintenance health.

## 19. Backup, Recovery, and Migrations

- **pg_dump and pg_restore** — logical backup and restore. `pg_dump` exports a database as SQL or a custom-format archive; `pg_restore` reloads it. Works across minor versions.
- **COPY command** — bulk loads data from files (CSV, binary) into tables or exports table data to files. Much faster than row-by-row INSERT.
- **Base backups and PITR** — `pg_basebackup` takes a physical snapshot; combined with archived WAL, you can restore to any point in time (Point-In-Time Recovery).
- **Schema migrations** — versioned, reversible scripts that evolve the database schema alongside application code. Each migration has an `upgrade()` and `downgrade()` path.
- **Schema vs data migrations** — schema migrations change structure (ADD COLUMN, CREATE TABLE); data migrations transform existing data. Run data migrations carefully, often in batches with transaction boundaries.
- **Migration tools** — Alembic (Python/SQLAlchemy), Flyway (Java), golang-migrate, node-pg-migrate. Choose one that matches your stack.

## 20. Connection Management

- **Connection pooling** — reuses database connections across requests instead of opening a new one per request. Reduces connection overhead and limits total connections.
- **PgBouncer** — a lightweight external connection pooler. Supports session, transaction, and statement pooling modes.
- **Connection pool sizing** — too few connections starve the application; too many overwhelm Postgres (each connection consumes memory). A common heuristic: `connections = (core_count * 2) + effective_spindle_count`.
- **Server-side vs client-side cursors** — server-side cursors keep result sets on the server and stream rows on demand; client-side cursors fetch everything at once. Use server-side for large result sets.

## 21. Database Design Patterns

- **Polymorphic associations** — one table references rows in multiple other tables (e.g., a "like" that can target a post, comment, or photo). Approaches: separate join tables (cleanest), nullable foreign keys, or a type+id pattern.
- **Star schema and denormalization** — analytical workloads may benefit from denormalized fact and dimension tables. Trade write complexity for read speed.
- **Soft deletes** — mark rows as deleted (`deleted_at` timestamp) instead of physically removing them. Preserves history but complicates queries (must filter on `deleted_at IS NULL`).
- **Upsert (INSERT ... ON CONFLICT)** — atomically insert a row or update it if a conflict (unique violation) occurs. Replaces the read-then-decide anti-pattern.
- **RETURNING clause** — returns the affected rows from INSERT, UPDATE, or DELETE. Eliminates the need for a follow-up SELECT.

## 22. Security

- **SQL injection** — constructing queries by string concatenation lets attackers inject arbitrary SQL. Always use parameterized queries / prepared statements.
- **Roles and privileges** — Postgres uses roles (users and groups) with granular GRANT/REVOKE on databases, schemas, tables, columns, and functions.
- **Row-Level Security (RLS)** — policies that filter rows per-user at the database level. Enables multi-tenant isolation without application-side WHERE clauses.
- **Prepared statements** — pre-compiled query templates with parameter placeholders ($1, $2). Prevent injection and can improve performance by reusing plans.
- **SSL/TLS connections** — encrypt client-server traffic. Configure `sslmode=verify-full` in production to prevent man-in-the-middle attacks.

## 23. Extensions and the Ecosystem

- **Extensions system** — `CREATE EXTENSION` installs packaged functionality. Extensions are first-class in Postgres and can add types, operators, indexes, and functions.
- **pgvector** — adds vector similarity search (L2 distance, inner product, cosine distance). Enables semantic search and recommendation systems inside Postgres.
- **PostGIS** — spatial data types and indexes (geometry, geography, raster). The standard for geospatial workloads in Postgres.
- **pg_stat_statements** — tracks execution statistics (calls, time, rows) for every distinct query. The first tool to reach for when diagnosing slow queries.
- **pg_trgm** — trigram-based similarity matching and indexing. Powers fast LIKE/ILIKE and fuzzy search with GIN or GiST indexes.
- **Foreign Data Wrappers (FDW)** — query external data sources (other Postgres instances, MySQL, CSV files, REST APIs) as if they were local tables.

## 24. Accessing PostgreSQL from Applications

- **Client libraries** — `psycopg2`/`psycopg3` (Python), `node-postgres` (`pg`) (Node.js), `JDBC` (Java). Each wraps libpq or the Postgres wire protocol.
- **Connection pool per application** — each application process should use a pool (SQLAlchemy pool, pg Pool, HikariCP). Don't open a connection per request.
- **ORM vs raw SQL** — ORMs (SQLAlchemy, Django ORM, TypeORM) add convenience and portability; raw SQL gives full control and performance. Many teams use both: ORM for CRUD, raw SQL for complex queries.
- **Repository pattern** — encapsulates database access behind a domain-specific interface. Keeps SQL out of route handlers and simplifies testing.
- **Testing with schemas** — create an isolated schema per test worker, run migrations, execute tests, then drop the schema. Enables parallel test execution without database conflicts.

---

## Self-Check

For each concept above, ask yourself:

1. **Can I explain it?** — Could I describe what it is and why it matters to a colleague in two sentences?
2. **Can I recognize it?** — If I saw it in a query plan, a schema definition, or a config file, would I understand what it's doing?
3. **Can I write a small example?** — Could I demonstrate it in a psql session or a short script without looking it up?

If the answer to any of these is no, that concept is a study target.
