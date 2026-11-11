## URL Shortener

A URL shortener turns a long URL into a short code and sends the browser to the long URL when that code is opened. The product shape is bit.ly: one call creates the code, and one call redirects. Redirects dominate creates. A create can take tens of milliseconds, and a redirect should finish in a few milliseconds after the cache hop. Codes stay valid for years unless the owner sets an expiry.

Assume 50 million new links a month, 80 redirects per new link, a 4× peak, 500 bytes per row and 3 years of retention. Creates average about 20 a second and peak near 80. Redirects average about 1,600 a second and peak near 6,400. Three years is 1.8 billion rows, about 1 TB. That is one database plus a cache in front of the read path. The fleet exists so the redirect stays up, not because 6,400 reads a second need hundreds of machines.

`POST /links` stores the code, the long URL, the owner and the created time, with an optional expiry and disabled flag on the same row. `GET /{code}` reads a shared cache, falls back to the row and fills the cache, then chooses the status. The click, with code, time and referrer, is appended after that choice, so a lost click is only an analytics gap. The code is a counter in base 62 or a hash prefix. Six characters cover 62^6, about 57 billion codes, so a counter needs 6 characters for 1.8 billion links and never collides. A random 7-character prefix, about 3.5 trillion slots, reaches a 50% chance of some unchecked collision at a bit over 2 million codes. So the hash path looks up each candidate and salts again on a hit. At 1.8 billion links that space is about 0.05% full, so a retry almost always lands free. The alphabet and retry are Base62 or Hash in [Unique ID Generation](../19_Unique_ID_Generation/). The cache and a stampede on one hot code are [Caching](../05_Caching/), and the create limit is [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/).

The status is the main trade-off. A 302 says the mapping is temporary, so the browser asks again on the next open, every click is logged, and a retarget takes effect. A 301 lets the browser store the mapping, so later opens skip the log and a retarget. Counted campaign links use 302. An uncounted stable page can use 301. A 307 also preserves the method, and short links are GETs, so 302 is the answer here.

```text
create      POST /links -> code         ~20/s, peak ~80
redirect    GET /{code} -> cache, row   ~1,600/s, peak ~6,400
storage     1.8B rows x 500 B ~ 1 TB
code        base62 counter (6 chars) or hash prefix + collision check
status      302 counts and can retarget, 301 lets the browser skip
```

![URL Shortener](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-1-url-shortener.png)

*Source: [`diagrams/classic-problems.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems.drawio), page 1.*

## Chat System

A chat system delivers a message to a person, a small group or a large channel, including devices that were offline when it was sent. The product shape is WhatsApp: a phone holds a live connection, a second device has its own place in the history, and a message waits when nobody is connected. The server that accepted one phone's connection is not the one that holds the recipient's, and a retry from a flaky network must not insert the message twice.

Assume 15 million daily users, 30 messages each, a 4× evening peak and 8% connected at peak. Sends average about 5,200 a second and peak near 21,000. The peak is 1.2 million open sockets, about 150 servers at 8,000 sockets each. One stored copy at 250 bytes is 450 million messages, about 110 GB a day and 41 TB a year.

A signed-in phone opens a connection that stays on the process that accepted it, which is WebSockets and SSE in [Networking and Communication](../10_Networking_and_Communication/). The chat tier keeps a map from user to that process, and a message looks up the recipient's process and forwards the frame. Finding that process's address is Service Discovery in [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/). The message is stored under the recipient, ordered by a Snowflake ID from [Unique ID Generation](../19_Unique_ID_Generation/). Each device remembers the last id it applied and, on reconnect, receives the ids after it. A phone at cursor 40, with 41 and 42 stored, receives 41 then 42. A tablet already at 42 receives nothing, and a retried frame whose id is applied is dropped. Whether the recipient is online is Presence in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/), and it picks the live socket or the mailbox.

A one-to-one message has one recipient. A group of about 8 keeps a copy in each member's history, so opening it is one read. A channel of hundreds stores the message once, and each phone reads from its cursor, because most members are offline and would not read a send-time copy. That rule is Fan-Out Strategies in the same topic. Without a routing table, a server can reach a user only by publishing on a bus all 150 servers hear. A "last 50 messages" pull is simpler than a cursor and can duplicate or skip when two devices disagree.

```text
peak         ~21,000 sends/s, 1.2M sockets, ~150 servers
route        user -> process map, socket pinned to its process
store        under the recipient, ordered by snowflake id
catch up     ids after the device cursor, applied ids dropped
copy rule    1:1 one recipient, group of 8 a copy each, channel stored once
```

![Chat System](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-2-chat-system.png)

*Source: [`diagrams/classic-problems.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems.drawio), page 2.*

