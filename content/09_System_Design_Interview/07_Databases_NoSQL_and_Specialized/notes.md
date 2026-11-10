# Databases — NoSQL and Specialized

These stores answer access paths a single relational primary serves badly: one opaque key, one nested document, an append-only feed, a hop across relationships, a time range, a keyword query, or a historical scan. The booking write can stay on that primary. Placement of keys, freshness, cache-aside, the copy pipeline, and ranking are the linked topics.

## Key Points

- **Access pattern to store** — name the key, the read, the write rule, and the rate before naming a product.
- **SQL vs NoSQL trade-offs** — multi-row constraints stay on the relational primary. A second store is polyglot persistence: one more access path, and one more pipeline.
- **Key-value store** — get, put, and delete of an opaque value. A durable put returns after the flush you required. A rebuildable copy is a cache.
- **Distributed key-value basics** — partition the keys, then replicate each partition. The ring is partitioning. An older copy is consistency.
- **Document store** — one nested document per read. Embed a field when that copy is the fact the page must keep.
- **Column-family store** — a wide row under one key, ordered for the slice you read. A different predicate reads every partition.
- **Graph database** — the query walks edges. A single foreign key stays a join on the primary.
- **Time-series database** — append a point, query a range, roll it up, and expire the raw samples. The hourly series is coarser.
- **Search index store** — terms point at ids. The primary holds the row. The index is a copy and can lag.
- **Data warehousing** — long scans on a column-oriented copy, off the booking primary. Freshness is the lag of the copy.

## Example

A tool library. The booking updates a deposit and inserts a reservation, at 200 writes per second, on a primary measured at 1,500. The feed appends 20,000 posts per second under a member id. Forty open reservations embed a catalog price that has since changed. One checkout series keeps 14 days of 10-second samples and 90 days of hourly averages.

```python
def choose(cross_row: bool, writes: int, cap: int) -> str:
    if cross_row and writes <= cap:
        return "relational"
    if not cross_row and writes > cap:
        return "nosql"
    return "measure"


def points_kept(samples_per_day: int, raw_days: int, hourly_days: int) -> int:
    return samples_per_day * raw_days + 24 * hourly_days


print(choose(True, 200, 1500), choose(False, 20_000, 1500), 40, points_kept(6 * 60 * 24, 14, 90))
# relational nosql 40 123120
```

The booking stays on the relational primary. The feed is a column family. The 40 embedded prices disagree with today's catalog, so that page should read the tool row. The series keeps 123,120 points, and the hourly averages do not restore a 10-second spike. A search index and a warehouse are further copies of the primary, for words and for the yearly borough report.

## See also

- [Databases Relational](../06_Databases_Relational/) — the primary, its indexes, and Choosing Relational or NoSQL.
- [Caching](../05_Caching/) — a rebuildable copy, and cache-aside in front of the primary.
- [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/) — which machine owns a key, and what moves when one joins.
- [Consistency and Replication](../09_Consistency_and_Replication/) — stale reads, quorums, and how two writes of one key are ordered.
- [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/) — the batch job or change stream that feeds a warehouse or a search index.
- [Search, Autocomplete, and Information Retrieval](../18_Search_Autocomplete_and_Information_Retrieval/) — inverted indexes, ranking, and autocomplete.
