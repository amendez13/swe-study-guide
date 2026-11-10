## URL Shortener

Lumen Orchard Exchange prints a short link on each crate card. The create call takes the long lot URL and returns a code. The redirect call takes the code and answers with the long URL. The alphabet, the counter, and a hash prefix that can collide are Base62 or Hash in [Unique ID Generation](../19_Unique_ID_Generation/). This card is the product around that code: the two calls, the row, the cache, and the click log.

A card printed in the morning is opened all week, so the redirect path is almost all reads. The redirect reads the code from a shared cache and, on a miss, reads the row and fills the cache. Where that tier sits, how an entry is evicted, and a stampede on one hot code are [Caching](../05_Caching/). The row holds the code, the long URL, the grower, and the time the card was printed. Each open appends a click, with the code, the time, and the referrer, after the redirect is chosen, so the buyer waits on the lookup and the status.

The status is the part the browser remembers. A 301 tells the browser the mapping stays. A later open can go straight to the lot page. That open adds no click, and a retargeted long URL stays behind the browser's copy. A 302 tells the browser to ask again. Every open reaches the exchange, the click log moves, and a changed lot URL is the one the next open receives. Lot cards use 302, because the desk counts opens and sometimes retargets a code. The hours page is stable, and the desk keeps no count for it, so it uses 301.

```text
POST /links     long URL in, code out
GET /{code}     long URL, plus a status
301             the browser may keep the target; later opens skip the log
302             every open asks again; the log moves
row             code, long URL, grower, printed at
click           code, time, referrer, appended after the status
code            Base62 or Hash
cache           Caching
```

## Chat System

Pickers at the exchange talk to the desk and to their crew from the rows. A signed-in phone holds a connection the server can write on. The upgrade, the frames, and the fact that the socket stays on the process that accepted it are WebSockets and SSE in [Networking and Communication](../10_Networking_and_Communication/). A note from Nia to Cal looks up the process that holds Cal's socket and forwards the frame. The exchange keeps that map, member to process. How a caller learns the current address of a service from a registry is Service Discovery in [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/).

A frame the phone has yet to apply is stored under Cal, ordered by message id. Those ids are Snowflake ID in [Unique ID Generation](../19_Unique_ID_Generation/). The phone and the shed tablet each keep the last id they applied. On reconnect, each device sends that cursor and receives the ids after it, which is how a note read on the tablet is still waiting on the phone, and how a retried frame with an id already applied is dropped. Whether Cal counts as online, and the heartbeat behind that mark, are Presence in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/). The stored ids and the catch-up are this card.

A one-to-one note has one recipient. The desk writes it to that socket or, with no socket, to that recipient's cursor. A crew of eight keeps a copy per member, so opening the crew reads one member's history. The harvest channel, opened by hundreds of pickers, stores the note once, and each phone fetches from its own cursor. The rule for copying at write time or at read time is Fan-Out Strategies in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/). The crew and the channel are the two shapes this product uses.

```text
socket          the process that accepted it
route           member → the process holding the socket
registry        Service Discovery
catch-up        ids after the device's cursor
one-to-one      one recipient
crew of eight   a copy per member
harvest channel one copy, each phone fetches from its cursor
ids             Snowflake ID
online          Presence
```

## News Feed

A grower publishes a lot note once. A member who follows that grower sees it on the board they open. Publish and retrieve are different calls. Publish stores the note. Retrieve returns the board.

An ordinary grower is copied into each follower's precomputed board at publish. A grower the whole exchange follows is stored once and pulled when a member opens the board, then merged with those precomputed rows. The pattern, and the line that chooses it, are Fan-Out Strategies in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/). This card is the board the open call returns.

Storage order is time. The board can use another order. A note for a lot that closes today can sort ahead of an older note with a lower score. The score is applied when the board is assembled. The assembled board can sit in a cache so the next open for that member skips the merge. The tier, and when the entry is dropped, are [Caching](../05_Caching/). A new note from a grower in the precomputed set is the event that refreshes that board.

```text
publish         store the note once
retrieve        the board a member opens
ordinary        copied into follower boards at publish
whole exchange  pulled at retrieve, then merged
pattern         Fan-Out Strategies
order           time in storage, score on the board
assembled board Caching
```

