## Geohash

A geohash is a short string that names one rectangle on the earth. Places in the same rectangle share the leading characters, so "what is near here" becomes a prefix lookup on an ordinary index. Latitude and longitude are two numbers, and a B-tree orders only one column. An index on longitude alone turns "coffee within 1 km" into a scan of a whole north-south strip. Geohash folds both coordinates into one string so a neighborhood is one range of keys.

The encoding interleaves the bits of longitude and latitude, longitude first. Each bit asks which half of the current interval the coordinate falls in, keeps that half, and hands the turn to the other coordinate. For downtown San Francisco, 37.7749° N, 122.4194° W, the first five bits are `01001`: west of 0°, north of 0°, west of −90°, south of 45°, east of −135°. That is 9, the first character. Each further character is five more bits in the alphabet `0123456789bcdefghjkmnpqrstuvwxyz`, which is base32 without `a`, `i`, `l` and `o`. At the equator, length 5 is about 4.9 km square, length 6 is about 1.2 km by 610 m, and length 7 is about 150 m square. The east-west side shrinks with cos(latitude), because a degree of longitude is about 111 km × cos(latitude).

That San Francisco point encodes as `9q8yyk8`, and a cafe 30 m east as `9q8yyk9`. A 500 m search reads the shared length-6 prefix as the range `['9q8yyk', '9q8yym')`, since `l` is not in the alphabet. A cell wall defeats the prefix: a point 200 m north encodes as `9q8yym0` and shares only `9q8yy`. Interleaving is a Z-order curve, so touching cells can sort far apart. The practical cover is the home cell plus its eight neighbors, up to nine ranges, followed by a distance check. A geohash is the default for a static catalog in a string column, and it can be cached and sharded by prefix. Redis GEO is this design in memory. A catalog spanning very different latitudes moves to S2 or H3. A small, unevenly dense set that fits in memory suits a quadtree.

```text
encode       interleave lon/lat bits, 5 bits per base32 character
prefix       one rectangle, one B-tree range
cell wall    a short walk can split two prefixes
query        home cell + 8 neighbors, then filter by distance
```

