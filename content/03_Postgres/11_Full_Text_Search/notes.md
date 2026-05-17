# Full-Text Search

Postgres includes a complete full-text search engine — no external service needed. It supports stemming, stop words, phrase matching, relevance ranking, and highlighted snippets, all backed by GIN indexes for fast lookups.

## Key Points

- **tsvector** — normalized, stemmed, position-aware representation of a document. Store it as a generated column for best performance.
- **tsquery** — boolean search expression with AND (`&`), OR (`|`), NOT (`!`), and phrase (`<->`).
- **websearch_to_tsquery** — parses Google-like syntax. Use for search input fields.
- **Configurations** — control stemming and stop words. Use `english` for prose, `simple` for identifiers.
- **ts_rank / ts_headline** — rank results by relevance, generate highlighted snippets for display.
- **GIN index** — makes `@@` fast. Index a stored tsvector column for best flexibility.
- **LIKE vs FTS** — LIKE is substring matching; FTS understands language. Use LIKE for patterns, FTS for search.

## Example

```sql
CREATE TABLE docs (
    id    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title text NOT NULL,
    body  text NOT NULL,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', title), 'A') ||
        setweight(to_tsvector('english', body), 'B')
    ) STORED
);

CREATE INDEX idx_docs_search ON docs USING GIN (search_vector);

-- Insert a document
INSERT INTO docs (title, body) VALUES (
    'PostgreSQL Full-Text Search',
    'Postgres provides built-in full-text search with stemming, ranking, and GIN indexes.'
);

-- Search with ranking and snippet
SELECT
    title,
    ts_rank(search_vector, query) AS rank,
    ts_headline('english', body, query, 'StartSel=**, StopSel=**') AS snippet
FROM docs, websearch_to_tsquery('english', 'full text search ranking') AS query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

This exercises weighted tsvectors (title weighted higher than body), a GIN index, websearch input parsing, relevance ranking, and highlighted snippets — a complete search feature in pure SQL.
