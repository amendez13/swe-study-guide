## Object Storage

An object store keeps a blob under a key, with a little metadata beside it. Lock Fourteen puts an 8 MB photo of a scale ticket at `tickets/2026/11/lot-18.jpg`, together with a content type and a checksum. A get returns that whole blob. A list under the prefix `tickets/2026/11/` is a string match on the key. Folders are that prefix. Mounting a volume is the next card.

The ticket survives a lost disk. Interview answers quote eleven nines, 99.999999999 percent, as the durability expected of this class of store, and the capacity grows with the harvest without a volume sized beforehand. The wait for the first byte is the cost. That wait is a poor fit for the open-lot page the yard screen reads on every truck. This week's tickets can sit in a hotter class that opens sooner. Last season's probes can sit in a colder, cheaper class. A second put of bytes the checksum already names can point at the object already stored. A caller that should not hold a long-lived credential can receive a pre-signed PUT that expires. The upload product around that URL is Video Uploading and Transcoding in [Content Distribution and Media](../22_Content_Distribution_and_Media/). A public photo read from many cities is Why a CDN in that same topic. Sizing a season of probes is QPS and Storage Estimate in [Interview Framework and Process](../01_Interview_Framework_and_Process/).

```text
PUT   tickets/2026/11/lot-18.jpg    key, blob, metadata
GET   tickets/2026/11/lot-18.jpg    the whole blob, after the first byte
LIST  tickets/2026/11/               a prefix match
hot   this week's tickets, sooner to open
cold  last season, cheaper, slower to open
```

## Block Storage

A block store presents a volume, or a set of fixed-size chunks, that a host treats as a disk. The open-lot database on the desk host mounts the volume and reads an 8 KB page at a chosen offset. The volume can be detached from a failed host and attached to its replacement. The caller addresses ranges. The ticket photo stays a key and a whole blob.

Fetching that whole blob is object storage. A distributed file system, the next card, is a shared tree of files across many machines. When the bytes are stored as chunks, a chunk whose checksum is already on disk can be kept once. A product that splits a grower's sheet into chunks, sends the changed chunks to a laptop, and keeps both copies when two offline edits diverge is File Sync and Conflict Resolution in [Content Distribution and Media](../22_Content_Distribution_and_Media/). The chunk on this card is the store type.

```text
object   one key, the whole blob, no mount
block    a volume or fixed-size chunks, mounted, a range at an offset
dfs      a shared tree of files on many machines
```

## Distributed File System

A distributed file system is a directory tree whose bytes live on many machines. The layout fits a large file read from the first byte to the last. The belt-history file is about 2 TB, and the nightly job opens it and scans. The usual cut is large blocks, more than one copy of each block, and a metadata service that holds the directory and the block list. HDFS is the teaching system: write the file once, then let many jobs read it. A second writer appending that same file is the case this layout handles poorly.

Small files spend the metadata service before they fill the data disks. Two million ticket files of a few kilobytes are two million directory records. A random read of one page is the same mismatch, because the block is large for a scan. Object storage has taken this landing for a lot of new files: the metadata service is no longer yours to run, and a batch engine can scan an object. Keep the shared file system when the job already has a path, the file is huge, it was written once, and the read runs straight through.

```text
fits    a huge file, written once, scanned from start to finish
hurts   millions of tiny files, random small reads, several writers
```

## Data Lake

A data lake is where raw files land, almost always on object storage. The moisture probe writes the bytes it captured. Those bytes have not been joined to a grower or summed by variety. A later job reads a prefix and writes a curated set, one file of cleaned daily rows that another job can trust. The raw files stay, so a new question can start from the capture.

The store built for the long analytical question is Data Warehousing in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). The schema of that store stays there. A columnar layout for the scanned file is Columnar Storage Formats in [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/). The lake holds the raw landing and the curated files jobs derive from it. The warehouse is where the analyst's query runs.

```text
lake       raw capture on object storage
curated    a later job's file, derived from a raw prefix
warehouse  the analytical store those files can load
```

## Batch Processing

A batch job reads a finished input. Yesterday's tickets are closed, the job starts on a schedule, and it may run for minutes or hours. It can sort, join, and aggregate the whole set, then write a settlement sheet, a curated lake file, or a load for the warehouse. A ticket that shows up while the job is running waits for the next run. The reader is the morning sheet, hours after the truck left. Throughput is the point.

The teaching shape is map, then shuffle, then reduce. Each worker reads a slice and emits a key with a value, the bushels on one ticket. Shuffle brings one grower's rows together. Reduce writes that grower's total. An engine may keep the intermediate rows in memory and still follow that shape. The warehouse load is Data Warehousing in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). A columnar file the job writes is Columnar Storage Formats in [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/). Use a batch job when the input can be complete before anyone needs the answer.

