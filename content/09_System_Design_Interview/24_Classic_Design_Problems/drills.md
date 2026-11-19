# Classic Design Problems — Drills

Original practice for assembling a product from blocks that live in the neighboring topics. Each card is one exercise: commit to an answer, then check it. The numbers are invented for familiar products: a short link, a chat with two devices, a home feed, a polite crawler, a key-value store, metrics collection, a reserved seat, and a price-time order book. The short code, the socket, presence, fan-out, the hash ring, quorums, a fetch deadline, the lock, the charge, the sample store, the crawled blob, the roll-up job, and the queue after a fill stay in the topics named in each answer.

## Redirect Code

The `promo` link must log every open, and the owner sometimes points that code at a new page. The `about` page never changes, and nobody counts it. Which status does each link answer with? The characters in the code are a separate choice.

```python
LINKS = {"promo": True, "about": False}
```

**Answer:** `promo` answers 302. Every open asks the shortener, the click log moves, and a new target is the page the next open receives. `about` answers 301. The browser may keep that target, and later opens never reach the log. The alphabet and a colliding hash prefix are Base62 or Hash in [Unique ID Generation](../19_Unique_ID_Generation/). The shared lookup the redirect reads is [Caching](../05_Caching/).

```python
LINKS = {"promo": True, "about": False}


def status(count_clicks: bool) -> int:
    if count_clicks:
        return 302
    return 301


print(status(LINKS["promo"]), status(LINKS["about"]))
# 302 301
```

![Redirect Code](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills-1-redirect-code.png)

*Source: [`diagrams/classic-problems-drills.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills.drawio), page 1.*

## Chat Offline

Alex sends "gate changed" to Riley. Riley's socket is down. The stored message ids are 41 and 42. Riley's phone last applied 40, and the tablet last applied 42. What does the service do while Riley is offline, what does the phone receive on reconnect, and what does the tablet receive?

```python
STORED = (41, 42)
PHONE = 40
TABLET = 42
ONLINE = False
```

**Answer:** The message is stored under Riley. No frame is written to a socket while `ONLINE` is false. On reconnect the phone sends cursor 40 and receives 41 and 42. The tablet sends cursor 42 and receives nothing further. A second delivery of 41 to the phone is dropped once that id is already applied. Whether Riley counts as online is Presence in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/). The socket is WebSockets and SSE in [Networking and Communication](../10_Networking_and_Communication/). The ids are Snowflake ID in [Unique ID Generation](../19_Unique_ID_Generation/). The map from Riley to the process that holds the socket is the routing table on the chat card. How that process registers its address is Service Discovery in [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/).

```python
STORED = (41, 42)
PHONE = 40
TABLET = 42
ONLINE = False


def catch_up(stored: tuple[int, ...], cursor: int) -> tuple[int, ...]:
    return tuple(message_id for message_id in stored if message_id > cursor)


sent_now = () if not ONLINE else catch_up(STORED, PHONE)
print(sent_now, catch_up(STORED, PHONE), catch_up(STORED, TABLET))
# () (41, 42) ()
```

![Chat Offline](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills-2-chat-offline.png)

*Source: [`diagrams/classic-problems-drills.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills.drawio), page 2.*

## Feed Assembly

Lee is an ordinary account. Lee's post is already in the reader's precomputed inbox. Sky is followed by millions of people. Sky's post was stored once and was not copied into that inbox. The reader's scores are Lee 3 and Sky 9. What does the open call return, and in what order?

```python
INBOX = ("lee",)
PULL = ("sky",)
SCORE = {"lee": 3, "sky": 9}
```

**Answer:** The open call starts with the precomputed inbox, pulls Sky because that post is not in it, and sorts by score. Sky leads, then Lee. The choice to copy Lee at publish and pull Sky at read is Fan-Out Strategies in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/). This exercise is the merge and the score. The assembled page can sit in [Caching](../05_Caching/) until a new precomputed post arrives.

