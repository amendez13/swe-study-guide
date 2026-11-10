## Object Storage

An object store keeps a blob under a string key, with a little metadata beside it: content type, size, and a checksum. Amazon S3 is the system this card describes. An 8 MB product photo lives at a key such as `photos/2026/11/img-1842.jpg`, and a read names that key.

**Why it exists.** Databases and attached disks are a poor home for files that are written once and then fetched whole. Photos, video uploads, backups, and log objects fill a disk, and they have to survive the loss of any one disk. An object store takes those blobs, spreads them across many machines, and grows as you add objects. There is no volume to size beforehand.

**How it works.**

1. The client sends a PUT with the key, the bytes, and the metadata. An 8 MB photo is one request. S3 accepts a single PUT up to 5 GB. A larger object is uploaded in parts (up to 5 TB) and assembled under the same key.
2. The service stores the blob, usually protected by replication or erasure coding across disks and machines, and records the key. Amazon S3 Standard is designed for 99.999999999% (eleven nines) durability of objects over a given year. Availability is a separate target: S3 Standard is designed for 99.99% availability.
3. A GET names the key and returns the object. From the same region the first byte often arrives in tens to a couple of hundred milliseconds. A range request can return a slice of the bytes, and the caller still names the key.
4. A LIST under the prefix `photos/2026/11/` returns keys that begin with that string. The folder is the prefix.
5. Since December 2020, S3 has provided strong read-after-write consistency for GET, PUT, LIST, and DELETE. After a successful PUT, a following GET or LIST of that key sees the new object.

A second PUT of the same bytes under a different name stores another object. If the key is a checksum of the bytes, that second upload can refer to the object already stored. A caller that should not hold a long-lived access key can receive a pre-signed URL, for example one that expires in 15 minutes, and PUT or GET through that URL alone.

**Trade-offs.** Storage classes trade retrieval speed for price. This week's photos can stay in a standard class. Last year's photos can move to a cheaper class. Some cold classes still return the first byte in milliseconds (S3 Glacier Instant Retrieval). S3 Glacier Flexible Retrieval typically restores an object in 1–5 minutes on the expedited tier (AWS quotes that for objects under 250 MB) and in 3–5 hours on the standard tier. Its bulk tier typically finishes in 5–12 hours. S3 Glacier Deep Archive typically restores within 12 hours, or within 48 hours on the bulk tier. A page that must paint in a few milliseconds reads a database or a cache, and leaves the blob for a download. Replacing an object means writing the whole blob again. With versioning on, the previous blob remains as an older version. You address a key. You do not mount the bucket and patch 8 KB in the middle. That interface is block storage.

**In an interview.** Say "S3-style object storage" for a whole file addressed by key: images, uploads, backups, and data-lake files. Quote eleven nines as S3's durability design target, and keep availability as the lower number. Name the storage class when the working set is hot and the archive is cold. Offer a pre-signed URL when a browser should upload without your credentials. The upload product built around that URL is Video Uploading and Transcoding in [Content Distribution and Media](../22_Content_Distribution_and_Media/). A public photo read from many cities is Why a CDN in that same topic. How many bytes a year of objects is, and the request rate, is QPS and Storage Estimate in [Interview Framework and Process](../01_Interview_Framework_and_Process/).

- A PUT stores the key, the blob, and metadata such as content type and checksum.
- A GET of `photos/2026/11/img-1842.jpg` returns that object. A range read still names the key.
- A LIST under `photos/2026/11/` is a prefix match. The folder is that prefix.
- S3 Standard is designed for eleven nines of durability over a year, and for 99.99% availability.
- A hot class opens in tens to a couple of hundred milliseconds. Some archive classes need a restore of minutes or hours.
- A pre-signed URL authorizes one upload or download until it expires.

![Object Storage](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing-1-object-storage.png)

*Source: [`diagrams/storage-processing.drawio`](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing.drawio), page 1.*

## Block Storage

A block store presents a volume that a host treats as a disk. The host reads and writes a range of bytes at an offset. Amazon EBS, a SAN LUN, and an iSCSI target are this interface.

**Why it exists.** A database rewrites one page inside a large file, many times a second. PostgreSQL's default page is 8 KB. The operating system, or the database itself, needs something it can mount and seek. An object store addresses a whole key. A distributed file system addresses a shared path. The page store under the database is a volume.

**How it works.**

