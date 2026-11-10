# Message Queues and Async Processing

A queue lets a producer finish without waiting for the consumer, and it keeps the message if the consumer is down. The choice that matters in an interview is which steps stay on the request, who receives each message, what a retry is allowed to do twice, and how a crash between a database row and a publish gets repaired.

## Key Points

- **Message queue** — a durable buffer. The broker writes the message, then acks the producer. Decoupling, load leveling, fault isolation, and slow work off the request path are the four jobs.
- **When to queue** — queue a step whose result the caller can learn later. A step the response needs stays on the request. Hiding that step behind the broker keeps the wait and adds the broker.
- **Point-to-point or pub/sub** — one consumer does a job, or every subscriber gets a copy. Consumer groups let one log do both. Feed fan-out and event-driven service design stay in their own topics.
- **Message delivery guarantees** — at-most-once can lose a message. At-least-once retries, and a lost ack duplicates the work. The practical default is at-least-once plus an idempotent consumer. Visibility timeouts and offsets are how the retry happens.
- **Consumer groups** — members of one group split the partitions, and every group still sees the log.
- **Ordering and partitions** — order follows the key onto one partition. There is no global order unless the log has one partition, and then one member of the group does the work. Extra members past the partition count sit idle.
- **Log or queue** — a queue deletes on ack. A log keeps the record and a consumer keeps an offset, so a later reader can replay.
- **Backpressure** — buffer a spike, drop only what can be lost, throttle the producer, or scale consumers up to the partition count. Lag and depth are metrics to page on.
- **Dead letter queue** — after N failures the message leaves the main queue, and later messages keep moving. The wait between tries stays in failure modes.
- **Transactional outbox** — the business row and the outbox row commit in one local transaction. A publisher sends unpublished rows after the fact. That is one database plus a later publish.

## Example

A county land-records desk records deeds. The receipt needs a book and page number before the grantor leaves. Indexing the parcel can wait. Four partitions and six indexers are online. One scan has already failed three times, and another has failed once. The failure limit is three.

```python
def path(step: str) -> str:
    if step in {"page-number", "fee"}:
        return "sync"
    return "queue"


def working(partitions: int, consumers: int) -> tuple[int, int]:
    busy = min(partitions, consumers)
    return busy, consumers - busy


def parked(tries: int, limit: int) -> str:
    if tries >= limit:
        return "dlq"
    return "main"


print(path("page-number"), path("index"), working(4, 6), parked(3, 3), parked(1, 3))
# sync queue (4, 2) dlq main
```

The page number stays on the request. The parcel index goes on the bus. Two of the six indexers sit idle because four partitions have four assignments. The scan that has failed three times is on the dead letter queue, and the scan that has failed once is still on the main queue, so later filings keep moving. Scans for one parcel share a key, so that parcel's index stays in order, and a different parcel can be on another partition. The assessor and the public search are a second consumer group on the same log, so each sees every recorded deed. A Monday spike buffers on the log. A week that never slows down is backpressure: scale the indexers, or slow the recording desk, and chart the lag in Observability. The deed row and the outbox row commit together, and a crash before publish leaves the outbox row for the publisher to send.

## See also

- [Networking and Communication](../10_Networking_and_Communication/) — Idempotency. The HTTP key that makes a retried POST one write. A consumer applies the same idea to a message id.
- [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/) — Event-Driven Architecture and the Saga Pattern. This topic is the bus those events travel on.
- [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/) — Stream Processing, Change Data Capture, and Event Sourcing. They read a log. The log-or-queue choice stays here.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Unreliable Networks. Timeouts and backoff between retries.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — Two-Phase Commit. The outbox is one local commit plus a later publish.
- [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/) — the Rate Limiter. Backpressure may slow a producer and does not define the bucket.
- [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/) — Fan-Out Strategies and Delivery Guarantees for Notifications.
- [Observability](../25_Observability/) — lag, queue depth, and dead-letter depth as metrics. Name the signal here and chart it there.