```text
input     a closed set: yesterday's tickets, a prefix, a dump
map       emit grower, bushels
shuffle   one grower's rows meet
reduce    write the total
latency   minutes to hours, after the input is complete
```

## Stream Processing

A stream job stays up. Each event is a temperature, a scale reading, or a lot closing, and the job updates a result while the truck is still in the yard. Yesterday arrives as a sequence of events, one window at a time. The window is measured in event time, the clock on the probe, which can differ from the minute the packet reached the job.

A tumbling window of five minutes closes, and the next five minutes start clean. A sliding window overlaps the one before it. The job keeps a watermark, the event time it is willing to treat as complete. A window can close once the watermark passes the window's end. An event whose event time is already behind that watermark is late. A grace interval can still count it. Past the grace, the job drops it or writes it aside. The log this job reads, and a delivery that can hand the same event twice, are Log or Queue and Message Delivery Guarantees in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

```text
event time   the minute on the probe
window       five minutes of event time, then an aggregate
watermark    how far event time the job treats as complete
late         event time sits behind the watermark
grace        a short allowance that still counts
```

## Batch or Stream

A batch job fits a complete set whose reader can wait. The morning settlement is that case. Every ticket from yesterday belongs in the total, and the sheet is due at 06:00, after the day has closed.

A stream job fits a check that has to be fresh. Silo 4 crossing 40 C should ring the duty phone within seconds. A number that has to be both yesterday's closed total and the last minute's total is two results. Serving both is Lambda or Kappa. The log under the fresh path is still Log or Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

```text
closed day, the reader can wait      batch
a check that must fire in seconds    stream
the closed day and the last minute   both results, next card
```

## Lambda or Kappa

Lambda runs two paths over the same facts. The batch path reads the closed day and writes the total people will reconcile, the bushels through midnight. The speed path folds events as they arrive and serves the minutes the batch has not covered. A query adds the batch total to the speed total from after the batch cutoff. Fold yesterday into the speed total as well and those bushels count twice. The batch path can be run again to correct a bad day. The cost is two copies of "bushels by grower" that can disagree until the batch lands.

Kappa keeps the one stream path. The events sit in a log. A corrected job starts again from the retained offsets and rebuilds the totals, so there is one codebase. The rebuild sees the events the log still holds. That retention is Log or Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). Lambda fits when a trusted batch result already exists and the fresh slice is thin. Kappa fits when replaying that log is acceptable and a second implementation is the cost to skip.

```text
lambda    batch through the cutoff + speed after the cutoff
kappa     one stream job, replay the log to rebuild
overlap   speed rows already inside the batch count twice
```

## Change Data Capture

Change data capture hands each committed insert, update, and delete to another store. The default read is the database write-ahead log or binlog. The primary already wrote that log so it can recover. A tailer sees the grade change on lot 18 and the delete of a voided ticket. The scale transaction stays the commit it already was, and the tailer reads the log after that commit. Debezium is the usual name for that tailer. A timer that polls the table rereads rows that did not change, and a delete is easy to miss once the row is gone.

The reader decides the destination. The yard screen's lot card drops a stale copy: Cache Invalidation in [Caching](../05_Caching/). Variety search updates Search Index Store in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). The monthly moisture report lands in Data Warehousing in that same topic. An outbox table written in the same database transaction is Transactional Outbox in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

```text
read the log      WAL or binlog, deletes included
lot card          invalidate the cache
variety search    update the search index
month report      land the row in the warehouse
outbox table      Transactional Outbox
```

## Event Sourcing

Event sourcing stores each change as an immutable event. The current value is a fold of that sequence. Lot 18 is receive 1000, ship 40, ship 25, receive 100. The bushels still on the floor are that fold, 1035. The events are the source of truth. A table of the current fill is a copy that can be rebuilt from them.

A snapshot is the fold saved at an event number. A reader starts there and applies the tail. That matches a fold from the first event and skips a scan of the whole season. The snapshot is for speed. The events still decide the value if the snapshot is thrown away. A projection is one fold shaped for a reader, the yard card or the bushels on the floor. Writes append events. Reads use the projection. That split is the CQRS cue. The broker shape that holds the events is Log or Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). A new field an old reader has to skip is Schema Evolution in [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/).

```text
events       receive 1000, ship 40, ship 25, receive 100
fold         1035 bushels still on the floor
snapshot     fold through ship 40, then apply the tail
projection   the yard card, from the same events
```
