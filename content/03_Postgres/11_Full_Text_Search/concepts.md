## `tsvector`

A sorted list of lexemes (normalized words) with positional information. This is the indexed representation of a document that Postgres searches against.

```sql
SELECT to_tsvector('english', 'The quick brown foxes jumped over the lazy dogs');
-- 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2
```

Notice: stop words ("the", "over") are removed, words are stemmed ("foxes" → "fox", "jumped" → "jump"), and positions are recorded. The `english` configuration controls these rules. Store a tsvector column (or generated column) on your table and index it for fast search.

## `tsquery`

A search query composed of lexemes combined with boolean operators: `&` (AND), `|` (OR), `!` (NOT), `<->` (followed by). Matched against tsvector using the `@@` operator.

```sql
-- AND: both terms must appear
SELECT * FROM articles WHERE search_vector @@ to_tsquery('english', 'postgres & replication');

-- OR: either term
SELECT * FROM articles WHERE search_vector @@ to_tsquery('english', 'postgres | mysql');

-- Phrase: terms in sequence
SELECT * FROM articles WHERE search_vector @@ to_tsquery('english', 'connection <-> pool');

-- NOT: exclude term
SELECT * FROM articles WHERE search_vector @@ to_tsquery('english', 'postgres & !mysql');
```

`to_tsquery` requires explicit operators between terms. For user-facing input where you don't want to force users to type `&`, use `plainto_tsquery` or `websearch_to_tsquery`.

## `websearch_to_tsquery()`

Parses Google-like search syntax into a tsquery. The most user-friendly input parser for search boxes.

```sql
-- Simple terms (implicitly AND'd)
SELECT websearch_to_tsquery('english', 'postgres replication');
-- 'postgr' & 'replic'

-- Quoted phrase
SELECT websearch_to_tsquery('english', '"connection pool"');
-- 'connect' <-> 'pool'

-- Exclusion with minus
SELECT websearch_to_tsquery('english', 'database -mysql');
-- 'databas' & !'mysql'

-- Use in a query
SELECT title FROM articles
WHERE search_vector @@ websearch_to_tsquery('english', 'full text search -elasticsearch');
```

This is typically what you want for a search input field. Users don't need to know tsquery syntax.

## Text search configuration and dictionaries

Configurations control stemming, stop words, and language-specific processing. The default `english` configuration handles most English text.

```sql
-- See available configurations
SELECT cfgname FROM pg_ts_config;

-- Compare configurations
SELECT to_tsvector('english', 'running runners run');  -- 'run':1,2,3
SELECT to_tsvector('simple', 'running runners run');   -- 'run':3 'runners':2 'running':1

-- Use 'simple' for identifiers, codes, or exact matching (no stemming)
CREATE INDEX idx_products_name ON products
    USING GIN (to_tsvector('simple', name));
```

Use `english` (or the appropriate language) for prose search. Use `simple` when you want exact token matching without stemming — product SKUs, usernames, code identifiers.

## `ts_rank` and `ts_headline`

`ts_rank` scores how well a document matches a query. `ts_headline` generates a text snippet with matching terms highlighted. Together they power ranked search results with context previews.

```sql
SELECT
    title,
    ts_rank(search_vector, query) AS rank,
    ts_headline('english', body, query,
        'StartSel=<b>, StopSel=</b>, MaxWords=35, MinWords=15'
    ) AS snippet
FROM articles, websearch_to_tsquery('english', 'postgres indexing') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 10;
```

`ts_rank_cd` (cover density) is an alternative that favors documents where matching terms are close together. Both ranking functions return a float; the absolute value is less meaningful than the relative ordering.

## GIN index on tsvector

Makes full-text search fast by indexing every lexeme and mapping it to the rows that contain it. Without a GIN index, `@@` requires a sequential scan.

```sql
-- Option 1: index a stored generated column
ALTER TABLE articles ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (to_tsvector('english', title || ' ' || body)) STORED;
CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);

-- Option 2: expression index (no extra column)
CREATE INDEX idx_articles_search ON articles
    USING GIN (to_tsvector('english', title || ' ' || body));
```

The stored-column approach is preferred because it makes the tsvector available in SELECT and for `ts_rank` without recomputing it. The expression index saves storage but requires the query to match the expression exactly.

## LIKE/ILIKE vs full-text search

LIKE does substring pattern matching — no stemming, no word boundaries, no ranking. Full-text search understands language and ranks results by relevance.

| Feature | LIKE / ILIKE | Full-text search |
|---------|-------------|------------------|
| Stemming | No ("run" won't match "running") | Yes |
| Ranking | No | Yes (ts_rank) |
| Stop words | No (matches "the", "and") | Filtered out |
| Index support | pg_trgm GIN/GiST for `%pattern%` | GIN on tsvector |
| Use case | Simple substring/prefix matching | Search over prose |

```sql
-- LIKE: exact substring (no index without pg_trgm)
SELECT * FROM products WHERE name ILIKE '%widget%';

-- Full-text search: linguistic match with ranking
SELECT * FROM products
WHERE to_tsvector('english', name || ' ' || description)
    @@ websearch_to_tsquery('english', 'widget');
```

Use LIKE/ILIKE for simple prefix matches or when the data isn't prose (codes, identifiers). Use full-text search for anything where users expect Google-like search behavior.