1. The service hands the host a volume of a chosen size, for example 500 GB.
2. The host formats a filesystem, or the database writes pages directly. Page 0 is bytes 0–8191. Page 1 starts at offset 8192. A read of page 100 is a read at offset 819,200.
3. The volume can be detached from a failed host and attached to its replacement. Most cloud volumes attach to one host at a time. Multi-attach exists for specific volume types, and the filesystem has to understand shared writers.
4. Some chunk-based and backup stores split the volume into chunks and keep a chunk once when its checksum is already stored. A plain attached volume stores the blocks you write, duplicates included.

**Trade-offs.** You get low-latency random reads and writes, a provisioned size, and snapshots of the volume. You expand the volume when it fills, and you pay for the size you allocated. An object store grows by the byte and has no attach step, with a coarser interface. A distributed file system fits when many machines open the same huge file by path and scan it. Syncing a user's folder to a laptop, including two offline edits of the same file, is File Sync and Conflict Resolution in [Content Distribution and Media](../22_Content_Distribution_and_Media/). The chunk on this card is only the way the store lays out bytes.

**In an interview.** Put the database data directory on block storage. Put images, logs, and lake files in object storage. Put a multi-terabyte sequential scan on a distributed file system, or on object storage the batch engine can read. Say the operation out loud: "8 KB at an offset" versus "GET the whole key."

| Store | How you address the bytes | When it fits |
| --- | --- | --- |
| Object storage | One key returns the blob. | Photos, backups, log objects, and lake files. |
| Block storage | A mounted volume, then a range at an offset. | Database pages and other small random reads and writes. |
| Distributed file system | A path in a tree shared by many machines. | A huge file written once and scanned straight through. |

![Block Storage](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing-2-block-storage.png)

*Source: [`diagrams/storage-processing.drawio`](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing.drawio), page 2.*

## Distributed File System

A distributed file system is a directory tree whose bytes live on many machines. A metadata service records which machine holds each block. HDFS is the teaching system: a NameNode holds the namespace, and DataNodes hold the blocks.

**Why it exists.** A single disk cannot hold a multi-terabyte click log, and a batch job wants to scan that file from the first byte to the last on several machines at once. Copying the whole file to every worker wastes the cluster. The file system places the blocks on the data nodes, and the job reads the blocks where they already sit.

**How it works.**

1. A client creates a path such as `/logs/clicks/2026-11-09.log` through the NameNode.
2. The file is cut into large blocks. HDFS uses 128 MiB blocks by default. A 2 TiB file is 16,384 blocks (`2 × 1024 × 1024 / 128`).
3. Each block is stored on several DataNodes. The default replication factor is 3, so the cluster holds 49,152 block replicas. A lost disk is repaired by copying a surviving replica.
4. The NameNode keeps the directory and the block list in memory. Hadoop's planning figure is on the order of 150 bytes of heap per file, directory, or block.
5. Jobs open the path and read straight through. The intended life of a file is one writer that finishes it, then many readers.

**Trade-offs.** The layout fits a huge file, written once, and scanned from start to finish. Two million files of a few kilobytes are a different workload. At about 4 KB each they hold only about 8 GB of data, and each file plus its block is a NameNode object: about four million objects, on the order of 600 MB of metadata by the 150-byte planning figure. The 2 TiB file is 16,384 blocks and a few megabytes of metadata. The tiny files also force the job to open millions of paths. A random read of one 8 KB page is the same mismatch, because the block was sized for a long scan. HDFS can append, and that append is still one sequential writer. Random updates in the middle of the file, and two writers at once, sit outside the design. Object storage has taken this landing zone for a lot of new data. You no longer run the metadata service, and Spark or a similar engine can scan an object. Keep the shared file system when the job already has a path, the file is huge, it was written once, and the read runs straight through.

**In an interview.** Name HDFS, the 128 MiB block, replication 3, and the NameNode as the metadata bottleneck. Prefer object storage for a new lake unless an existing job needs the path. Mention small files before you propose HDFS for logs that arrive as one file per event.

- A 2 TiB file at the 128 MiB default is 16,384 blocks, and replication 3 stores 49,152 replicas.
- The NameNode holds the directory and the block map. Plan on about 150 bytes of heap per file, directory, or block.
- The fit is one writer, then many sequential readers.
- Millions of tiny files pressure the metadata service long before they fill the disks.
- New landing zones often use object storage and let the batch engine scan the objects.