## Web Crawler

The exchange refreshes variety notes by fetching public cultivar-trial pages. Seeds enter the frontier. A fetcher takes the next URL the frontier releases, resolves the host through a cache of recent lookups, and downloads the page. A parser pulls the text and the links. The text is stored. Links that pass the filters return to the frontier. A page that keeps inventing new links, or a body past the size cap, is dropped, and the fetcher takes the next URL.

A URL already taken in this cycle is skipped. The check uses a normalized form, so a trailing slash and a default port stay one URL, and it stores a hash of that form. A set answers exactly. A bloom filter is the compact check, and a false positive skips a page. A body whose fingerprint matches bytes already kept is stored once, even when two trials host the same sheet. The blob under a key is Object Storage in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). A host's robots.txt is fetched and kept before any page on that host. A disallowed path stays out of the fetcher.

A trial sheet updated yesterday is due again. The due time, and the per-host gap that decides whether a due URL may leave now, are URL Frontier. A fetch that hits its deadline is tried again with a growing gap, a spread, and a cap. That wait is Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/).

```text
loop            frontier → fetch → parse → store → frontier
host lookup     a cache of recent resolutions
URL seen        normalized hash, a set or a bloom filter
trap            new links without end, or a body past the cap, dropped
same bytes      one stored body
blob            Object Storage
robots          kept per host; a disallowed path is never fetched
due and gap     URL Frontier
missed fetch    Timeouts and Retries
```

## URL Frontier

The frontier is the list of URLs still to fetch, and it is the gate in front of the fetcher. Each host has its own queue. After a fetch, that host waits out a gap before another of its URLs may leave. A crawl-delay in robots.txt is that host's gap. A higher-priority URL on a host fetched a moment ago waits out the rest of the gap. Priority orders URLs the gap has released.

The list is ordered by more than arrival. A sheet due today, because the trial updated it, outranks a cultivar page that has sat unchanged for a season. Freshness is that due time. A page members open often is due sooner. A stable page nobody opened is due later. The queues are stored durably, and the offsets are checkpointed, so a fetcher that crashes resumes the list.

How the crawl walks the graph sits beside that order. A breadth-first walk takes a layer of links before it follows one path down, so many hosts move and one host is a slice of the crawl. A depth-first walk follows one path to its end. That path can sit on one host and spend the crawl there while other seeds wait. The exchange walks breadth-first. Priority is a bias among the URLs the gate has released in that layer.

```text
per host        one queue, a gap after each fetch
crawl-delay     the gap robots.txt names for that host
priority        among URLs the gap has released
freshness       due sooner when the page changes or members open it
storage         durable queues, checkpointed offsets
breadth-first   a layer of hosts, then deeper links
depth-first     one path; one host can fill the crawl
```

## Distributed Key-Value Store

Lot status at the exchange is a key and a value. get returns the value. put replaces it. The product is those two calls, how many copies must answer, and what the caller does when a copy is silent. This card is the pair of knobs the lot turns.

The key lands on a ring, so a lot has a predictable node and a new node takes a share of the keys. That placement is Consistent Hashing in [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/). Each lot is kept on N copies, and this store uses N = 3. Lot status has to return the put that was acknowledged, so its write set and its read set share a copy: W = 2 and R = 2. A display of crates packed today may show a stale count, so it uses W = 1 and R = 1. The overlap rule those pairs rely on is Quorum Reads and Writes in [Consistency and Replication](../09_Consistency_and_Replication/).

Two puts that neither saw the other leave two values, and the way one replaces the other, or both stay for a merge, is Conflict Resolution in [Consistency and Replication](../09_Consistency_and_Replication/). The node the client calls, the wait for acknowledgements, and a read that writes a newer value back are Read and Write Path in that topic. A copy that stops answering, and a write held aside until it returns, are Replica Failure Handling there. A deadline on the way to a copy is Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/).

```text
calls           get(key), put(key, value)
placement       Consistent Hashing
N               3
lot status      W = 2, R = 2
crates packed   W = 1, R = 1
overlap         Quorum Reads and Writes
two puts        Conflict Resolution
client node     Read and Write Path
silent copy     Replica Failure Handling
deadline        Timeouts and Retries
```