```python
INBOX = ("lee",)
PULL = ("sky",)
SCORE = {"lee": 3, "sky": 9}


def board(inbox: tuple[str, ...], pull: tuple[str, ...]) -> tuple[str, ...]:
    rows = inbox + pull
    return tuple(sorted(rows, key=lambda name: -SCORE[name]))


print(board(INBOX, PULL))
# ('sky', 'lee')
```

![Feed Assembly](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills-3-feed-assembly.png)

*Source: [`diagrams/classic-problems-drills.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills.drawio), page 3.*

## Politeness

`trial.example` publishes a crawl-delay of 2 seconds, and the frontier fetched it 1 second ago. `notes.example` has no crawl-delay, so the crawler uses a 1-second gap, and that host was fetched 5 seconds ago. Both URLs are due. `trial.example/rust` is the priority recrawl. Which URL may leave now, and how long does the other host still wait?

```python
HOSTS = {
    "trial.example": {"gap": 2, "elapsed": 1},
    "notes.example": {"gap": 1, "elapsed": 5},
}
DUE = (("trial.example", "rust", 1), ("notes.example", "leaf", 2))
```

**Answer:** `notes.example/leaf` may leave. `trial.example/rust` waits 1 more second. Priority orders URLs the gap has released, and the priority recrawl is still inside its crawl-delay. A path `robots.txt` disallows never reaches this choice. The queues and the due time are the URL Frontier card. A fetch that then hits its deadline is Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). Googlebot does not honor a crawl-delay line. A crawler that does treats that line as the host's gap, which is the rule this exercise uses.

```python
HOSTS = {
    "trial.example": {"gap": 2, "elapsed": 1},
    "notes.example": {"gap": 1, "elapsed": 5},
}
DUE = (("trial.example", "rust", 1), ("notes.example", "leaf", 2))


def wait(host: str) -> int:
    row = HOSTS[host]
    return max(0, row["gap"] - row["elapsed"])


def next_url() -> str:
    allowed = [item for item in DUE if wait(item[0]) == 0]
    allowed.sort(key=lambda item: item[2])
    host, path, _priority = allowed[0]
    return f"{host}/{path}"


print(next_url(), wait("trial.example"))
# notes.example/leaf 1
```

![Politeness](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills-4-politeness.png)

*Source: [`diagrams/classic-problems-drills.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills.drawio), page 4.*

## KV Knobs

Order status has to return the put that was acknowledged. The page-view counter may be stale. N is 3. Which W and R does each key use, and which topic owns the rule that makes the order-status pair valid?

```python
N = 3
MUST_SEE_ACK = {"order-status": True, "page-views": False}
```

**Answer:** Order status uses W = 2 and R = 2. Page views use W = 1 and R = 1. The reason the first pair shares a copy with every acknowledged write is Quorum Reads and Writes in [Consistency and Replication](../09_Consistency_and_Replication/). That card owns the overlap rule. Where the key sits is Consistent Hashing in [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/). A copy that stops answering is Replica Failure Handling in Consistency and Replication. A deadline on the way to a copy is Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). This exercise records the pair the product picked.

```python
N = 3
MUST_SEE_ACK = {"order-status": True, "page-views": False}


def knobs(must_see_ack: bool) -> tuple[int, int]:
    if must_see_ack:
        return (2, 2)
    return (1, 1)


print(
    N,
    knobs(MUST_SEE_ACK["order-status"]),
    knobs(MUST_SEE_ACK["page-views"]),
)
# 3 (2, 2) (1, 1)
```

![KV Knobs](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills-5-kv-knobs.png)

