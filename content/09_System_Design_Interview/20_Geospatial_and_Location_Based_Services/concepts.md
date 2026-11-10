## Geohash

A geohash is a short string that names one rectangle on the earth. Places in the same rectangle share the leading characters, so "what is near here" becomes a prefix lookup on an ordinary index.

### Why it exists

Latitude and longitude are two numbers, and a B-tree orders only one column. An index on longitude alone turns "coffee within 1 km" into a scan of every business in a north-south strip the width of the search. In a city that strip is far larger than the neighborhood. Geohash folds both coordinates into one string so a neighborhood is one range of keys. The string sits on the business row, and any database that can answer "starts with this prefix" can serve the lookup.

### How it works

The encoding interleaves the bits of longitude and latitude, longitude first. Longitude begins as the interval from −180° to 180°, and latitude as −90° to 90°. Each bit asks which half of the current interval the coordinate falls in, keeps that half, and hands the turn to the other coordinate. Two places that survive the same cuts lie in the same rectangle, share a prefix, and sort next to each other. That is why the interleaving is worth doing: closeness in both dimensions becomes closeness in one string, which a B-tree can read as a range.

The first five bits of downtown San Francisco, 37.7749° N, 122.4194° W, are a full walk of one character. The longitude is west of 0°, so bit 0 is 0 and the longitude window becomes −180° to 0°. The latitude is north of 0°, so bit 1 is 1. The longitude is west of −90°, so bit 2 is 0. The latitude is south of 45°, so bit 3 is 0. The longitude is east of −135°, so bit 4 is 1. The bits `01001` are the number 9, which is the first character of the hash.

Each further character is the next five bits, written in the geohash alphabet `0123456789bcdefghjkmnpqrstuvwxyz`. The alphabet is base32 with `a`, `i`, `l`, and `o` removed, so a handwritten code is harder to misread. Five bits per character is the whole encoding: one character splits the current cell into 32. An odd length is square in degrees, because longitude's 360° span is twice latitude's 180° span and an odd length gives longitude the extra bit. An even length is twice as wide as it is tall, in degrees. On the ground, the east-west side of every cell shrinks with cos(latitude), since a degree of longitude is about 111 km × cos(latitude) while a degree of latitude stays near 111 km. The table uses 111 km per degree and rounds.

| Length | Longitude bits, latitude bits | Cell at the equator |
| --- | --- | --- |
| 1 | 3, 2 | 5,000 km × 5,000 km |
| 2 | 5, 5 | 1,250 km × 620 km |
| 3 | 8, 7 | 156 km × 156 km |
| 4 | 10, 10 | 39 km × 19.5 km |
| 5 | 13, 12 | 4.9 km × 4.9 km |
| 6 | 15, 15 | 1.2 km × 610 m |
| 7 | 18, 17 | 150 m × 150 m |
| 8 | 20, 20 | 38 m × 19 m |

A nearby-search index stores a hash longer than the query prefix. That San Francisco point encodes as `9q8yyk8`. A cafe about 30 m east encodes as `9q8yyk9`. The two share `9q8yyk`, a length-6 cell about 1.2 km by 610 m at the equator and about 960 m wide at this latitude. A 500 m search reads that prefix as one B-tree range. The exclusive end of the range is the next character in the geohash alphabet: after `k` comes `m`, because `l` is not in the alphabet, so the range is `['9q8yyk', '9q8yym')`.

A cell wall defeats the prefix. A point about 200 m north of the same corner encodes as `9q8yym0`. It shares only `9q8yy` with `9q8yyk8`. The cells `9q8yyk` and `9q8yym` share an edge, and the two places are a short walk apart, but a length-6 query of the home cell never returns the northern one. This interleaving is a Z-order curve, so cells that touch on the map can sit far apart in sorted order. The practical cover is the home cell plus the eight cells that share a side or a corner with it: up to nine prefix ranges. A distance check then drops anything the rectangles included and the circle did not. Shortening the prefix by one character widens the same grid into one range, and it scans more rows. The diagram draws the same rule with three short codes: `b7nq4c` and `b7nq4f` share five characters, and `b7nq80` shares four.

