# Extensions and the Ecosystem

Postgres's extension system is what makes it more than a relational database. Extensions add vector search, geospatial queries, query analytics, fuzzy text matching, and federated queries — all inside the database, with full SQL integration and index support.

## Key Points

- **Extensions system** — `CREATE EXTENSION` installs packaged types, operators, and functions. First-class, versioned, per-database.
- **pg_stat_statements** — query performance analytics. Shows call count, total/mean time, rows. First tool for slow query diagnosis.
- **pgvector** — vector similarity search (cosine, L2, inner product). Powers semantic search and RAG inside Postgres.
- **PostGIS** — geospatial types and indexes. Industry standard for "find near X" and spatial analysis.
- **pg_trgm** — trigram indexing for `LIKE '%x%'`, ILIKE, and fuzzy string matching. Great for autocomplete and typo-tolerant search.
- **Foreign Data Wrappers** — query remote databases and files as local tables. Pushes predicates to remote when possible.

## Example

```sql
-- Combine extensions for a "find similar products near me" query

CREATE EXTENSION postgis;
CREATE EXTENSION pg_trgm;
CREATE EXTENSION vector;

CREATE TABLE products (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        text NOT NULL,
    description text NOT NULL,
    price       numeric(10, 2) NOT NULL,
    location    geography(Point, 4326),
    embedding   vector(384)  -- sentence-transformer embedding
);

-- Indexes for each search dimension
CREATE INDEX idx_products_name ON products USING GIN (name gin_trgm_ops);
CREATE INDEX idx_products_location ON products USING GIST (location);
CREATE INDEX idx_products_embedding ON products USING hnsw (embedding vector_cosine_ops);

-- Fuzzy name search
SELECT name, similarity(name, 'widgit') AS sim
FROM products WHERE name % 'widgit' ORDER BY sim DESC LIMIT 5;

-- Nearby products
SELECT name, ST_Distance(location, ST_MakePoint(-73.98, 40.75)::geography) AS meters
FROM products
WHERE ST_DWithin(location, ST_MakePoint(-73.98, 40.75)::geography, 5000)
ORDER BY meters LIMIT 10;

-- Semantic similarity (vector search)
SELECT name, embedding <=> '[0.1, 0.2, ...]'::vector AS distance
FROM products ORDER BY distance LIMIT 5;
```

Three different search paradigms (fuzzy text, spatial, and semantic) running on the same table in the same database, each with its own specialized index. No external services required.