![Distributed File System](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing-3-distributed-file-system.png)

*Source: [`diagrams/storage-processing.drawio`](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing.drawio), page 3.*

## Data Lake

A data lake is where raw files land, almost always on object storage such as S3, GCS, or ADLS. The click collector writes the bytes it captured, under a prefix such as `s3://logs/clicks/2026/11/09/`. Those bytes have not been joined to a user or summed by page.

**Why it exists.** Loading every new feed into a warehouse table before it can land drops fields you later wish you had kept, and it blocks the file until someone designs the schema. The lake stores the capture cheaply so a new question can start from the original bytes.

**How it works.**

1. Producers PUT raw files. The schema is whatever is inside the file, and a job applies it when the file is read. That is schema on read. A file may be JSON, CSV, or Parquet.
2. A later batch job reads yesterday's prefix, drops bad rows, and writes a curated object: one file of cleaned daily clicks that another job can trust.
3. A load job can copy that curated file into warehouse tables, where an analyst runs SQL.
4. The raw files stay. When the curated job had a bug, a new job can read the capture again.

**Trade-offs.** A lake with no owner and no curated output becomes a pile of files in three date formats that no query trusts. The warehouse is the other bet: tables with a schema, built for the long analytical question. That store is Data Warehousing in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). A columnar layout for the file a scan actually reads is Columnar Storage Formats in [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/). Table formats such as Apache Iceberg, Delta Lake, and Apache Hudi add transactions and a schema on top of the lake files. They narrow the gap, and they still sit on the object store. Say so when the analyst's SQL runs on those tables directly.

**In an interview.** Put the unchanged capture in the lake, name the job that writes the curated file, and put the analyst's year-long query in the warehouse or in an explicit lakehouse table. Say who is allowed to read the raw prefix. The lake holds files. The warehouse holds the tables those files can load.

| Artifact | Where it lives | Who writes it |
| --- | --- | --- |
| The click file, bytes unchanged | The lake, on object storage | The collector |
| One cleaned file for the day | A curated object, derived from a raw prefix | A batch job |
| Clicks by page for last year | The warehouse | A load into warehouse tables |

![Data Lake](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing-4-data-lake.png)

*Source: [`diagrams/storage-processing.drawio`](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing.drawio), page 4.*

## Batch Processing

A batch job reads a finished input, runs to completion, and writes an output. Yesterday's click logs are closed. The job starts on a schedule, may run for minutes or hours, and writes a rollup. A click that arrives while the job is running waits for the next run.

**Why it exists.** Some answers are meaningful once the set is complete: page views for a closed day, a curated lake file, a full rebuild of a statistic. Processing those events one by one spends complexity on latency the reader did not ask for. Throughput is the point. The morning report can wait until 06:00.

**How it works.** The teaching shape is MapReduce. Spark uses the same shape for a group-by, and it can keep the intermediate rows in memory, spilling to disk when a partition is large.

1. Map. Each worker reads a slice and emits pairs. Clicks on pages `a`, `a`, and `b` become `(a, 1)`, `(a, 1)`, `(b, 1)`.
2. Shuffle. The engine groups pairs by key, so every pair for page `a` meets on one reducer.
3. Reduce. That reducer sums the values. If the slices for page `a` contributed 250, 100, 50, and 600, the reducer writes 1,000.
4. The output is a report file, a curated lake object, or a load for the warehouse.

The warehouse load is Data Warehousing in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). A columnar file the job writes is Columnar Storage Formats in [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/). Use a batch job when the input can be complete before anyone needs the answer.

**Trade-offs.** The job can sort, join, and aggregate the whole set, and the same input can be run again to fix a bug. The result is late by the schedule plus the runtime: a 02:00 job that runs 40 minutes describes yesterday. A click from 30 seconds ago is in the next run. A stream job is the alternative when the result has to move while events are still arriving.

**In an interview.** Name the closed input and the deadline. If the reader can wait until the input is sealed, one scheduled job is enough. Say what is late: anything that arrives after the seal waits for the next run. Walk map, shuffle, and reduce with a small sum, and say that Spark is that grouping with a faster engine.

- The input is a closed set: yesterday's logs, an object prefix, or a database dump.
- Map emits `(page, 1)`. Shuffle brings one page's pairs together. Reduce writes the total. Here that total is 1,000.
- The job runs for minutes or hours after the input is complete.
- A click that arrives during the run is counted in the next run.