### Trade-offs

A geohash is the default when places are mostly static and the index should be a string column. You can cache by prefix and shard by prefix, and the encoder is short enough to implement directly. Redis GEO stores a geohash in a sorted set, which is this design in a widely used in-memory form.

The grid is even in degrees, so the same length covers less ground toward the poles. A length-5 cell is about 4.9 km by 4.9 km at the equator, about 3.3 km wide at 48° where a degree of longitude is about 74 km, and about 1.0 km wide at 78° where a degree of longitude is about 23 km. A guide that stays in one band of latitude can pick one length and keep it. A product whose "1 km" must mean the same ground distance in Singapore and in Oslo wants the equal-area cells on the Google S2 card. H3, the hexagonal grid, is the other global option.

A quadtree is the better fit when the set fits in memory and density is very uneven. The tree grows deep downtown and stays shallow in empty country, and it has no string prefix to shard on. S2 keeps the "one id, then a range scan" shape and replaces Z-order rectangles with cells of roughly equal area ordered by a Hilbert curve.

### In an interview

Store the geohash on the business row. Pick the length from the radius with the table, query that cell plus its eight neighbors, filter by real distance, and sort. Name the boundary before you are asked: two places a short walk apart can miss a shared prefix when a cell wall falls between them. If the product is global, switch the id to S2 or H3 and keep the same query shape. Mention that a downtown prefix is a hot shard, and that a repeated neighborhood search can be cached.

### Recap

- Each character is five bits, longitude and latitude interleaved with longitude first, written in a 32-character alphabet.
- A shared prefix is one rectangle, which a B-tree reads as one range. Nearby places usually share a long prefix because they survived the same cuts.
- A cell wall can split a short walk into two prefixes. Read the home cell and the eight that touch it, then apply the distance.
- At the equator, length 5 is about 4.9 km across, length 6 is about 1.2 km by 610 m, and length 7 is about 150 m. The east-west side shrinks with cos(latitude).

