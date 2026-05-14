# Geospatial and Location-Based Services

How to index and query spatial data — the building block for "what's near me?" features. This topic appears in interview problems like Yelp, Uber, and Google Maps, and as a component in any system that needs proximity search.

## Key Points

- **Geohash** — encodes lat/lon into a string where shared prefixes mean proximity. Works with standard B-tree indexes. Query the target cell plus 8 neighbors.
- **Quadtree** — recursive 2D subdivision. Adapts resolution to data density. In-memory, O(log N) lookup. Good for non-uniform distributions.
- **Google S2** — sphere-to-Hilbert-curve mapping with 64-bit cell IDs. Uniform area cells, used by Google Maps and Uber. More precise than geohash for global services.
- **Proximity service** — read-heavy, static data. Geohash + database query for nearby results. Cache aggressively. For dynamic data (driver locations), use Redis GEOADD with real-time updates.
- **Geofencing** — detect entry/exit from predefined zones. Point-in-polygon test, optimized with spatial indexes for large zone counts.

## Example

Designing a "nearby restaurants" feature:

```text
Requirements:
  10M restaurants globally. Users search within 1–25 km radius.
  Read-heavy: 100K searches/sec, 100 restaurant updates/sec.
  Latency: < 100ms for search results.

Storage:
  PostgreSQL with PostGIS extension for geospatial queries.
  Each restaurant: id, name, lat, lon, geohash_6, category, rating.
  Index: B-tree on geohash_6 (6-character geohash ≈ 1.2 km precision).

Search flow:
  1. Client sends (lat=37.77, lon=-122.42, radius=5km, category=sushi).
  2. Compute geohash: "9q8yyk" → prefix "9q8yy" (5 chars ≈ 5 km).
  3. Query: WHERE geohash_6 LIKE '9q8yy%' AND category = 'sushi'
     Also query the 8 neighboring prefixes for edge coverage.
  4. Post-filter: compute exact distance, discard results > 5 km.
  5. Sort by distance and rating. Return top 20.

Caching:
  Cache results by (geohash_prefix, category, sort_order) in Redis.
  TTL 5 minutes — restaurant data changes rarely.
  Cache hit rate > 90% for popular areas.

  100K QPS × 10% miss rate = 10K QPS to database. Manageable.
```