![Batch Processing](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing-5-batch-processing.png)

*Source: [`diagrams/storage-processing.drawio`](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing.drawio), page 5.*

## Stream Processing

A stream job stays up. It reads events as they arrive and updates a result while those events are still fresh. Kafka is the usual log. Flink is the usual processor. A click, a checkout, or a sensor reading is one event.

**Why it exists.** The morning batch cannot page someone within seconds. A fraud check, a live counter, or "checkout failures crossed 50 in a minute" needs a result that moves with the events. The input is never finished, so the job has to decide when a window is complete enough to emit.

**How it works.**

1. Producers append events to a Kafka topic. Each event carries an event-time timestamp: when the click happened. That clock can differ from processing time, the minute the job received the event.
2. The job groups events into windows on event time. A tumbling window of five minutes is `[0, 5)`, then `[5, 10)`, then `[10, 15)`, with no overlap. A sliding window overlaps the one before it, for example a five-minute window that starts every minute. A session window closes after a gap with no events, so the boundary is idle time.
3. The job keeps a watermark: the event time it is willing to treat as complete. Watermarks usually trail the newest timestamp by a small bound, so a slightly late event still arrives before the window closes. In the hand calculation this topic uses, a window that ends at `end` stays open while `watermark < end`.
4. An event whose event time is already behind the watermark is late. A grace interval can still count it. With the watermark at minute 15 and a grace of 2 minutes, an event still counts when its event time is at least `15 - 2`. Minute 14 is in the closed window that ends at 15, and it still counts. Minute 12 is in that same window and past the grace, so the job drops it or writes it aside. Minute 16 is in the window that ends at 20, and the watermark has not passed that end, so the window is still open.
5. The job writes the aggregate for a closed window to a sink: a database row, a cache key, or another topic.

Flink's allowed lateness is the production version of that grace idea: a bounded period after the window end during which a late event may still update the result, after which the event goes to a side output. The hand rule above measures grace back from the watermark so the arithmetic stays small. The decision you defend is the same. How late an event may still change the result, and where the rest goes.

The log this job reads, and a delivery that can hand the same event twice, are Log or Queue and Message Delivery Guarantees in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

**Trade-offs.** You get freshness of seconds. You take on late data, out-of-order events, and duplicate delivery. An at-least-once log counts an event twice unless the update is idempotent or the sink deduplicates. Flink can offer exactly-once output for a pipeline whose sink participates, for example with Kafka transactions. That property belongs to the pipeline. A large grace keeps windows open and holds state. A tiny grace drops events from a slow producer.

**In an interview.** Separate event time from processing time before you pick a window. Say tumbling, sliding, or session. Name the watermark, and say what a late event does: update the window inside grace, or leave the result. Point duplicate delivery at Message Delivery Guarantees.

- Event time is the timestamp on the event. Processing time is when the job sees it.
- A tumbling window of five minutes does not overlap the next one. A sliding window does.
- The watermark is how far in event time the job treats the stream as complete.
- With the watermark at minute 15 and a grace of 2 minutes, minute 14 still counts, minute 12 is dropped or set aside, and minute 16 is in an open window.
- The same event can arrive twice. The count stays honest when the update is idempotent or the sink deduplicates.

![Stream Processing](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing-6-stream-processing.png)

*Source: [`diagrams/storage-processing.drawio`](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing.drawio), page 6.*

## Batch or Stream

Batch and stream are two schedules for an aggregate. A batch job fits a complete set whose reader can wait. A stream job fits a check that has to be fresh. A number that has to be both yesterday's closed total and the last minute's total is two results.

**Why it exists.** One job asked to be both the reconciled daily total and the alert from 30 seconds ago misses one of those requirements. The choice is which result the reader needs, and whether the input is closed.

**How it works.**

1. The morning report is page views by page for yesterday. The sheet is due at 06:00, and it has to include every click from the closed day. The input can be sealed. One scheduled batch job is enough.
2. Checkout failures crossed 50 in the last minute, and on-call should hear within a few seconds. The events are still arriving. A stream job on Kafka and Flink is the fit.
3. The office wants yesterday's closed total and the page views from the last minute. Those are two results. Serving both is Lambda or Kappa, the next card.

The log under the fresh path is Log or Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

