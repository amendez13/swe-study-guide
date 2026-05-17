## Extensions system

`CREATE EXTENSION` installs packaged functionality — types, operators, functions, indexes — as first-class database objects. Extensions are the standard way to add capabilities beyond core Postgres.

```sql
-- Install an extension (must be available on the server)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- List installed extensions
SELECT extname, extversion FROM pg_extension;

-- Update to latest version
ALTER EXTENSION pgcrypto UPDATE;

-- See what an extension provides
SELECT * FROM pg_extension_objects WHERE extname = 'pgcrypto';
```

Extensions are installed per-database. The underlying shared library must be present on the server filesystem (installed via OS package manager or compiled). Cloud-managed Postgres instances have a curated list of supported extensions.

## `pg_stat_statements`

Tracks execution statistics for every distinct query: call count, total time, rows returned, and buffer usage. The first tool to reach for when diagnosing slow queries.

```sql
CREATE EXTENSION pg_stat_statements;

-- Top 10 queries by total time
SELECT
    calls,
    ROUND(total_exec_time::numeric, 1) AS total_ms,
    ROUND(mean_exec_time::numeric, 1) AS mean_ms,
    rows,
    LEFT(query, 80) AS query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Queries with the worst mean time
SELECT calls, ROUND(mean_exec_time::numeric, 1) AS mean_ms, query
FROM pg_stat_statements
WHERE calls > 100
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Reset stats (do this periodically to see recent trends)
SELECT pg_stat_statements_reset();
```

Configure in `postgresql.conf`: `shared_preload_libraries = 'pg_stat_statements'`. The extension normalizes queries (replacing constants with `$1`, `$2`) so the same query with different parameters counts as one entry.

## pgvector

Adds vector similarity search — L2 distance, inner product, and cosine distance. Enables semantic search, recommendations, and RAG (retrieval-augmented generation) inside Postgres.

```sql
CREATE EXTENSION vector;

CREATE TABLE documents (
    id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    content   text NOT NULL,
    embedding vector(1536)  -- OpenAI embedding dimension
);

-- Create an index for approximate nearest neighbor (ANN) search
CREATE INDEX idx_docs_embedding ON documents
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Find 5 most similar documents to a query vector
SELECT id, content, embedding <=> '[0.1, 0.2, ...]'::vector AS distance
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

Index types: `ivfflat` (faster builds, good recall) and `hnsw` (better recall, slower builds, more memory). For small tables (<10k rows), exact search without an index is fast enough.

## PostGIS

Spatial data types and indexes for geospatial workloads. Stores geometry (flat coordinates) and geography (earth-surface coordinates) with operators for distance, containment, intersection, and buffering.

```sql
CREATE EXTENSION postgis;

CREATE TABLE places (
    id       integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name     text NOT NULL,
    location geography(Point, 4326) NOT NULL  -- WGS84 lat/lon
);

CREATE INDEX idx_places_location ON places USING GIST (location);

-- Find places within 1km of a point
SELECT name, ST_Distance(location, ST_MakePoint(-73.985, 40.748)::geography) AS meters
FROM places
WHERE ST_DWithin(location, ST_MakePoint(-73.985, 40.748)::geography, 1000)
ORDER BY meters;
```

PostGIS is the industry standard for spatial databases. It powers ride-sharing geofencing, delivery routing, real-estate search, and any application that needs "find things near X" or "is point inside polygon."

## pg_trgm

Trigram-based similarity matching and indexing. Powers fast `LIKE '%pattern%'`, `ILIKE`, and fuzzy string search without full-text search overhead.

```sql
CREATE EXTENSION pg_trgm;

-- GIN index for LIKE/ILIKE acceleration
CREATE INDEX idx_products_name_trgm ON products USING GIN (name gin_trgm_ops);

-- Now this uses the index (without pg_trgm, %pattern% requires a seq scan)
SELECT * FROM products WHERE name ILIKE '%widget%';

-- Similarity search (fuzzy matching)
SELECT name, similarity(name, 'postgre') AS sim
FROM products
WHERE name % 'postgre'  -- % operator: similarity > pg_trgm.similarity_threshold
ORDER BY sim DESC;
```

pg_trgm splits strings into three-character sequences and compares overlap. It's ideal for autocomplete, "did you mean" suggestions, and searching against misspellings — cases where full-text search is overkill or doesn't work (FTS requires whole words).

## Foreign Data Wrappers (FDW)

Query external data sources as if they were local tables. Built into core Postgres; extensions provide wrappers for different sources.

```sql
CREATE EXTENSION postgres_fdw;

-- Connect to a remote Postgres instance
CREATE SERVER analytics_db FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'analytics.internal', dbname 'warehouse');

CREATE USER MAPPING FOR app_user SERVER analytics_db
    OPTIONS (user 'reader', password 'secret');

-- Import remote tables
IMPORT FOREIGN SCHEMA public FROM SERVER analytics_db INTO foreign_analytics;

-- Query remote tables like local ones
SELECT customer_id, sum(revenue) FROM foreign_analytics.daily_revenue
WHERE date > '2024-01-01' GROUP BY customer_id;
```

Available FDW implementations: `postgres_fdw` (other PG instances), `mysql_fdw`, `redis_fdw`, `file_fdw` (CSV/text files), `multicorn` (any Python data source). Queries are pushed down to the remote server when possible, reducing data transfer.
