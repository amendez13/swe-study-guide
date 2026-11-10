# Classic Design Problems

Lumen Orchard Exchange is nine products that share a packing shed: crate-card links, picker chat, the growers' board, a crawl of public trial pages, the frontier in front of that crawl, lot status in a key-value store, cold-room samples, grafting-class benches, and the morning crate call. Each card applies a building block and names the topic that owns the block. Short codes, sockets, presence, fan-out, the hash ring, quorums, fetch retries, locks, the charge, the time-series store, and the post-trade queue stay in those topics.

## Key Points

- **URL Shortener** — create returns a code, redirect returns the long URL. Lot cards answer 302 so every open is logged and a retarget is visible. The hours page answers 301. The code is Base62 or Hash. The lookup cache is Caching.
- **Chat System** — route a frame to the process that holds the socket. Store ids the phone has not applied, and catch a device up from its cursor. A crew of eight keeps a copy per member. The harvest channel stores one copy. Ids are Snowflake ID. Presence and Fan-Out Strategies stay in Real-Time and Notification Systems.
- **News Feed** — publish stores a note once. Retrieve merges a precomputed board with a grower the whole exchange follows, then sorts by score. The copy-at-write or copy-at-read rule is Fan-Out Strategies. The assembled board is Caching.
- **Web Crawler** — frontier, fetch, parse, store, and the new links go back. The host lookup is cached. A normalized URL is fetched once per cycle, through a set or a bloom filter. Matching bytes are stored once, as Object Storage. A trap or an oversized body is dropped. robots.txt is kept per host. A missed fetch is Timeouts and Retries.
- **URL Frontier** — one queue per host, and a gap after each fetch. Priority orders URLs the gap has released. Freshness is the due time. The queues are durable. The walk is breadth-first, so one host stays a slice of the crawl.
- **Distributed Key-Value Store** — get and put. Keys sit on Consistent Hashing. N is 3. Lot status uses W = 2 and R = 2. Crates packed today uses W = 1 and R = 1. The overlap rule, conflicts, the client path, and a silent copy stay in Consistency and Replication.
- **Metrics Monitoring System** — pear room pushes, and a heartbeat shows silence. The door counter is scraped, and a missed read is silence. Samples land in a Time-Series Database. A coarser series is Batch Processing. One open incident pages once.
- **Ticket Booking System** — a bench is HELD for 8 minutes, confirmed after capture, and released by the timer or a failed capture. The exclusive row is Optimistic or Pessimistic. The charge is Authorize and Capture. The dawn wagon sells 22 tickets for 20 seats.
- **Matching Engine** — lower ask, then earlier time. Nine crates at limit 12 fill four and then three, and two rest as a bid at 12. A sequencer stamp is the arrival order. One thread matches one variety. The trade then enters a Message Queue.

## Example

A lot card is counted, so its redirect is 302, and the hours page is 301. Bench 7 paid at minute 6 stays confirmed at minute 7. An unpaid bench is still held at minute 3 and free at minute 9. The morning buy of nine crates at limit 12 walks the ask book.

```python
HOLD_MIN = 8
ASKS = (
    (12, 1, 4, "a"),
    (12, 2, 3, "b"),
    (13, 0, 8, "c"),
)


def redirect(count_clicks: bool) -> int:
    if count_clicks:
        return 302
    return 301


def bench(now: int, paid_at: int | None) -> str:
    if paid_at is not None and paid_at < HOLD_MIN:
        return "confirmed"
    if now >= HOLD_MIN:
        return "available"
    return "held"


def fill(limit: int, qty: int) -> tuple[tuple[tuple[str, int], ...], int]:
    book = [list(row) for row in sorted(ASKS)]
    taken: list[tuple[str, int]] = []
    for row in book:
        price, _time, avail, name = row
        if price > limit or qty == 0:
            break
        take = min(avail, qty)
        taken.append((name, take))
        row[2] = avail - take
        qty -= take
    return tuple(taken), qty


print(
    redirect(True),
    redirect(False),
    bench(7, 6),
    bench(3, None),
    bench(9, None),
    fill(12, 9),
)
# 302 301 confirmed held available ((('a', 4), ('b', 3)), 2)
```

The 302 is the lot card and the 301 is the hours page. The paid bench stays taken. The unpaid bench returns at the timer. The buy takes the earlier ask at 12 before the later one, leaves two crates as a resting bid, and leaves the ask at 13 untouched. The code on the card, the lock on the bench, and the queue after the fill stay in the topics named above.

## See also

- [Caching](../05_Caching/) — the shared tier. The redirect lookup and the assembled board sit there. Eviction and a hot key stay there.
- [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/) — Time-Series Database. The sample store stays there. Push, scrape, and the open incident stay here.
- [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/) — Consistent Hashing. Where a lot key sits stays there.
- [Consistency and Replication](../09_Consistency_and_Replication/) — Quorum Reads and Writes, Conflict Resolution, Read and Write Path, and Replica Failure Handling. The overlap rule and a silent copy stay there. The W and R this store picks stay here.
- [Networking and Communication](../10_Networking_and_Communication/) — WebSockets and SSE. The socket stays there. Routing a frame to the process that holds it stays here.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Message Queue. Settlement after a fill stays there. The match stays here.
- [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/) — Service Discovery. Which chat process is registered stays there.
- [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/) — Object Storage and Batch Processing. The crawled blob, and the job that builds a coarser series, stay there.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Timeouts and Retries. A fetch that hits its deadline stays there.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — Optimistic or Pessimistic, and Distributed Locks. The exclusive update on a bench stays there. The 8-minute hold stays here.
- [Unique ID Generation](../19_Unique_ID_Generation/) — Base62 or Hash, and Snowflake ID. The short code and the message id stay there. The redirect and the catch-up stay here.
- [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/) — Presence and Fan-Out Strategies. Who is online, and copy-at-write versus copy-at-read, stay there.
- [Payment and Financial Systems](../23_Payment_and_Financial_Systems/) — Authorize and Capture. The charge that confirms a bench stays there. The hold and the timer stay here.
