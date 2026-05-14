# Search, Autocomplete, and Information Retrieval

How to find and rank relevant content at scale. Search appears in system design interviews both as a standalone problem ("Design a search autocomplete system") and as a component in larger designs ("How would users search for products?").

## Key Points

- **Inverted index** — maps terms to documents. The core data structure for full-text search (Elasticsearch, Solr, Lucene).
- **Trie (prefix tree)** — each path represents a prefix. O(prefix length) lookup. Foundation for autocomplete, combined with frequency data for ranking.
- **Autocomplete system** — offline data gathering (query logs → frequency counts → trie) + online query service (prefix lookup → top K cached results, < 50ms latency).
- **Relevance ranking** — TF-IDF / BM25 as baseline text relevance, then layer behavioral signals (CTR, recency, popularity, personalization).
- **Full-text search architecture** — Elasticsearch as a derived store fed by CDC. Sharded index, replicated for read scaling. Scatter-gather query execution.

## Example

Adding search to a product catalog with 50M products:

```text
Requirements:
  Full-text search across product name and description.
  Autocomplete suggestions as the user types.
  Faceted filtering: category, price range, brand, rating.
  Latency: search < 200ms, autocomplete < 50ms.

Architecture:
  Source of truth: PostgreSQL (products table)
  Search index: Elasticsearch (derived via CDC from Postgres)
  Autocomplete: Redis cache of top suggestions per prefix

Write path:
  Product created/updated in Postgres
  → Debezium CDC → Kafka "products" topic
  → Elasticsearch consumer indexes the document
  Lag: ~2 seconds (acceptable for product catalog)

Search query:
  GET /search?q=wireless+headphones&category=electronics&min_price=20
  → Elasticsearch multi-match query on name + description
  → BM25 scoring + boost by rating and sales volume
  → Filter by category and price range (post-filter)
  → Return top 20 results with facet counts

Autocomplete:
  Nightly job: aggregate search query logs → top 10K queries per prefix
  Store in Redis: "auto:wire" → ["wireless headphones", "wireless mouse", ...]
  On keypress: Redis GET "auto:{prefix}" → < 5ms

  Fallback: if prefix not in Redis, query Elasticsearch
  with prefix match on product names.
```