*Source: [`diagrams/classic-problems-drills.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills.drawio), page 5.*

## Push or Scrape

A batch job sits behind a firewall. The collector cannot dial it. An API server exposes a `/metrics` page the collector can dial, and a silent server has to show up as a missed read. Which collection mode does each one use, and where do the samples land?

```python
SOURCES = {
    "batch-job": {"dialable": False},
    "api-server": {"dialable": True},
}
```

**Answer:** The batch job pushes. The API server is scraped, so a missed read is the silence signal. The batch job adds a heartbeat, because a push with nothing new and a push that has stopped are the same until that heartbeat is late. The samples append to a Time-Series Database in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). A one-hour series built from a closed day is Batch Processing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). The page for an error ratio that stays above 1% is one open incident, so the next evaluation in that stretch stays quiet.

```python
SOURCES = {
    "batch-job": {"dialable": False},
    "api-server": {"dialable": True},
}


def mode(dialable: bool) -> str:
    if dialable:
        return "scrape"
    return "push"


print(mode(SOURCES["batch-job"]["dialable"]), mode(SOURCES["api-server"]["dialable"]))
# push scrape
```

![Push or Scrape](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills-6-push-or-scrape.png)

*Source: [`diagrams/classic-problems-drills.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills.drawio), page 6.*

## Seat Hold

Seat 7 is `HELD` at minute 0 for 8 minutes. The buyer's capture succeeds at minute 6. Another buyer taps Reserve on that seat at minute 7. Seat 12 was held at minute 0 and never captured. The sweeper runs at minute 3 and again at minute 9. What is seat 7 at minute 7, may the second buyer hold it, and what is seat 12 at each sweeper run?

```python
HOLD_MIN = 8
SEAT_7_PAID = 6
SWEEPS = (3, 9)
```

**Answer:** At minute 7 seat 7 is confirmed, and the second tap finds it taken. Capture at minute 6 is inside the 8 minutes, so the hold has become a confirmation. Seat 12 is still held at minute 3. At minute 9 the sweeper releases it to available. The row lock or the version check is Optimistic or Pessimistic in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). A lease outside one database is Distributed Locks in that topic. The capture itself is Authorize and Capture in [Payment and Financial Systems](../23_Payment_and_Financial_Systems/). The shuttle's 22 tickets for 20 seats are a different inventory. This seat has no spare.

```python
HOLD_MIN = 8
SEAT_7_PAID = 6
SWEEPS = (3, 9)


def seat(now: int, paid_at: int | None) -> str:
    if paid_at is not None and paid_at < HOLD_MIN:
        return "confirmed"
    if now >= HOLD_MIN:
        return "available"
    return "held"


def can_hold(state: str) -> bool:
    return state == "available"


print(
    seat(7, SEAT_7_PAID),
    can_hold(seat(7, SEAT_7_PAID)),
    tuple(seat(now, None) for now in SWEEPS),
)
# confirmed False ('held', 'available')
```

![Seat Hold](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills-7-seat-hold.png)

*Source: [`diagrams/classic-problems-drills.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills.drawio), page 7.*

## Price-Time Fill

The ask book for one symbol is four shares at 12 with time 1, three shares at 12 with time 2, and eight shares at 13 with time 0. A buy of nine shares arrives with limit 12, after the sequencer stamp. What fills, what rests on the bid book, and what stays on the ask book?

```python
ASKS = (
    (12, 1, 4, "a"),
    (12, 2, 3, "b"),
    (13, 0, 8, "c"),
)
BUY = (12, 9)
```

**Answer:** The buy fills four shares from the earlier ask at 12, then three from the later ask at 12. Two shares rest as a bid at 12. The eight shares at 13 stay on the ask book, because 13 is above the limit. Price leads time, so that ask stays put even though its time is 0. The sequencer stamp is the arrival time the book sorts on, and this buy is one stamp behind the asks it walks. One thread owns this symbol, with the book in memory. Settlement reads the trade from a Message Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) after the fill returns.

```python
ASKS = (
    (12, 1, 4, "a"),
    (12, 2, 3, "b"),
    (13, 0, 8, "c"),
)
BUY = (12, 9)


def fill(limit: int, qty: int) -> tuple[tuple[tuple[str, int], ...], int, tuple[tuple[str, int], ...]]:
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
    resting = tuple((row[3], row[2]) for row in book if row[2] > 0)
    return tuple(taken), qty, resting


print(fill(*BUY))
# ((('a', 4), ('b', 3)), 2, (('c', 8),))
```

![Price-Time Fill](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills-8-price-time-fill.png)

*Source: [`diagrams/classic-problems-drills.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-drills.drawio), page 8.*