![Geohash](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-1-geohash.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 1.*

## Quadtree

A quadtree is an in-memory tree of nested rectangles. A crowded rectangle splits into four equal children, and an empty stretch of map stays one leaf. A geohash spends the same resolution everywhere, so an empty county and a downtown block of one prefix length are the same size cell. A quadtree spends depth only where the points are. That fits a working set that lives in memory: one city's businesses loaded at startup, or the drivers connected to one machine.

The root is one box around the region. A leaf splits into northwest, northeast, southwest and southeast when it holds more points than a cap and is still larger than a minimum size. The diagram uses a cap of 4 and a floor of 50 m. Six businesses in a 200 m box, the yard, split into 100 m children. Two businesses in an 800 m box, the ridge, stay a leaf. Nine businesses already inside a 40 m box, the post, stop despite the count, because the floor is finer than a 400 m search and another split would prune nothing. The floor also stops a crowd at one address from splitting forever, and it bounds the depth of a lookup.

A radius query opens a child only when that child's box meets the circle, and every point under a missed box is skipped. The points that remain still take a distance check, because a box can touch the circle at a corner and hold a point outside the radius. Choose a quadtree when the set fits in memory, density varies sharply, and the process that answers the query holds the tree. Choose a geohash when the index must be a column, a cache key or a shard key. S2 is a quadtree on each face of a cube with a storable 64-bit id, and H3 is the hexagonal grid for the same global job.

```text
split    more than 4 points and larger than 50 m
stop     a crowd inside the floor stays one leaf
query    open boxes that meet the circle, then measure
fits     uneven density, in one process's memory
```

![Quadtree](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-2-quadtree.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 2.*

## Google S2

Google S2 names every region of the earth with a 64-bit cell id. It projects the sphere onto the six faces of a cube, splits each face into a hierarchy of cells, and numbers those cells along a Hilbert curve so a search circle becomes a short list of id ranges. The reason to leave a pure geohash is the longitude shrink: a degree of longitude is about 111 km at the equator, about 74 km at 48°, and about 23 km at 78°. The same geohash length is a different amount of ground, so a radius tuned in Singapore misfits Oslo.

The six cube faces are level 0, and each deeper level splits every cell into four, through level 30. A nonlinear projection keeps the quads close in size on the sphere. With S2's default, the largest cell at a level is at most about 2.1 times the smallest, while a degree grid has shrunk about fivefold east-west between the equator and 78°. Average edges are about 2.3 km at level 12, 1.1 km at level 13, 140 m at level 16, and 0.9 cm at level 30.

The Hilbert curve makes the ids useful as keys. The next id along the curve shares a side with the current cell, so a disk of cells lies on a few segments of the curve, and each segment is one B-tree range. Geohash's Z-order curve jumps, which is why its practical query grabs nine cells instead of a tight cover. A nearby search stores each business's cell id at the level whose edge is near the radius, asks the library for the covering ranges, reads them, and distance-filters. H3, the hexagonal index published by Uber, does the same global job, and each hexagon's six neighbors sit at one distance. A single-city guide can keep a geohash. The cost of S2 is a library dependency and an id less readable than `9q8yyk`.

```text
geohash   base32 prefix + 8 neighbors   cell shrinks with cos(latitude)
quadtree  tree in memory                degree boxes unless projected
S2        a few Hilbert id ranges       roughly equal area per level
H3        a k-ring of hexes             equal neighbor distance
```

![Google S2](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-3-google-s2.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 3.*

## Proximity Service

A proximity service returns the places within a radius of the caller, nearest first. The spatial index supplies a small box of candidates, and a distance check turns that box into the circle the caller asked for. Take the diagram's 400 m search. Encode the caller's point at a length whose cell is at least the radius in both directions. Length 7 is about 150 m, too small for one ring of neighbors. Length 6 is about 1.2 km by 610 m at the equator and about 820 m by 610 m at 48°, so it clears 400 m. The service reads the home cell and its eight neighbors, up to nine ranges.

It then measures each candidate and drops anyone past 400 m. A business in the corner of a neighbor cell is inside the rectangles and outside the circle, and the diagram marks that corner. The survivors are sorted by distance. Over a few hundred meters, scaling the longitude delta by cos(latitude) and treating the patch as flat is enough. A precise distance uses haversine on a sphere of about 6371 km. The nine-cell read fetches extra rows on purpose. S2's region cover or an H3 k-ring is tighter and needs a library. For a city guide, nine geohash ranges plus the distance check is the design to defend.

Business rows change slowly and the same neighborhood is searched again and again, so the candidate list can be cached with an explicit staleness bound. That is When Caching Helps and Cache Tier Placement in [Caching](../05_Caching/). The prefix is the shard key, and the downtown cell needs a plan before it melts one machine. That is Horizontal Partitioning (Sharding) and Hot Partition Mitigation in [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/). Moving drivers belong on Location Updates, because a cached driver query serves a position that has already changed.

```text
pick     a cell at least the radius: length 6 for 400 m
read     home cell + 8 neighbors
filter   drop candidates past 400 m, like the corner pin
serve    sort by distance, cache, shard by prefix
```

![Proximity Service](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-4-proximity-service.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 4.*

## Geofencing

A geofence is a virtual boundary around a place. The service decides whether a location is inside the boundary, and whether this location just crossed a line the previous one had not. A proximity search answers "what is near me". A fence answers "tell me when someone crosses this line": a driver entering an airport pickup loop, a courier leaving a delivery zone, a phone walking into a store's 30 m ring.

A round fence is one distance compare: the diagram's ring is inside when the sample is under 30 m from the center. A polygon, such as a delivery zone, uses the even-odd ray test. Cast a ray due east from the sample and count the edges it crosses. Odd is inside and even is outside. Count an edge when one endpoint is strictly above the sample's latitude and the other is not, so a ray through a vertex counts once. The service keeps the previous sample per device. Outside then inside is an enter, inside then outside is an exit, and two samples on the same side record nothing. On the diagram, Pip moves into the ring and Lark leaves the square. GPS noise on the line flips the result between fixes, so the event waits for a margin or for two samples that agree.

A short list of fences can be tested one by one. A city full of store rings cannot. Index each fence by its bounding box with the same geohash, quadtree or S2 index the places use, and run the exact test only on fences whose boxes contain the sample. A circle stays a circle until the outline itself matters, because a polygon pays one test per edge. Testing on the device saves server load and works offline. Testing on the server sees every device and changes a fence without an app release. The message that follows the crossing is Push Notification System in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/).

```text
circle     inside when distance < radius (30 m)
polygon    inside when an eastward ray crosses an odd number of edges
event      outside -> inside = enter, inside -> outside = exit
scale      bounding-box index first, exact test on candidates
```

![Geofencing](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-5-geofencing.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 5.*

## Location Updates

Location updates split into two write paths. Places that rarely move live in an index rebuilt in batches and swapped in. People and vehicles that move live in memory, with each position replaced every few seconds and expired by a TTL when the reports stop. One index for both would force the restaurant catalog to absorb hundreds of thousands of writes a second, or force driver search to wait for a batch job.

Businesses use the batch path. A job reads the business table, builds a fresh geohash or S2 index beside the one serving, and swaps it in when the build finishes. Searches during the build read the previous index, so nobody sees a half-written structure. On the diagram, 4,000 places and about 12 edits a day become one rebuild. Drivers use a memory index: each ping replaces one entry in a geohash in a Redis sorted set, an in-memory quadtree, or a map from S2 cell id to driver id. A million active drivers reporting every 5 seconds is 200,000 single-key writes a second, far more often than any rebuild runs. The diagram's single worker, Lark, reports every 5 seconds and makes 720 replacements an hour.

Staleness has a different bound on each path. A business is stale until the next swap. A driver who enters a tunnel or whose app was killed has to disappear from matching, so the memory entry gets a TTL of a few missed intervals: 30 seconds is six missed 5-second pings. Every ping refreshes the TTL, including one that says the driver has not moved. The memory index loses its contents on a crash, and drivers recover because their phones report again within seconds. Billing history, if needed, is persisted separately. At scale the memory index is sharded by cell, and a downtown cell is a hot shard. The ping connection is WebSockets and SSE in [Networking and Communication](../10_Networking_and_Communication/), and a crossing is Geofencing.

```text
businesses   a handful of edits a day   rebuild beside, then swap   stale until next swap
drivers      a ping every 5 s           replace one memory entry    TTL 30 s
volume       1 rebuild per batch        ~200,000 writes/s for 1M drivers
```

![Location Updates](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial-6-location-updates.png)

*Source: [`diagrams/geospatial.drawio`](/content/09_System_Design_Interview/20_Geospatial_and_Location_Based_Services/diagrams/geospatial.drawio), page 6.*
