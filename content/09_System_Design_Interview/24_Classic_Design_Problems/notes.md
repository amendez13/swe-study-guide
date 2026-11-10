# Classic Design Problems

Nine products, each one a place where the neighboring topics meet. A bit.ly-style short link, a WhatsApp-style chat, a Twitter or Facebook home feed, a Googlebot-style crawl and the frontier in front of it, a Dynamo-style key-value store, Prometheus-style metrics, a Ticketmaster-style seat hold, and a stock-exchange order book. The card walks the product. The alphabet, the socket, presence, fan-out, the hash ring, quorums, retries, locks, the charge, the time-series store, and the queue after a fill stay in the topics that own them.

## Key Points

- **URL Shortener** — create returns a code, redirect returns the long URL. A counted link that may be retargeted answers 302, so every open hits the service. A stable page that is not counted answers 301, and the browser may skip later opens. The redirect is cache, then row. The click is appended after the status. A base-62 counter is unique at 6 characters for this volume. A hash prefix collides early and needs a lookup.
- **Chat System** — the socket stays on the process that accepted it, and a route map forwards the frame. Messages sit under the recipient, ordered by snowflake id. A device catches up from its cursor. One recipient gets one write. A group of eight gets a copy per member. A channel of hundreds stores the message once.
- **News Feed** — publish stores a post once. An ordinary account is copied into follower inboxes. An account past the cutoff, 5,000 followers in this design, is pulled when the feed is opened and merged. The page sorts by score. The assembled page can be cached until a new precomputed post arrives.
- **Web Crawler** — frontier, fetch, parse, store, and the links that pass go back. DNS is cached. A normalized URL hash is remembered with a set or a bloom filter. Identical bytes are stored once. A trap or an oversized body is dropped. `robots.txt` is kept per host. A missed deadline retries with a growing wait.
- **URL Frontier** — one queue per host, and a gap after each fetch. Priority orders only URLs the gap has released. Freshness is a due time. The queues are durable. The walk is breadth-first, so one host stays a slice of the crawl.
- **Distributed Key-Value Store** — `get` and `put`. Keys sit on a consistent-hash ring with N = 3. Order status uses W = 2 and R = 2, so the read overlaps the acknowledged write. Page views use W = 1 and R = 1 and may be stale. Conflicts, the coordinator, and a silent replica stay in Consistency and Replication.
- **Metrics Monitoring System** — scrape a dialable `/metrics` page. A missed scrape is silence. A job the collector cannot dial pushes, and a heartbeat makes a dead push visible. Samples land in a time-series store. Coarser series are a batch job. One open incident pages once.
- **Ticket Booking System** — a seat is `HELD` for 8 minutes, confirmed after capture, and released by the timer or a failed capture. The row updates only while it is still available. A shuttle may sell 22 tickets for 20 seats. A numbered seat has no spare.
- **Matching Engine** — lower ask, then earlier time. Nine shares at limit 12 fill four and then three, and two rest as a bid at 12. The ask at 13 stays. A sequencer stamp is the arrival order. One thread matches one symbol. The trade then enters a queue.

## Example

A counted short link uses 302, and a stable page uses 301. Seat 7 paid at minute 6 is still confirmed at minute 7. An unpaid seat is still held at minute 3 and free at minute 9. A buy of nine shares at limit 12 walks the ask book.

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


def seat(now: int, paid_at: int | None) -> str:
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
    seat(7, 6),
    seat(3, None),
    seat(9, None),
    fill(12, 9),
)
# 302 301 confirmed held available ((('a', 4), ('b', 3)), 2)
```

The 302 is the counted link and the 301 is the stable page. The paid seat stays taken. The unpaid seat returns when the hold expires. The buy takes the earlier ask at 12 before the later one, leaves two shares as a resting bid, and leaves the ask at 13 on the book. The code alphabet, the lock on the seat, and the queue after the fill stay in the topics named below.

## Which knob the product turns

| Product | The choice on this card | Where the mechanism lives |
| --- | --- | --- |
| Short link | 302 when clicks or retargets matter, 301 when the target is stable | Unique ID Generation, Caching |
| Chat | Cursor per device; copy a group of 8; store a large channel once | Networking, Real-Time, Unique ID Generation |
| Home feed | Copy ordinary posts at publish; pull a huge account at read | Real-Time, Caching |
| Crawler | Politeness, robots, URL hash, content hash | Object Storage, Timeouts and Retries, URL Frontier |
| Key-value | W = 2, R = 2 for order status; W = 1, R = 1 for a counter | Consistent Hashing, Consistency and Replication |
| Metrics | Scrape if dialable; push plus a heartbeat otherwise | Time-Series Database, Batch Processing |
| Reserved seat | Hold 8 minutes; confirm only after capture | Transactions, Payments |
| Order book | Price then time; one thread per symbol; queue after the fill | Message Queues |

## See also

- [Caching](../05_Caching/) — the shared tier for the redirect lookup and the assembled feed. Eviction and a hot key stay there.
- [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/) — the time-series store for samples. Push, scrape, and the open incident stay here.
- [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/) — where a key sits on the ring.
- [Consistency and Replication](../09_Consistency_and_Replication/) — quorum overlap, conflict resolution, the coordinator, and a silent replica. The W and R this store picks stay here.
- [Networking and Communication](../10_Networking_and_Communication/) — WebSockets and SSE. Routing a frame to the process that holds the socket stays here.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — the queue settlement reads after a fill. The match stays here.
- [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/) — service discovery for the chat process that registered its address.
- [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/) — object storage for a crawled body, and the batch job that builds a coarser metrics series.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — a fetch or a replica call that hits its deadline.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — the conditional update on a seat, and a lease when the hold lives outside that database. The 8-minute timer stays here.
- [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/) — a create limit on the shortener so one client cannot mint the code space.
- [Unique ID Generation](../19_Unique_ID_Generation/) — base 62 or a hash prefix for the short code, and snowflake ids for chat messages.
- [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/) — presence, and copy-at-write versus copy-at-read. The chat screen and the feed page stay here.
- [Payment and Financial Systems](../23_Payment_and_Financial_Systems/) — authorize and capture. The hold and the timer stay here.