## News Feed

A news feed shows a person the posts published by accounts they follow. Publish and retrieve are different calls. The product shape is a Twitter or Facebook home feed: one post is written once, and opening the app returns a ranked page. Most accounts have a modest audience, and a few have millions. Copying every post to every follower at publish melts on those few accounts. Building every page at read melts on the open rate.

Assume 40 million daily users, 8 opens each, a 3× peak, and 5% publishing once. Opens average about 3,700 a second and peak near 11,000. Posts average about 23 a second. An ordinary account has 150 followers, so copying at publish is about 3,500 inbox writes a second. One post from an account with 5 million followers would be 5 million writes, about 24 minutes of that ordinary fan-out.

Publish stores the post once with its author and time. For an author under the cutoff, a worker appends a reference into each follower's precomputed inbox. This design puts the cutoff at 5,000 followers. One post at that size is about 5,000 inbox writes, roughly a second and a half of ordinary fan-out, and anything larger is refused on the write path. Retrieve loads the reader's inbox, pulls posts from the huge accounts they follow, and merges. Storage order is time, and page order is a score applied at assembly, so an ordinary post scored 3 and a celebrity post scored 9 come back celebrity first. The assembled page can be cached under the reader until a new precomputed post drops it. Eviction and a stampede are [Caching](../05_Caching/), and the copy rule is Fan-Out Strategies in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/).

Copy-on-write makes the open a single inbox read and a celebrity post a write storm. Copy-on-read makes publish one insert and every open a scan of the follow list. The hybrid pays the cheap writes and refuses the expensive ones. Ranking at read can leave a new post under a cached page until the entry drops, and ranking at write freezes the score before later signals exist. A purely chronological feed is the right product only when the promise is "latest."

```text
opens        ~3,700/s, peak ~11,000
ordinary     150 followers, copied at publish, ~3,500 writes/s
cutoff       5,000 followers; above it, stored once and pulled at read
huge         5M followers = ~24 min of ordinary fan-out, not copied
page         merge inbox + pulled posts, sort by score, cache
```

![News Feed](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-3-news-feed.png)

*Source: [`diagrams/classic-problems.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems.drawio), page 3.*

## Web Crawler

A web crawler fetches public pages, stores their text and follows the links it is allowed to follow. The product shape is Googlebot: start from seeds, download a page, remember it, and come back when the page is due again. The web is a graph with loops, duplicates and pages that generate new links forever, and the crawler has to make progress across many hosts while obeying each host's rules.

Assume 5 million fetches a day, 80 KB of HTML each, and a default gap of one fetch per second per host. That is about 60 fetches a second, so about 60 hosts are in flight at once, and about 400 GB of HTML a day before duplicates collapse. A seen-set of 20 million URLs is 320 MB as 16-byte hashes, or about 23 MB as a bloom filter aimed at 1% false positives. A larger crawl multiplies the fetchers, and the per-host gap still caps what any one site absorbs.

Seeds enter the frontier. A fetcher takes the next released URL, resolves the host through a DNS cache, and downloads with a deadline. A parser pulls text and links. The text is stored, and links that pass the filters return to the frontier. A page that keeps inventing links, or a body past the size cap, is dropped by budget rather than by understanding the page. Dedup is two checks. A URL already taken this cycle is skipped, using a hash of its normalized form: lowercase host, no fragment, no default port, and one trailing-slash policy. A set answers exactly. A bloom filter is smaller and sometimes skips a page it has not fetched, and it never forgets an inserted URL. A body whose content hash matches bytes already kept is stored once, as Object Storage in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). A similarity hash would also collapse pages that differ only by a footer.

A host's `robots.txt` is fetched and kept before any page on that host, and a disallowed path never reaches the fetcher. A missed deadline retries with a growing wait, a spread and a cap, which is Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). Politeness gates throughput, so more fetchers help only while new hosts are available. Some crawlers read `crawl-delay` as the gap. Googlebot ignores it and applies its own per-host rate. The due time and the gap are the URL Frontier card.

```text
load         ~60 fetches/s, ~60 hosts in flight, ~400 GB/day
loop         frontier -> fetch -> parse -> store -> links back
URL dedup    normalized hash: set (320 MB) or bloom filter (~23 MB)
body dedup   content hash, stored once
rules        robots.txt per host, trap and size budgets
```

![Web Crawler](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-4-web-crawler.png)

*Source: [`diagrams/classic-problems.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems.drawio), page 4.*

