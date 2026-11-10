# Geospatial and Location-Based Services

Nearby search, geofences, and live positions all start from the same problem: latitude and longitude are two numbers, and the indexes we already know order one. A geohash, a quadtree, and S2 cells each fold a map into something a lookup can prune. A proximity call reads a box of candidates and then a real distance. A geofence compares this sample with the previous one. Businesses are rebuilt in a batch. Drivers are replaced in memory and expired with a TTL. Caching, sharding, the socket that carries a ping, and the push after a fence fires stay in the topics that own them. A keyword match on a place name stays in Search Autocomplete and Information Retrieval.

## Key Points

- **Geohash** — interleaves longitude and latitude bits, longitude first, and writes each five bits as one base32 character. A shared prefix is one rectangle and one B-tree range. At the equator, length 5 is about 4.9 km across, length 6 about 1.2 km by 610 m, and length 7 about 150 m. The east-west side shrinks with cos(latitude). Two places a short walk apart can miss the prefix when a cell wall falls between them, so a query reads the home cell and the eight that touch it, then checks the distance.
- **Quadtree** — an in-memory tree that splits a box into four when it holds more than a small cap and is still larger than a minimum size. With a cap of 4 and a floor of 50 m, a dense 200 m box splits, a sparse 800 m box stays a leaf, and a crowd already inside the floor stops. A radius query opens only boxes that meet the circle. Choose it when the points fit in memory and density is uneven.
- **Google S2** — a degree of longitude is about 111 km × cos(latitude): about 74 km at 48° and about 23 km at 78°. S2 projects the sphere onto six cube faces, quarters the cells to level 30, and numbers them along a Hilbert curve as 64-bit ids so a circle becomes a few id ranges. Cells at one level have roughly equal area. H3 is the hexagonal grid for the same global job. A single-city catalog can stay on a geohash prefix.
- **Proximity Service** — pick a cell at least as big as the radius, read it and its eight neighbors, keep candidates within the radius, and sort. A corner of the box can fail the distance. A repeated catalog search can sit in a cache. A prefix can name a shard, and a downtown prefix runs hot. Moving drivers are Location Updates.
- **Geofencing** — a circle is a distance compare, such as under 30 m from a center. A polygon is inside when an eastward ray crosses an odd number of edges. Outside then inside is an enter. Inside then outside is an exit. Debounce GPS jitter on the line. A long fence list tests only the boxes the index returns. The send is Push Notification System.
- **Location Updates** — a business index is rebuilt beside the live one and swapped in, so a handful of edits a day can wait for the batch. Drivers live in memory: a million of them reporting every 5 seconds is about 200,000 single-key writes a second, and a TTL of a few missed pings, such as 30 seconds, drops a silent device. The connection is WebSockets and SSE.

## Example

Two San Francisco hashes a few dozen meters apart share a length-6 cell. A third hash, about 200 m north across a cell edge, does not. A prefix box from 0 to 100 holds the corner and the cafe. A 40 m radius keeps the cafe. A sample that was outside a fence and is now inside records an enter.

```python
def shares(left: str, right: str, length: int) -> bool:
    return left[:length] == right[:length]


def in_box(pin: tuple[int, int], box: tuple[int, int, int, int]) -> bool:
    x, y = pin
    x0, x1, y0, y1 = box
    return x0 <= x <= x1 and y0 <= y <= y1


def within(pin: tuple[int, int], center: tuple[int, int], radius: int) -> bool:
    return (pin[0] - center[0]) ** 2 + (pin[1] - center[1]) ** 2 <= radius**2


def kept(
    pins: tuple[tuple[str, tuple[int, int]], ...],
    center: tuple[int, int],
    radius: int,
    box: tuple[int, int, int, int],
) -> tuple[str, ...]:
    return tuple(name for name, pin in pins if in_box(pin, box) and within(pin, center, radius))


def crossed(was_in: bool, now_in: bool) -> str:
    if not was_in and now_in:
        return "enter"
    if was_in and not now_in:
        return "exit"
    return "still"


home = "9q8yyk8"
nearby = "9q8yyk9"
across_edge = "9q8yym0"
places = (("corner", (2, 2)), ("cafe", (60, 55)), ("far", (180, 50)))
print(
    shares(home, nearby, 6),
    shares(home, across_edge, 6),
    kept(places, (50, 50), 40, (0, 100, 0, 100)),
    crossed(False, True),
)
# True False ('cafe',) enter
```

The length-6 range is one B-tree read for the two cafes that share `9q8yyk`, and a different read for the place across the cell edge. The far pin never entered the box. The corner pin did, and the radius removed it. Recording the enter is the fence test. Sending the message stays in Real-Time and Notification Systems.

## See also

- [Caching](../05_Caching/) — When Caching Helps and Cache Tier Placement. A repeated proximity read of a slow-changing catalog can sit there, with an explicit staleness bound. The prefix query and the distance filter stay here.
- [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/) — Horizontal Partitioning (Sharding) and Hot Partition Mitigation. Placing a prefix on a shard, and cooling a downtown prefix, stay there. The prefix that names a cell stays here.
- [Networking and Communication](../10_Networking_and_Communication/) — WebSockets and SSE. The connection that carries a location ping stays there. Which index that ping updates stays here.
- [Search Autocomplete and Information Retrieval](../18_Search_Autocomplete_and_Information_Retrieval/) — a keyword match on a place name stays there.
- [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/) — Push Notification System. The send after a fence fires stays there. The enter and the exit stay here.
