# Storage and Data Processing at Scale

Lock Fourteen weighs grain, keeps the probe files, and has to know both yesterday's closed total and that a silo just ran hot. The bytes live in an object, on a volume, or in a shared file tree. Raw files land in a lake. A batch job reads a finished set. A stream job folds events as they arrive. Change data capture and event sourcing are how a committed row, or the events themselves, feed another view.

## Key Points

- **Object storage** — a key, a blob, and metadata. Durable and large, with a wait for the first byte. Hot and cold classes, and a pre-signed PUT, stay a store choice. The upload product and a public edge copy stay in Content Distribution and Media.
- **Block storage** — a volume or fixed-size chunks a host mounts and reads at an offset. A chunk already stored under the same checksum can be kept once. Syncing a file to a laptop stays in Content Distribution and Media.
- **Distributed file system** — a shared tree for a huge file, written once and scanned straight through. Millions of tiny files spend the metadata service.
- **Data lake** — raw files on object storage. A later job writes a curated set. The analytical store is Data Warehousing, and a columnar file layout stays in Encoding Serialization and Schema Evolution.
- **Batch processing** — a scheduled job over a complete input, minutes to hours. Map, shuffle, and reduce are the teaching shape.
- **Stream processing** — a job that stays up, windows on event time, and a watermark for late events. The log and a duplicate delivery stay in Message Queues and Async Processing.
- **Batch or stream** — a closed set that can wait, or a check that has to fire in seconds. Asking for both is the next card.
- **Lambda or Kappa** — a batch path plus a speed path, or one stream job that rebuilds by replaying a log. The log's retention stays in Message Queues and Async Processing.
- **Change data capture** — tail the write-ahead log or binlog, including deletes. A cache, a search index, and a warehouse are the usual destinations. An outbox table is Transactional Outbox.
- **Event sourcing** — the events are the source of truth. A snapshot skips a full replay. A projection serves a reader. Schema changes on an event stay in Encoding Serialization and Schema Evolution.

## Example

Lot 18 received 1000 bushels, shipped 40, shipped 25, and received 100. Yesterday's batch total is 48,200 bushels, and the speed path has 860 from after midnight. The yard screen's budget for a first byte is 50 ms. A sealed scan in the cold class takes 800 ms to start.

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

The fold leaves 1035 bushels on the floor. A snapshot after the first ship is 960, and the tail brings it back to 1035, which is the same fold. The query is yesterday's batch plus today's speed path with no overlap, 49,060. The cold scan misses the screen budget, so the open lot stays on the primary and the sealed probe file stays in object storage. The morning settlement can wait for a complete file. Silo 4 crossing 40 C has to ring while the grain is still in the bin.

## See also

- [Interview Framework and Process](../01_Interview_Framework_and_Process/) — QPS and Storage Estimate. How many bytes a season of probes is.
- [Caching](../05_Caching/) — Cache Invalidation. A captured change can drop a stale lot card.
- [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/) — Data Warehousing and Search Index Store. This topic feeds those stores.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Log or Queue, Message Delivery Guarantees, and Transactional Outbox. Processing reads the log. The broker choice stays there.
- [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/) — Columnar Storage Formats and Schema Evolution. A lake file's layout, and a new field on an event.
- [Content Distribution and Media](../22_Content_Distribution_and_Media/) — Why a CDN, Video Uploading and Transcoding, and File Sync and Conflict Resolution. A pre-signed PUT and a chunk are store facts. The product flows stay there.