![Geohash](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-1-geohash.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 1.*

## Quadtree

A quadtree is an in-memory tree of nested rectangles. A crowded rectangle splits into four equal children, and an empty stretch of map stays one leaf.

### Why it exists

A geohash spends the same resolution on every part of the map. A downtown block and an empty county of the same prefix length become the same size cell, so the county scan reads a wide box of almost nothing, while downtown is still coarser than the search unless every row stores a long hash. A quadtree spends depth only where the points are. That fits a working set that lives in memory: the businesses of one city loaded at startup, or the drivers currently connected to one machine.

### How it works

The root is one box around the service region. Inserting a point walks down to a leaf. The leaf splits into northwest, northeast, southwest, and southeast when it holds more points than a small cap and the box is still larger than a minimum size. Both numbers are knobs. The cap keeps a leaf cheap to scan. The floor stops a crowd standing at one address from splitting forever, because those points may never fall into different quadrants, and it caps the depth of a lookup.

The diagram uses a cap of 4 and a floor of 50 m, a reasonable pair when searches are a few hundred meters:

- Six businesses in a 200 m box split. The children are 100 m boxes, and the points spread across them. The diagram calls this box the yard.
- Two businesses in an 800 m box stay a leaf. There is nothing further to prune. The diagram calls this box the ridge.
- Nine businesses already inside a 40 m box stop, even though the count is over the cap. A 50 m floor is already finer than a 400 m search, so another split would not remove any of them from that search. The diagram calls this box the post.

A radius query opens a child only when that child's box meets the circle. A box that misses the circle is left unread, and so is every point under it. Points in the boxes that remain still take a distance check. A box can touch the circle at a corner and hold a point outside the radius. A point query follows one child at each level, so its cost is the depth, and the floor is what bounds that depth. Building the tree walks every point down its path and replaces a leaf with four children when the split rule fires.

### Trade-offs

Choose a quadtree when the points fit in memory, density varies sharply across the map, and the process that answers the query is the process that holds the tree. Empty regions cost a single leaf. A fixed geohash grid cannot make that trade.

Choose a geohash when the index has to be a column, when you want a stable prefix to cache or to shard, or when the catalog is too large to pin in one process. A quadtree built on raw latitude and longitude still uses degree rectangles, so it shrinks east-west toward the poles the same way a geohash does, unless you project the coordinates first.

S2 is a quadtree on each of the six faces of a cube, with a 64-bit id you can store and range-scan, and with cells of roughly equal ground area. H3 is the hexagonal grid for that same global job. Use one of those when the tree has to cover the whole earth evenly and has to outlive a single process. Use the plain quadtree when you want the density adaptation and you are willing to keep the structure in memory.

### In an interview

State the split rule and the minimum size, and say what the floor is for: a pile of points at one address must stop splitting. Walk a radius query as "open a box only when it meets the circle, then distance-filter the points that remain." Say the structure lives in memory. If the question grows into a durable multi-city index, move to a geohash or to S2, and say that the quadtree's advantage was spending resolution on the dense parts of the map.

### Recap

- Split a leaf into four equal boxes when it has more than the cap and is still larger than the floor. The diagram's knobs are 4 points and 50 m.
- A dense 200 m box splits. A sparse 800 m box stays a leaf. A crowd already inside the floor stops.
- A radius query skips any box that misses the circle, then measures the points that were opened.
- The tree matches uneven density in memory. A database column, a shard key, or a global equal-area grid is a geohash, S2, or H3.

![Quadtree](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-2-quadtree.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 2.*

## Google S2

Google S2 names every region of the earth with a 64-bit cell id. It projects the sphere onto the six faces of a cube, splits each face into a hierarchy of cells, and numbers those cells along a Hilbert curve so a search circle becomes a short list of id ranges.

### Why it exists

A geohash cell is a rectangle of degrees. A degree of latitude stays near 111 km everywhere. A degree of longitude is about 111 km × cos(latitude): about 111 km at the equator, about 74 km at 48°, and about 23 km at 78°. The same prefix length is a different amount of ground, so a radius tuned in one city under-covers or over-covers a city at another latitude. S2 makes one level mean roughly the same ground area from the equator to near the poles. The Hilbert numbering also turns a region into a few ordered ranges, which is a tighter cover than a hand-built ring of geohash neighbors.

### How it works

Project the earth onto a cube. The six faces are the level-0 cells. Each deeper level splits every cell into four, through level 30. A nonlinear projection spreads those quads so they stay closer in size once they sit on the sphere. S2's default is a quadratic approximation of a tangent projection. With that default, the largest cell at a level is at most about 2.1 times the area of the smallest cell at the same level. A latitude-longitude grid has already shrunk by a factor of about five in the east-west direction between the equator and 78°.

The edges below are the square root of the average cell area on a sphere of radius 6371 km. Real edges vary around that average.

| Level | Average edge |
| --- | --- |
| 12 | about 2.3 km |
| 13 | about 1.1 km |
| 16 | about 140 m |
| 30 | about 0.9 cm |

The Hilbert curve is the part that makes the ids useful as keys. It visits every cell in an order that stays continuous: the next id along the curve shares a side with the current one, and the faces are turned so the curve continues from one face onto the next. Cells that sit together on the map tend to sit together in id order. A disk of cells therefore lies on a few segments of the curve, and each segment is one inclusive range of 64-bit ids. Each range is one B-tree read.

Geohash interleaving is a different curve, Z-order, which jumps. The same disk breaks into more separate prefixes, and the practical geohash query grabs the home cell plus eight neighbors rather than asking for an optimal cover. Hilbert is why S2 can hand you the short list of ranges instead. The 64-bit id packs the cube face, the position along the curve, and the level.

In a nearby search you store each business's cell id at the level whose edge is near the radius, ask the library for the ranges that cover the caller's circle, read those ranges, and distance-filter. The cover is still a set of cells around the circle, so the distance check stays.

### Trade-offs

| | Geohash | Quadtree | S2 | H3 |
| --- | --- | --- | --- | --- |
| Key | base32 string | the tree in memory | 64-bit cell id | hex id |
| Ground size of one step | shrinks with cos(latitude) | degree boxes, unless you project | roughly equal area at one level | roughly equal hexes |
| Nearby query | one prefix plus 8 neighbors | open boxes that meet the circle | a few Hilbert id ranges | a k-ring of hexes |
| Fits | a SQL column and a static catalog | uneven density, in memory | one radius that means the same distance worldwide | the same global job, with equal neighbor distance |

H3 is the hexagonal hierarchical index published by Uber. A hexagon has six neighbors, all at one distance. A square has edge neighbors and farther corner neighbors, which is why a geohash radius becomes a 3×3 block with a distance check after it.

S2 is the upgrade when one catalog spans very different latitudes. A single-city guide, with every place near one latitude, can keep a geohash prefix: one cell size fits the radius. The cost of S2 is the dependency. The Hilbert encoding is a library, and the id is less readable than `9q8yyk`.

### In an interview

Draw the longitude shrink first: 111 km at the equator, about 74 km at 48°, about 23 km at 78°. That is the reason to leave a pure geohash. Then say six cube faces, cells down to level 30, Hilbert order so a circle is a few id ranges, and a distance filter after the read. Mention H3 as the hexagonal alternative. If the interviewer wants a design you can implement in the room, offer geohash and say what you give up: even cell area, and a tight region cover.

### Recap

- A degree of longitude shrinks with cos(latitude). The same geohash length is a smaller patch of ground at 78° than at the equator.
- S2 projects the sphere onto six cube faces and quarters the cells to level 30, where the average edge is about a centimeter.
- Cells at one level have roughly equal area. With the default projection the largest is about twice the smallest, which is far tighter than a degree grid.
- A Hilbert curve numbers the cells so a circle becomes a few id ranges. Each range is one index scan. H3 does the global job with hexes.

![Google S2](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-3-google-s2.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 3.*

## Proximity Service

A proximity service returns the places within a radius of the caller, nearest first. The spatial index supplies a small box of candidates, and a distance check turns that box into the circle the caller asked for.

### Why it exists

Reading every business on every search stops working as the catalog grows. The index, whether a geohash, an S2 cell, or a quadtree, exists to discard the places that cannot be in range. The box it returns is larger than the circle, so the service still measures. The design is those two steps: a cheap range to gather candidates, an exact distance to keep them, and a sort to present them.

### How it works

Take a caller who wants places within 400 m, the radius on the diagram. Encode the caller's point at a length whose cell is at least that large in both directions. Length 7 is about 150 m, smaller than 400 m, so one ring of neighbors can miss part of the circle. Length 6 is about 1.2 km by 610 m at the equator, and at 48° it is still about 820 m by 610 m, so both sides clear 400 m. The home cell plus the eight cells that touch it covers the circle. The service reads those prefixes, up to nine ranges, and holds every business in them.

It then measures the distance from the caller to each candidate and drops anyone past 400 m. A business in the corner of a neighbor cell sits inside the rectangles and outside the circle. The diagram marks that corner. The survivors are sorted by distance.

Over a few hundred meters, a local flat approximation is enough: scale the longitude delta by cos(latitude) and treat the patch as a plane. A precise distance uses the haversine formula on a sphere of radius about 6371 km. The filter is there either way, because the index returned a box.

The same neighborhood and category are searched again and again, and business rows change slowly, so the candidate list or the finished page can sit in a cache. Where that copy lives, and how long it may stay stale, are When Caching Helps and Cache Tier Placement in [Caching](../05_Caching/).

A busy downtown cell and an empty rural cell should be free to land on different machines. How a prefix picks a shard, and what to do when one downtown prefix takes most of the reads, are Horizontal Partitioning (Sharding) and Hot Partition Mitigation in [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/). People and cars that move every few seconds belong on the Location Updates path, in a memory index, rather than in this batch catalog.

### Trade-offs

The nine-cell read fetches extra rows on purpose. A tighter cover, from S2's region cover or from an H3 k-ring, returns fewer extras and depends on a library. For a city guide, nine geohash ranges plus the distance check is the design to defend. A finer hash fetches less junk inside each cell, and once the radius is larger than the cell you need more than the eight neighbors. A coarser hash is one fatter range.

Caching the result matches a catalog that changes a few times a day. Caching a moving-driver query serves a location that has already changed. That is the line between this card and Location Updates. A quadtree on one machine prunes the same search by skipping boxes that miss the circle, which helps when density is uneven and the set fits in memory.

### In an interview

Walk one request: choose the geohash length from the radius, read the home cell and its eight neighbors, drop candidates past the radius, sort, paginate. Then add the two production concerns. A repeated neighborhood read can be cached, with an explicit staleness bound. The prefix is the shard key, and the downtown cell needs a plan so it does not melt one machine. Say the corner pin in one sentence, so it is clear the index gathers candidates and the distance check decides membership.

### Recap

- Pick a cell at least as big as the radius. For 400 m, length 6 works at the equator and at 48°. Length 7 is too small for a single ring of neighbors.
- Read the home cell and the eight that touch it. Measure each candidate and keep those within 400 m. Sort by distance.
- A corner of a neighbor cell is inside the box and outside the circle. The distance check removes it.
- Cache the slow-changing catalog query. Shard by prefix, and watch the downtown cell. Moving drivers use a separate memory index.

![Proximity Service](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-4-proximity-service.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 4.*

## Geofencing

A geofence is a virtual boundary around a place. The service decides whether a location is inside the boundary, and whether this location just crossed a line the previous one had not.

### Why it exists

A proximity search answers "what is near me." A fence answers "tell me when someone crosses this line": a driver entering an airport pickup loop, a courier leaving a delivery zone, a phone walking into a store's 30 m ring. The product event is the crossing. The design problem is evaluating that test on every position sample without comparing the sample to every fence in the catalog.

### How it works

A round fence is a distance compare. The ring on the diagram is inside when the sample is under 30 m from the center. A round boundary is stored as a center and a radius, because that test is one comparison and it has no edges to special-case.

A polygon, such as a delivery zone or a building outline, uses the even-odd ray test. Cast a ray due east from the sample and count the boundary edges it crosses. An odd count means inside. An even count means outside. Count an edge when one endpoint is strictly above the sample's latitude and the other is not. A ray that passes exactly through a vertex then contributes one crossing, which keeps a corner from flipping the result.

Keep the previous sample for that device. Outside followed by inside is an enter. Inside followed by outside is an exit. Two samples on the same side record nothing. GPS noise on the line itself flips the result from one fix to the next, so the event waits until the point has cleared the boundary by a margin, or until two samples in a row agree on the new side. The diagram labels the two samples Pip and Lark: one moves into the 30 m ring, and the other leaves the square.

A short list of fences can be tested one by one on each sample. A city full of store rings cannot. Index each fence by its bounding box, using the same geohash, quadtree, or S2 index the places use, and run the exact test only on fences whose boxes contain this sample. The circle is still one distance compare. The polygon pays for one test per edge, which is the reason a round boundary stays a circle.

The enter and the exit are the decision this service owns. The message the user then receives is Push Notification System in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/).

### Trade-offs

A circle is the right stored shape until the outline itself matters. It is one compare, vertices never come up, and a slightly larger radius is a simple debounce. A polygon is worth the ray test when the boundary is a real outline, a campus or a city limit.

Testing every fence is the simple loop, and it stops being acceptable once fence count times sample rate dominates the CPU budget. The bounding-box lookup is the proximity idea pointed at fences. Running the test on the device saves server load and keeps working offline. Running it on the server sees every device and can change a fence without an app release. Pick one in the interview and give the reason.

### In an interview

Give both predicates: distance under the radius for a circle, and an odd number of eastward ray crossings for a polygon. Define enter and exit from the previous sample, and mention a debounce so GPS jitter on the line does not fire a stream of events. For a large fence catalog, test only the fences whose indexed boxes contain the sample. Hand the send itself to the notification topic.

### Recap

- A circle is inside when the distance to the center is under the radius. The diagram's ring is 30 m.
- A polygon is inside when an eastward ray crosses an odd number of edges. Count a vertex once.
- Outside then inside is an enter. Inside then outside is an exit. The same side records nothing. Debounce jitter on the line.
- Many fences are filtered by bounding box first. The exact test runs on the candidates. The push that follows is a separate system.

![Geofencing](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-5-geofencing.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 5.*

## Location Updates

Location updates split into two write paths. Places that rarely move live in an index rebuilt in batches and swapped in. People and vehicles that move live in memory, with each position replaced every few seconds and expired by a TTL when the reports stop.

### Why it exists

A restaurant changes its pin occasionally. A driver changes position between two searches. One index for both either forces the restaurant catalog to absorb hundreds of thousands of writes a second, or forces the driver search to wait for a batch job. The design choice is which store a given point lives in, and how stale that store is allowed to be.

### How it works

Businesses use the batch path. A listing is added, a shop closes, or a pin is corrected only a handful of times a day across a large catalog. A job reads the business table, builds a fresh geohash or S2 index beside the one that is serving, and swaps the new index in when the build finishes. Searches during the build keep reading the previous index, so a query never sees a half-written structure. A place corrected at noon can wait until the next swap. Rewriting rows that did not change is part of that full rebuild, and the cost is paid on the schedule rather than on the search path. The diagram draws this at a size you can count: 4,000 places and about 12 edits a day become one rebuild, and the 12 edits ride along inside it.

Drivers and other moving users use a memory index. Each ping replaces that one driver's entry in a geohash held in a Redis sorted set, in an in-memory quadtree, or in a map from S2 cell id to driver id. The next "cars within 1 km" runs the same box-then-distance steps as the business search, against this memory index.

The write rate is why the driver path stays in memory. Suppose a million active drivers each report every 5 seconds. That is 200,000 updates a second, and each update replaces a single key. A scheduled rebuild of the business catalog runs far too seldom to follow those points. Sending each ping through a rebuild of the whole catalog would rewrite every business row to move one driver. The diagram's single worker, labeled Lark, reports every 5 seconds and produces 720 in-memory replacements in an hour. Same split, small enough to do by hand: one point-update per ping, against one rebuild of all 4,000 rows.

Staleness has a different bound on each path. A business is stale until the next swap, which matches how seldom a storefront moves. A driver whose phone enters a tunnel, or whose app was killed, has to disappear from matching. Give the memory entry a TTL of a few missed intervals. With a ping every 5 seconds, 30 seconds is six missed reports. Refresh the TTL on every ping, including a ping that says the driver has not moved, so a parked driver stays searchable and a silent driver expires. After the TTL the key is gone and the driver is absent from results.

The phone sends the ping on a long-lived connection. How that connection stays open is WebSockets and SSE in [Networking and Communication](../10_Networking_and_Communication/). A new point can cross a boundary. That test is Geofencing.

### Trade-offs

Rebuild-and-swap keeps every reader on a complete business index, and it spends the write once per batch. It leaves drivers minutes behind, which is too late for dispatch. The memory path absorbs 200,000 single-key writes a second and loses its contents on a crash. Drivers recover because their phones report again within seconds. The business catalog has to survive a restart, so it stays durable. If you need driver history for billing, persist the stream separately. The live matching index can still be memory.

At a million drivers the memory index is sharded by cell too. A downtown cell is a hot memory shard, the same shape as the hot prefix on the proximity path. A driver who crosses a cell boundary is a delete in the old cell and an insert in the new one, or a single replace when the key is the driver id and the cell is a field on the value.

### In an interview

Draw the two paths before any schema. Places: rebuild a new index beside the live one, keep serving the old index, swap when the build finishes. Drivers: replace one memory entry every few seconds. Put a write rate on the driver path, such as a million drivers every 5 seconds making 200,000 writes a second, and put a TTL beside it, such as 30 seconds. Point the connection at WebSockets and SSE, and point a crossing at Geofencing.

### Recap

| | Businesses | Drivers and moving users |
| --- | --- | --- |
| How often a point changes | a handful of edits a day | a position every few seconds |
| What is written | a new index built beside the live one, then swapped | one memory entry, replaced in place |
| Write volume | one catalog rebuild per batch | about 200,000 writes/s for a million drivers every 5 s |
| How stale a result may be | until the next swap | a TTL of a few missed pings, such as 30 s |

![Location Updates](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-6-location-updates.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 6.*