**Trade-offs.** Batch is simpler to rerun and easier to make complete, and the answer is late. Stream is fresh, and it needs windows, a watermark, and a plan for duplicates. Asking for both means two results that must be combined so the same event is counted once.

**In an interview.** Ask when the reader needs the answer, and whether you can name the closed input. Closed day and a 06:00 deadline is batch. A page within seconds is stream. Both a closed total and a live slice means you say "two results" and move to Lambda or Kappa.

| Need | Choice |
| --- | --- |
| The closed day is complete, and the reader can wait until morning. | Batch. |
| A check has to fire within seconds. | Stream. |
| The reader wants the closed day and the last minute. | Both results. Lambda or Kappa. |

![Batch or Stream](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing-7-batch-or-stream.png)

*Source: [`diagrams/storage-processing.drawio`](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing.drawio), page 7.*

## Lambda or Kappa

Lambda and Kappa are two ways to serve a closed historical result and a fresh result together. Lambda runs a batch path and a speed path. Kappa keeps one stream path and rebuilds by replaying a log.

**Why it exists.** A batch job is the total people will reconcile, and it is blind after its cutoff. A stream job is fresh, and it is awkward to rebuild unless the log still holds the history. The architecture is how those two facts become one number.

**How it works.** Lambda has three pieces. The batch layer reads the closed day and writes the reconciled view. The speed layer folds events after that cutoff. The serving layer stores both views and answers the query.

1. Yesterday's batch total is 48,200 page views, and it covers every event through midnight.
2. The speed path has 860 page views from after midnight.
3. The query adds the batch total to the speed total from after the cutoff: `48,200 + 860 = 49,060`.
4. A second speed total of 2,060 still includes 1,200 page views from late yesterday that the batch already counted. Adding that longer total produces `48,200 + 2,060 = 50,260`. Those 1,200 page views are in the answer twice.
5. The batch path can be run again to correct a bad day. Until that run lands, the two copies of "page views by page" can disagree.

Kappa drops the second implementation. The events sit in a log. A corrected job starts again from the retained offsets and rebuilds the totals, so there is one codebase. The rebuild sees only the events the log still holds. Kafka's default time retention is 7 days (`log.retention.hours=168`), and operators change it. A compacted topic keeps the latest record per key, so it can rebuild a current value and it cannot replay a history that compaction already dropped. How long a log keeps a record is Log or Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

```python
def query(batch: int, speed_after_batch: int) -> int:
    return batch + speed_after_batch


print(query(48_200, 860), query(48_200, 860 + 1_200))
# 49060 50260
```

**Trade-offs.** Lambda fits when a trusted batch result already exists and the fresh slice is thin. The cost is two copies of the logic that can disagree until the batch lands, and a serving query that must not overlap them. Kappa fits when replaying the log is acceptable and a second implementation is the cost to skip. The cost is retention long enough to rebuild, and a stream job that can reprocess that history.

**In an interview.** Write the query as batch plus the speed path after the cutoff, and show the double count when the ranges overlap. Choose Lambda when the nightly batch is already the system of record. Choose Kappa when you can say how long the log keeps events and that one code path will rebuild them.

- Lambda serves the batch total through the cutoff plus the speed total after the cutoff. Here that is 49,060.
- Adding speed rows the batch already counted produces 50,260. Those events are in the answer twice.
- Kappa is one stream job. Replaying the retained log rebuilds the totals.
- A compacted log keeps the latest record per key. A full rebuild needs the history the log still holds.

![Lambda or Kappa](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing-8-lambda-or-kappa.png)

*Source: [`diagrams/storage-processing.drawio`](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing.drawio), page 8.*

## Change Data Capture

Change data capture hands each committed insert, update, and delete to another store. The usual read is the database's own recovery log: the Postgres write-ahead log, or the MySQL binlog. The primary already wrote that log so it can recover. A tailer reads it after the commit. Debezium is the usual tailer.

**Why it exists.** A cache, a search index, and a warehouse need the committed row, including the moment it disappears. A timer that polls the table rereads rows that did not change. A delete is easy to miss once the row is gone, unless the application soft-deletes and leaves a flag behind. The log already contains the change.

**How it works.**