## Metrics Monitoring System

Cold rooms report temperature, and the packing doors report a count. A push has the room send each sample to a collector. Pear room sits behind the shed network, and the collector cannot dial it, so pear room pushes. A scrape has the collector read a metrics page on an interval. The door counter can be dialed, so the collector scrapes it. A missed scrape is the door going silent. On the push path, a heartbeat is what makes a silent room visible, because a room with nothing new and a room that has stopped look alike until that heartbeat is late.

A sample is a metric, a time, a value, and tags. The store that appends samples and answers a range is Time-Series Database in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). The exchange keeps raw samples for a day, a one-minute series for a month, and a one-hour series after that. Building the coarser series from a closed day is a scheduled job. The job shape is Batch Processing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/).

Pear room pages when the temperature stays above 4°C for ten minutes. The rule runs every minute. One open incident for that room and that rule means later evaluations in the same stretch stay quiet. A page repeats after the incident is resolved, or after the repeat interval the rule names.

```text
pear room       push, plus a heartbeat for silence
door counter    scrape; a missed read is silence
sample          metric, time, value, tags
store           Time-Series Database
coarser series  one minute, then one hour
job             Batch Processing
page            one open incident per room and rule
```

## Ticket Booking System

The Saturday grafting class has 40 benches. Many members tap Reserve together, and bench 7 can be confirmed for one member. The tap takes a hold. The bench is HELD for 8 minutes under that member. A second tap in the window finds it held. Payment before the 8 minutes elapse confirms it. The timer, or a payment that fails, sets the bench back to AVAILABLE.

The exclusive update, a row lock or a version check, is Optimistic or Pessimistic in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). A lease on the hold when it lives outside one database is Distributed Locks in that topic. The charge that turns a hold into a confirmation is Authorize and Capture in [Payment and Financial Systems](../23_Payment_and_Financial_Systems/). Confirmation runs after the capture succeeds. A failed capture, or a hold that reaches 8 minutes with no capture, returns the bench.

The benches stop at 40 confirmed seats. The dawn wagon to the upper field is a separate inventory. It has 20 seats and sells 22 tickets, because two riders usually miss the gate. At the gate, the latest of those extra tickets is rebooked onto the next wagon. A bench has no such spare. Two members who both arrive each need their own.

```text
class           40 benches, HELD for 8 minutes
confirm         capture succeeded, inside the 8 minutes
release         the timer, or a failed capture
exclusive row   Optimistic or Pessimistic
lease           Distributed Locks
charge          Authorize and Capture
wagon           22 tickets for 20 seats
gate            the latest extra ticket takes the next wagon
```

## Matching Engine

The morning call matches bids and asks for one variety at a time. An ask rests with a price, the time it arrived, and a crate count. Asks are ordered by price ascending, and by time ascending at one price. Bids are ordered by price descending, then time ascending. A buy crosses when its limit is at least the best ask. It fills at the resting ask's price, earlier time first at that price, then walks to the next ask. Crates the buy cannot take, because the next ask is above the limit, rest on the bid book at the buy's limit.

One morning book looks like this. Four crates ask 12 at time 1, three crates ask 12 at time 2, and eight crates ask 13 at time 0. A buy of nine crates at limit 12 takes four from the earlier ask and three from the later ask at 12. Two crates rest as a bid at 12. The eight crates at 13 stay on the ask book.

Every order takes a sequencer stamp before it reaches a book. The stamp is one increasing number, and that number is the arrival time the book sorts on. Two orders that met at the door have one order after the stamp. The match for one variety runs on one thread, with the book in memory, so that thread keeps the book consistent on its own. A second variety is a second thread. The fill returns before anything is written to disk. The trade is then handed to a queue. Settlement, the grower's statement, and the buyer's receipt read that queue on their own pace. The buffer and the later consumer are Message Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

```text
asks            lower price, then earlier time
bids            higher price, then earlier time
9 at limit 12   fills 4, then 3; 2 crates rest as a bid at 12
left on ask     8 crates at 13
sequencer       one increasing stamp, then the book
one variety     one thread, book in memory
after the fill  Message Queue
```
