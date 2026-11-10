## Horizontal Partitioning (Sharding)

Horizontal partitioning, also called sharding, places different rows of one dataset on different machines. Each shard is a primary for its own rows: its own disk and its own write log. Two bookings on two shards do not share that log.

You do this when one primary's writes or storage are the ceiling. A larger machine is vertical scaling, and extra stateless web servers are horizontal scaling. Both are [Scalability Fundamentals](../02_Scalability_Fundamentals/). On the Scale Cube, splitting the rows is the Z-axis: the same code, a different slice of the keyspace. An equality lookup on the shard key lands on one shard. A query that does not carry the key is a scatter-gather: ask every shard and merge. A second way in is a lookup you keep beside the key. Relational joins, hot-shard diagnosis, and the copy while rows move are Database Sharding and Sharding Challenges in [Databases Relational](../06_Databases_Relational/). A commit that must prepare on two shards is Two-Phase Commit in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). Leaving one box because the key space no longer fits is Distributed Key-Value Basics in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/).

```text
one primary   12 million bookings, one log
four shards   about 3 million each, four logs
```

## Vertical Partitioning

Vertical partitioning moves different tables, columns, or feature data onto different servers or stores. The booking row stays on the relational primary. The gate-scan log for that sailing, wide and append-only, lives on another disk. One page may read both.

Vertical scaling is a bigger machine for the box you already have. That lever is Vertical Scaling in [Scalability Fundamentals](../02_Scalability_Fundamentals/) and Vertical Database Scaling in [Databases Relational](../06_Databases_Relational/). The Scale Cube's Y-axis is a split by function, a different service. Its Z-axis is a split of the same rows by key, the previous card. A vertical partition can sit behind a Y-axis service. It does not shard a key, and it does not raise the write rate of the booking log. Which store fits the scan log is [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/).

```text
bookings(sailing_id, seat, fare)    relational primary
scans(sailing_id, at, gate)         another store, another disk
```

## Choosing a Shard Key

The shard key is the column, or the composite, that picks the shard. The query you serve most should include it, so that query hits one shard. The key should also spread writes. A key that does only one of those is the usual mistake.

The ferry page that loads one sailing wants `sailing_id`. Every booking for that departure sits together, and the read is one shard plus a time order. A passenger's upcoming sailings are then a lookup from passenger to sailing ids. That lookup is small. `passenger_id` would keep one passenger together and scatter one sailing across shards. `departure_day` puts today's inserts on the latest shard. A composite such as `(region_id, sailing_id)` keeps a region together when you operate that way, and still spreads sailings inside the region. An index that is not the shard key, and a join across shards, are Sharding Challenges in [Databases Relational](../06_Databases_Relational/).

```text
sailing_id       one sailing, one shard; the passenger page is a lookup
passenger_id     one passenger, one shard; a sailing is scatter-gather
departure_day    today's inserts share one shard
```

## Range Partitioning

Range partitioning gives each shard a contiguous span of the key. Shard A owns sailing ids 1 through 3000. A query for ids 100 through 180 reads A and can stop at the end of that span. A query that crosses 3000 reads A and B and merges.

The span is only even when the key is. Names, postal codes, and a timestamp all clump. The shard that owns "now" takes the inserts while older shards sit quiet. Splitting that hot span is a rebalance of the map, not a new hash function. Use a range when the range scan is the product and you will watch the edges.

```text
shard A   sailing_id 1–3000
shard B   sailing_id 3001–6000
ids 100–180      shard A
ids 2990–3010    shard A and shard B
```

## Hash Partitioning

Hash partitioning maps `hash(key) % N` to a shard. Sequential sailing ids that would share a range land on different shards. Point lookups spread. A range scan does not: ids 100 through 180 are not one span, so the read is a scatter-gather across the shards.

N is part of the address. Sailing 1 stays on shard 1 when N goes from 4 to 5. Sailing 10 was shard 2 and becomes shard 0. Sailings 11 and 14 move as well. Changing N remaps almost every key, not only the keys near a boundary. That remap is why the ring exists. The relational cost of copying those rows is Sharding Challenges in [Databases Relational](../06_Databases_Relational/).

```text
sailing  1 % 4 → 1     sailing  1 % 5 → 1
sailing 10 % 4 → 2     sailing 10 % 5 → 0
sailing 11 % 4 → 3     sailing 11 % 5 → 1
sailing 14 % 4 → 2     sailing 14 % 5 → 4
```

## Consistent Hashing

Consistent hashing places nodes and keys on one ring. Hash the node to a position. Hash the key to a position. Walk clockwise from the key. A node that sits on the key's position is the owner. Otherwise the first node you meet owns the key. That walk is the lookup. How a client learns the map is Request Routing, later in this topic.