1. The application commits on the primary. Order 1842 moves from `hold` to `shipped`. A voided order is deleted. Both changes are in the WAL or the binlog.
2. The connector often starts with a consistent snapshot of the table, then follows the log so later commits keep the copy current.
3. The tailer emits those commits in log order. The reader decides the destination. The product page drops a stale copy: Cache Invalidation in [Caching](../05_Caching/). Catalog search updates Search Index Store in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). The monthly revenue report lands in Data Warehousing in that same topic.
4. An outbox table written in the same database transaction is a different tool. Use it when a message must commit or roll back with the business write. That pattern is Transactional Outbox in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

**Trade-offs.** Log-based capture sees deletes and skips the quiet rows a poll would reread. It couples you to the database's log format, and the tailer has to keep up: a log that is recycled before it is read loses the change. There is lag. The cache and the search index update after the commit, on that lag. Polling is simpler to start, costs reads on rows that did not change, and misses a hard delete.

**In an interview.** Say "tail the WAL or binlog" before you say "poll `updated_at`." Name the destination: invalidate a cache, upsert a search document, or load a warehouse row. Mention the delete. When the message has to be in the same transaction as the row, that is the outbox, and it belongs in the queue topic.

- The capture reads the WAL or the binlog, so a delete is an event in the log.
- A product-page cache drops its stale copy.
- Catalog search updates the search index.
- A monthly report lands the row in the warehouse, off the primary.
- A message that must commit with the row is Transactional Outbox, written by the application.

![Change Data Capture](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing-9-change-data-capture.png)

*Source: [`diagrams/storage-processing.drawio`](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing.drawio), page 9.*

## Event Sourcing

Event sourcing stores each change as an immutable event. The current value is a fold of that sequence. The events are the source of truth. A table of the current value is a copy that can be rebuilt from them.

**Why it exists.** A column that only stores "1,035 units on hand" drops the history that produced it. A bad overwrite is hard to explain or rebuild. The events still decide the number, and a new screen can be built later by folding the same history a different way.

**How it works.** Take a product's stock. The events, in order, are receive 1000, ship 40, ship 25, and receive 100.

1. A command appends an event. It does not update a stock column in place.
2. The fold applies the sequence. Start at 0. Receive 1000 leaves 1000. Ship 40 leaves 960. Ship 25 leaves 935. Receive 100 leaves 1035. The units on hand are 1035.
3. A snapshot is the fold saved at an event number, for speed. A snapshot after the first ship holds 960. A reader starts there and applies the tail, ship 25 and receive 100: `960 - 25 + 100 = 1035`. That matches a fold from the first event and skips a scan of the whole history. Throw the snapshot away and the events still decide the value.
4. A projection is one fold shaped for a reader, such as the stock count on the product page. Writes append events. Reads use the projection. That split is CQRS, command query responsibility segregation: the write model is the event log, and the read model is the projection.

The log that holds the events is Log or Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). A new field an old reader has to skip is Schema Evolution in [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/).

```python
def fold(events: list[tuple[str, int]], start: int = 0) -> int:
    level = start
    for kind, amount in events:
        level += amount if kind == "receive" else -amount
    return level


events = [("receive", 1000), ("ship", 40), ("ship", 25), ("receive", 100)]
snapshot = fold(events[:2])
print(fold(events), snapshot, fold(events[2:], snapshot))
# 1035 960 1035
```

**Trade-offs.** You keep an audit trail, and you can rebuild a projection or answer "what was on hand after the second event?" You take on a longer write path, event shapes that have to evolve, and queries that are awkward until a projection exists. A snapshot can be stale or wrong. The recovery is to rebuild it from the events. This fits a domain whose history matters: orders, inventory movements, a ledger. A profile row that is simply overwritten is a heavy place to start.

**In an interview.** Walk the four events and show the snapshot plus the tail reaching the same total. Say the events are the source of truth and the projection is disposable. Name CQRS as the split between appending events and reading a projection. Leave the broker, delivery, and schema rules in their own topics.

- The events are receive 1000, ship 40, ship 25, and receive 100.
- The fold is 1035 units still on hand.
- A snapshot through the first ship holds 960, and the tail brings it back to 1035.
- The product page reads a projection built from those same events.
- The snapshot is for speed. Deleting it leaves the events in charge of the value.

![Event Sourcing](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing-10-event-sourcing.png)

*Source: [`diagrams/storage-processing.drawio`](/content/09_System_Design_Interview/13_Storage_and_Data_Processing_at_Scale/diagrams/storage-processing.drawio), page 10.*