## URL Frontier

The URL frontier is the list of URLs still to fetch, and it is the gate in front of the fetcher. In a Googlebot-style crawler it decides which host may be touched now, which URL on that host goes next, and where the crawl resumes after a crash. Without it, a crawler follows whatever link it just parsed. One host with a deep path can fill the crawl, and a site can be hit as fast as the fetchers can open connections.

Each host has its own queue, and after a fetch that host waits out its gap before another of its URLs may leave. The gap is the `crawl-delay` line when the crawler honors it, and the crawler's own per-host rate otherwise. Priority orders the URLs the gap has released. It does not jump the gap. A host whose gap is 2 seconds, fetched 1 second ago, still waits 1 second even for its priority recrawl, while a host with a 1-second gap fetched 5 seconds ago may leave now. Freshness is a due time: a page the site changed, or one people open often, is due sooner than a page that has sat still for a season.

The crawler card's budget of about 60 fetches a second means about 60 host queues release a URL at any moment. A waiting list of 20 million URLs at about 100 bytes each is about 2 GB, small enough to keep durable on one log per fetcher partition. The cost that matters is the checkpoint: after a crash the fetcher resumes from the last flushed offset, and URLs handed out since then are fetched again. Checkpointing often shortens that replay and adds write traffic.

The walk is breadth-first: a layer of links before one path down, so many hosts move and each host is a slice of the crawl. Depth-first can follow one path on one host to its end while other seeds wait, and the gap makes that path even slower. A single global priority queue is easy to explain and hard to make polite, because the top score can be the same host again. Strict round-robin spends budget evenly, including on pages unchanged for a year.

```text
per host     one queue, a gap after each fetch
priority     orders released URLs, never jumps the gap
freshness    due time: changed and popular pages sooner
durability   ~2 GB of URLs on logs, checkpointed offsets
walk         breadth-first, so one host stays a slice
```

![URL Frontier](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-5-url-frontier.png)

