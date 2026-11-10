# Geospatial and Location-Based Services

Cindermoss Survey indexes plot pins across a valley and a polar holding, answers a radius from the drying shed, and decides when a crew enters the work ring or leaves the frost hollow. A geohash prefix, a quadtree, and S2 cells are the indexes. The proximity path reads a box and then a distance. Fences are the enter and exit tests. Pins are rebuilt on a schedule. A crew ping updates one memory entry. A cache tier, a shard map, the socket that carries a ping, and the message after a fence fires stay in the topics that own them. A keyword match on a pin's name stays in Search Autocomplete and Information Retrieval.

## Key Points

- **Geohash** — interleaves longitude and latitude, five bits to a character. The shed `b7nq4c` and the post `b7nq4f` share `b7nq4`. The ridge `b7nq80` shares only `b7nq`. A five-character prefix is a B-tree range, a box a few kilometers across in the valley. The read is that cell and the eight that touch it.
- **Quadtree** — an in-memory tree. A box with more than 4 pins splits while it is wider than 50 meters. The yard splits. The ridge stays a leaf. A pile on one post stops at the floor. A radius query leaves a box unread when the box misses the circle.
- **Google S2** — a degree of longitude is about 74 km at 48° and about 23 km at 78°, taking 111 km at the equator. S2 projects the sphere onto six cube faces, numbers cells along a Hilbert curve as 64-bit ids, and keeps roughly equal area at one level. A valley prefix is enough near 48°. Both holdings want equal-area cells. H3 is the hexagonal cousin.
- **Proximity Service** — read the cell and its eight neighbors, then keep pins within 400 meters. A corner of the box can fail that distance. A repeated ask can sit in a cache. The valley prefix and the polar prefix can sit on different shards. A moving crew is Location Updates.
- **Geofencing** — the work ring is under 30 meters from the shed. The frost hollow is a polygon, inside on an odd number of eastward ray crossings. Outside then inside is an enter. Inside then outside is an exit. A long fence list tests only the boxes the index returns. The send is Push Notification System.
- **Location Updates** — 4,000 pins and about 12 edits a day become one scheduled rebuild, and searches keep the previous index until the swap. A ping every five seconds replaces one memory entry, 720 point-updates in an hour. The pipe is WebSockets and SSE.

## Example

The shed and the post share a five-character cell. The ridge leaves that cell. A prefix box from 0 to 100 meters holds the corner and the post. A 40-meter radius keeps the post. Pip's sample moves from outside the ring to inside.

```python
def same(left: str, right: str, length: int) -> bool:
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


pins = (("corner", (2, 2)), ("post", (60, 55)), ("lane", (180, 50)))
print(
    same("b7nq4c", "b7nq4f", 5),
    same("b7nq4c", "b7nq80", 5),
    kept(pins, (50, 50), 40, (0, 100, 0, 100)),
    crossed(False, True),
)
# True False ('post',) enter
```

The five-character range is one B-tree read for the shed and the post, and a different read for the ridge. The lane pin never entered the box. The corner pin did, and the radius removed it. Recording Pip's enter is the fence test. Sending the message stays in Real-Time and Notification Systems.

## See also

- [Caching](../05_Caching/) — When Caching Helps and Cache Tier Placement. A repeated proximity read can sit there. The prefix query and the distance filter stay here.
- [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/) — Horizontal Partitioning (Sharding) and Hot Partition Mitigation. Placing a prefix on a shard, and cooling the yard prefix, stay there. The prefix that names a cell stays here.
- [Networking and Communication](../10_Networking_and_Communication/) — WebSockets and SSE. The pipe for a ping stays there. Which index the ping updates stays here.
- [Search Autocomplete and Information Retrieval](../18_Search_Autocomplete_and_Information_Retrieval/) — a keyword match on a pin's name stays there.
- [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/) — Push Notification System. The send after a fence fires stays there. The enter and the exit stay here.
