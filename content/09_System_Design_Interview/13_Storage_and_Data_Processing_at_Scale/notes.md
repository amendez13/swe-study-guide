# Storage and Data Processing at Scale

Large files and large computations need a home and a schedule. Photos and click logs land in an object store such as S3. A database page lives on a block volume. A multi-terabyte scan can use a distributed file system such as HDFS. Raw files sit in a lake until a job curates them and a warehouse answers SQL. A batch job, MapReduce or Spark, reads a finished input. A stream job, Kafka and Flink, updates a result as events arrive. Change data capture and event sourcing are how a committed row, or the events themselves, feed another view.

## Key Points

- **Object storage** — a key, a blob, and metadata. S3 Standard is designed for eleven nines of durability over a year and 99.99% availability. Hot and cold classes, and a pre-signed URL, are store choices. The upload product and a public edge copy stay in Content Distribution and Media.
- **Block storage** — a volume the host mounts and reads at an offset. An 8 KB database page is the usual example. A chunk store may keep a repeated checksum once. Syncing a folder to a laptop stays in Content Distribution and Media.
- **Distributed file system** — HDFS keeps a shared tree for a huge file, written once and scanned straight through. The default block is 128 MiB and the default replication is 3. Millions of tiny files spend the NameNode.
- **Data lake** — raw files on object storage. A later job writes a curated file. The analytical tables are Data Warehousing, and a columnar file layout stays in Encoding Serialization and Schema Evolution.
- **Batch processing** — a scheduled job over a complete input, minutes to hours. Map, shuffle, and reduce are the teaching shape. Spark keeps that grouping and can hold intermediates in memory.
- **Stream processing** — a job that stays up. Windows are on event time, and a watermark decides when a window can close. A short grace can still count a late event. The log and a duplicate delivery stay in Message Queues and Async Processing.
- **Batch or stream** — a closed set that can wait, or a check that has to fire in seconds. Asking for both is the next card.
- **Lambda or Kappa** — a batch path plus a speed path, merged as batch plus the speed total after the cutoff, or one stream job that rebuilds by replaying a log. Overlap counts an event twice. The log's retention stays in Message Queues and Async Processing.
- **Change data capture** — tail the write-ahead log or binlog, including deletes. A cache, a search index, and a warehouse are the usual destinations. An outbox table is Transactional Outbox.
- **Event sourcing** — the events are the source of truth. A snapshot skips a full replay and must match the fold. A projection serves a reader. Schema changes on an event stay in Encoding Serialization and Schema Evolution.

## Example

A product received 1000 units, shipped 40, shipped 25, and received 100. Yesterday's batch count of page views is 48,200, and the speed path has 860 from after midnight. The product page's budget for a first byte is 50 ms. An archived photo in a cold class takes 800 ms before the first byte.

```python
def fold(events: list[tuple[str, int]], start: int = 0) -> int:
    level = start
    for kind, amount in events:
        level += amount if kind == "receive" else -amount
    return level


def query(batch: int, speed_after_batch: int) -> int:
    return batch + speed_after_batch


EVENTS = [("receive", 1000), ("ship", 40), ("ship", 25), ("receive", 100)]
print(fold(EVENTS), query(48_200, 860), 800 <= 50)
# 1035 49060 False
```

The fold leaves 1035 units on hand. A snapshot after the first ship is 960, and the tail brings it back to 1035, the same fold. The query is yesterday's batch plus today's speed path with no overlap, 49,060. The cold read misses the 50 ms budget, so the live product row stays on the primary and the archived photo stays in object storage. The morning page-view report can wait for a complete file. Checkout failures crossing a threshold have to page while the failures are still happening.

## See also

- [Interview Framework and Process](../01_Interview_Framework_and_Process/) — QPS and Storage Estimate. How many bytes a year of objects is, and the request rate in front of them.
- [Caching](../05_Caching/) — Cache Invalidation. A captured row change can drop a stale product page.
- [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/) — Data Warehousing and Search Index Store. This topic feeds those stores.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Log or Queue, Message Delivery Guarantees, and Transactional Outbox. Processing reads the log. The broker choice stays there.
- [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/) — Columnar Storage Formats and Schema Evolution. A lake file's layout, and a new field on an event.
- [Content Distribution and Media](../22_Content_Distribution_and_Media/) — Why a CDN, Video Uploading and Transcoding, and File Sync and Conflict Resolution. A pre-signed URL and a chunk checksum are store facts. The product flows stay there.