*Source: [`diagrams/classic-problems.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems.drawio), page 5.*

## Distributed Key-Value Store

A distributed key-value store offers `get(key)` and `put(key, value)` across many machines, with a chosen number of copies and a chosen number of acknowledgements. The product shape is Dynamo: the key picks a place on a ring, a write waits for W copies, and a read waits for R copies. Applications disagree about staleness. An order status has to return the put that was acknowledged, while a page-view counter can be a few seconds behind. The API is the same, and the knobs are per key.

Assume 200 million keys, 800 bytes each, N = 3, and a peak of 8,000 gets and 2,000 puts a second. One copy is 160 GB and three are 480 GB, so a handful of nodes. The bytes would fit one large machine. The copies exist so one node can be down while a W = 2 write still completes, and so a read can be required to overlap that write.

The key lands on a ring, so it has a predictable node and a new node takes a share of the keys. That is Consistent Hashing in [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/). The client talks to a coordinator. On a put it sends the value to the N copies and acknowledges after W accept. On a get it asks R copies, returns the newest answer, and can write that value back onto an older copy, which is read repair. The path is Read and Write Path in [Consistency and Replication](../09_Consistency_and_Replication/). Order status uses W = 2 and R = 2. With N = 3, any two copies overlap any other two, which is W + R > N, Quorum Reads and Writes in that topic. The page-view counter uses W = 1 and R = 1, and a read can miss the latest write. Two puts that never saw each other are resolved by last-write-wins or kept for an application merge, which is Conflict Resolution there. A silent copy is Replica Failure Handling there, and its deadline is Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/).

W = 3 and R = 1 lets a read ask any one copy and stalls the write on one silent replica. W = 2 and R = 2 tolerates one silent replica and keeps the overlap. A sloppy quorum counts a stand-in when a preferred replica is down. That is hinted handoff. It keeps the write available and breaks the overlap until the hint is delivered, so do not describe it as a strict quorum.

```text
order status   N=3 W=2 R=2   W+R>N, a read overlaps every acked write
page views     N=3 W=1 R=1   a read can miss the latest write
placement      consistent hashing; coordinator waits for W, reads R
repair         read repair; LWW or merge for concurrent puts
silent copy    deadline, then hinted handoff or a failed strict write
```

![Distributed Key-Value Store](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-6-distributed-key-value-store.png)

*Source: [`diagrams/classic-problems.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems.drawio), page 6.*

## Metrics Monitoring System

A metrics system collects numeric samples over time, stores them so a range query is cheap, and pages a person when a rule stays true. The product shape is Prometheus: scrape a `/metrics` page on an interval when the collector can dial the target, and accept a push when it cannot. A dead target has to look different from a healthy, quiet one, and old samples have to get cheaper or the disk fills with one-second data nobody graphs.

Assume 2,000 servers, 80 series each, a scrape every 15 seconds and about 16 bytes per sample on the wire. That is about 11,000 samples a second and about 15 GB a day uncompressed. A time-series layout often compresses to a byte or two per sample, so plan disk from a measurement and keep 15 GB as the ceiling.

A long-lived API server can be dialed, so it is scraped, and a missed scrape is recorded as `up = 0`. A batch job behind a firewall pushes instead. On that path a heartbeat makes silence visible, because a job with nothing new and a stopped job look the same until the heartbeat is late. The Prometheus Pushgateway keeps the last pushed value until something deletes it, so a stuck push looks healthy without a heartbeat or expiry. A sample is a name, a time, a value and labels, stored in a Time-Series Database from [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). This design keeps raw samples a day, a one-minute series a month and a one-hour series after that. Stock Prometheus keeps one resolution, so the coarser series come from a compactor over a closed day or a recording rule. That job is Batch Processing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). Rollups make year-long queries cheap and hide spikes shorter than the bucket.

The page fires when the API error ratio stays above 1% for 10 minutes, evaluated every minute. One open incident for that service and rule keeps later evaluations quiet. The page repeats after the incident resolves or after the rule's repeat interval. Paging on every true evaluation would wake someone once a minute for the same incident.

```text
load        2,000 servers x 80 series / 15 s ~ 11,000 samples/s, ~15 GB/day raw
collect     scrape what you can dial (up = 0 on a miss), push + heartbeat otherwise
retain      raw 1 day, 1-minute 1 month, 1-hour after
alert       error ratio > 1% for 10 min, checked every minute
incident    one open page, repeat on resolve or the interval
```

![Metrics Monitoring System](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-7-metrics-monitoring-system.png)