Adding a node inserts one position. It takes the arc from its predecessor up through its own position. Those keys used to belong to the next node clockwise, and the rest of the ring stays put. Removing a node gives its arc to its successor, the next node clockwise. With one position per node, that arc is about `1/N` of the keys when the arcs are even. N is the count after an add, or the count before a remove. The keys that move are the arc. They are `1/N` only when the arcs are even.

The next nodes clockwise can hold copies of the same key. How many of those copies a write waits for, and whether a read may see an older one, is [Consistency and Replication](../09_Consistency_and_Replication/). A node going quiet is not the repair, and it is not the write path or the read path. Those are the same topic. A whole site going dark is [High Availability and Reliability](../03_High_Availability_and_Reliability/). Distributed caches often choose a node with this ring. Cache-aside, and a hot key that is a cache problem, stay in [Caching](../05_Caching/).

```text
circle 0–99: A at 10, B at 40, C at 75
hash 30 walks to B
hash 80 wraps past 99 and meets A
add D at 25, from this ring: D takes (10, 25] from B
remove B, from this ring: (10, 40] goes to C
```

## Virtual Nodes (Vnodes)

One position per physical machine has two problems. The arcs are uneven, so one machine can own much more of the ring than another. An add or a remove then shifts load only with the neighbor that owned the arc, so one machine absorbs the whole change and the others keep their share.

Many virtual nodes per physical machine place that machine at many positions. The arcs get smaller, and the shares get closer to even. Adding a machine inserts many positions and takes a thin slice from many neighbors. Removing it hands many small arcs to many successors. The machine still has one disk. The ring stops treating one random point as a fair share. A cache cluster uses the same idea when the machines differ in size. The cache patterns stay in [Caching](../05_Caching/).

```text
one point each:   arcs 60, 10, 30
many points each: each machine closer to a third
```

## Rebalancing

Rebalancing moves data when a node joins, leaves, or a span grows skewed. The move is a copy, then a cutover. Reads and writes continue. A rebalance that refuses traffic until the copy finishes is an outage of that key range. During the copy a key can sit on the source, the destination, or both. One owner must accept the write, or the row forks. That hazard is also Sharding Challenges in [Databases Relational](../06_Databases_Relational/).

Fixed partitions: create more partitions than nodes. The key hashes into a partition, and the partition sits on a node. Adding a node moves some partitions. The partition number does not change. With 240 partitions on 4 nodes, each node holds 60. A fifth node takes 12 from each, and every node holds 48. The function still has 240 partitions.

Dynamic split: cut a partition when it passes a size you set, and merge partitions that shrink under a floor. Only that span changes. HBase splits regions this way.

Virtual nodes: the new machine takes many small arcs, as the previous card describes. The partition map those moves update is the next card.

```text
240 partitions, 4 nodes, 60 each
a 5th node takes 12 from each → 48 each
a key's partition number stays
```

## Request Routing

Request routing is how a client reaches the shard the partition map names. The map is the object: a key range, or a hash partition, to a node. Consistent hashing told you how to compute an owner from positions. This card is how that result is stored and refreshed.

The client can hold the map and send straight to the owner. There is no extra hop. Every language you ship has to learn a new map when membership changes, or it will keep writing to a node that no longer owns the key.

A proxy can hold the map. Clients stay simple, which matters when you do not ship those clients. The proxy is another hop, and it has to scale with the request rate.

Any node can accept the request and forward it when it is not the owner. Nodes exchange the map by gossip. There is no central coordinator. Cassandra is the usual example. While membership is changing, two nodes can name different owners, and a forward uses the map the receiver has. A coordination service can store the map for the clients or the proxy. It does not store the booking rows.

```text
client map    client → owner
proxy         client → proxy → owner
gossip        client → any node → owner
```

## Hot Partition Mitigation

A hot partition is a shard whose key, or whose range, takes a disproportionate share of the traffic. Even hashing does not fix one key that is most of the writes. Sailing 88 is a celebrity key. Every booking for it hashes to one shard.

Salt the key. Append a small bucket, `88#0` through `88#7`, and write each booking to one bucket. The sailing is no longer one partition. The sailing page reads all eight and merges. That merge is the cost. Eight reads are worth it when the single key was the ceiling, and a client that reads one bucket sees one eighth of the bookings.

Split a hot range when the clump is a span, not one key. Cut "this week" into days. The map gains spans. Keys outside the hot span stay where they are.

Isolate the key on its own shard and leave the ring for everyone else. That shard can be a larger machine, which is vertical scaling for one key, in [Scalability Fundamentals](../02_Scalability_Fundamentals/). The next hot sailing is a new isolation until you give it the same treatment. A relational hot member, including a counter row the reader cannot merge, stays in Sharding Challenges in [Databases Relational](../06_Databases_Relational/). A hot key in a cache, and copying that value across cache nodes, is Hot Key Mitigation in [Caching](../05_Caching/).

```text
sailing 88          one shard takes every booking
sailing 88#0–#7     eight shards, the page merges eight reads
```