*Source: [`diagrams/classic-problems.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems.drawio), page 7.*

## Ticket Booking System

A ticket system lets one person reserve one specific seat, hold it while they pay, and release it if they do not. The product shape is Ticketmaster: the seat is named, two buyers cannot both end the night with it, and the hold lasts a few minutes. Charging a card that never gets a seat, or confirming a seat that was never charged, is the failure the design avoids.

The worked inventory is 40 seats, which is a small room, not a storage problem. The load is the onsale: 5,000 taps in the same second, almost all of them losing. Each tap is one conditional update on one seat row, and the database serializes the winners. Scale the web tier for the 5,000 arrivals, and keep the seat update on one row in one database until inventory is partitioned by event.

A seat is `AVAILABLE`, `HELD` for one buyer, or `CONFIRMED`. The tap runs an update that sets the seat to `HELD` for this buyer, with `held_until` 8 minutes out, only where the status is still `AVAILABLE`. Zero rows updated means another buyer won. The same buyer retrying sees their own hold. A pessimistic path locks the row first and makes the same change. Both are Optimistic or Pessimistic in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). A lease held outside the database is Distributed Locks in that topic, with an 8-minute TTL, and the row still has to move to `HELD` in the same decision. Otherwise a crash between the two writes leaves them disagreeing. A capture inside the 8 minutes confirms the seat, using Authorize and Capture in [Payment and Financial Systems](../23_Payment_and_Financial_Systems/). A failed capture, or a sweeper finding `held_until` passed, returns the seat to `AVAILABLE` and releases any authorization. A lock held for all 8 minutes would pin a database connection to a buyer who may have walked away.

The 40 seats stop at 40 confirmed holders. A shuttle with 20 seats is different inventory. It sells 22 tickets because about two riders miss the departure, and the latest extra ticket moves to the next shuttle at the gate. Overbooking is a policy for fungible seats with a predictable no-show rate, and a bug for a numbered seat.

```text
states      AVAILABLE -> HELD (8 min) -> CONFIRMED, timer back to AVAILABLE
win         UPDATE ... SET HELD WHERE status = AVAILABLE; 0 rows = lost
load        40 seats, 5,000 taps in one second
confirm     only after capture succeeds inside the hold
overbook    a 20-seat shuttle sells 22; a numbered seat never does
```

![Ticket Booking System](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-8-ticket-booking-system.png)

*Source: [`diagrams/classic-problems.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems.drawio), page 8.*

## Matching Engine

A matching engine pairs buy and sell orders for one instrument and emits trades. The product shape is a stock exchange: an order book per symbol, price-time priority, and a fill reported before settlement finishes its own work. Two orders that arrive "at the same time" still need one of them to be first, and the match has to be fast enough that a disk write is the wrong thing to put in front of the fill.

Budget one busy symbol at 15,000 orders a second. That is a target for this design, not a claim about a particular exchange. The match is a handful of memory updates on one core: find the best price, walk the orders at that price, rest any remainder. A second symbol is a second core. Asks sort by price ascending, then time ascending. Bids sort by price descending, then time ascending. A buy crosses when its limit is at least the best ask, fills at the resting ask's price, and rests whatever it cannot take on the bid book at its limit.

One book has four shares asking 12 at time 1, three asking 12 at time 2, and eight asking 13 at time 0. Price leads time, so 13 sorts after both asks at 12 even though time 0 is earlier. A buy of nine at limit 12 takes four, then three, both at 12. The remaining two rest as a bid at 12, and the eight at 13 stay. Every order takes a sequencer stamp before it reaches a book, and that one increasing number is the arrival time. One thread per symbol, with the book in memory, keeps the book consistent without locks. Splitting a symbol across threads would need a partitioned book that still has one total order. Pro-rata matching, which splits a fill by size, is a different venue rule from Nasdaq-style price-time.

The fill returns before anything is written to disk. The trade then goes on a queue that settlement, the seller's statement and the buyer's receipt read at their own pace, which is Message Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). A crash between the fill and the queue write can drop a trade the client already saw. A replicated log write before the acknowledgement closes that gap and puts the log's latency on the match. Say which one you picked.

```text
ask a   12  t1  4   fills 4
ask b   12  t2  3   fills 3
ask c   13  t0  8   stays, above the limit 12
bid     12  t*  2   the remainder of the buy of 9 rests
order   sequencer stamp, one thread per symbol, fill then queue
```

![Matching Engine](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems-9-matching-engine.png)

*Source: [`diagrams/classic-problems.drawio`](/content/09_System_Design_Interview/24_Classic_Design_Problems/diagrams/classic-problems.drawio), page 9.*
