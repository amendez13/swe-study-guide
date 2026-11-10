# Geospatial and Location-Based Services — Drills

Original practice for a shared prefix, a cell edge, and a box that still needs a distance check. Each card is one exercise: commit to an answer, then check it. The numbers are invented for Cindermoss Survey, a valley office that indexes plot pins and two crews, Pip and Lark. The yard is dense. The north ridge is sparse. A work ring and a frost hollow are fences. A second holding sits near 78°. A cache tier stays in Caching. Placing a shard and cooling a hot prefix stay in Data Partitioning and Consistent Hashing. The pipe that carries a ping stays in Networking and Communication. The message after a fence fires stays in Real-Time and Notification Systems. A keyword match on a pin's name stays in Search Autocomplete and Information Retrieval.

## Prefix Cell

The stored codes are the shed `b7nq4c`, the post `b7nq4f`, and the ridge `b7nq80`. Which pairs share a cell at length 5? Does the ridge share the shed's cell at length 4? The survey queries at 5 and stores 6. What does that length mean in the valley?

```python
SHED = "b7nq4c"
POST = "b7nq4f"
RIDGE = "b7nq80"
QUERY = 5
```

**Answer:** The shed and the post share `b7nq4`, so a length-5 query reads them in one range. The ridge differs at the fifth character, so that range leaves it out. At length 4 all three share `b7nq`, a wider cell. Length 5 is the box the survey is willing to scan, a few kilometers across in this valley. Length 6 is the finer code stored on the pin, on the order of a kilometer along its long side. The B-tree serves the length-5 predicate as a bounded range on the string.

```python
SHED = "b7nq4c"
POST = "b7nq4f"
RIDGE = "b7nq80"
QUERY = 5


def same(left: str, right: str, length: int) -> bool:
    return left[:length] == right[:length]


print(same(SHED, POST, QUERY), same(SHED, RIDGE, QUERY), same(SHED, RIDGE, QUERY - 1))
# True False True
```

## Edge Neighbor

Cells are 100-meter squares. The edge pin is (99, 50). The pin across the line is (101, 50). Which cells are they in, how many meters apart are they, and does a cover of the edge pin's cell plus its eight neighbors include the cell across the line?

```python
CELL = 100
EDGE = (99, 50)
ACROSS = (101, 50)
```

**Answer:** The pins are 2 meters apart and sit in cells (0, 0) and (1, 0). A read of (0, 0) alone misses the pin across the line. The cover is nine cells, the home cell and the eight that touch it, and (1, 0) is in that cover. The distance filter still drops a pin in one of those cells that is far from the caller. The nine-cell read is how the boundary stays in the result.

```python
CELL = 100
EDGE = (99, 50)
ACROSS = (101, 50)


def cell_of(point: tuple[int, int]) -> tuple[int, int]:
    return (point[0] // CELL, point[1] // CELL)


def covers(origin: tuple[int, int]) -> tuple[tuple[int, int], ...]:
    x, y = cell_of(origin)
    return tuple((x + dx, y + dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1))


print(cell_of(EDGE), cell_of(ACROSS), ACROSS[0] - EDGE[0], len(covers(EDGE)), cell_of(ACROSS) in covers(EDGE))
# (0, 0) (1, 0) 2 9 True
```

## Quad Split

A leaf splits when it holds more than 4 pins and the box is still wider than 50 meters. A crowded box already at that floor stops. A sparse box stays a leaf. The yard has 6 pins in 200 meters. The ridge has 2 pins in 800 meters. One post has 9 pins in 40 meters. What does each do? A circle centered at (300, 300) with radius 50 meets the valley's four children. Which boxes does the query open?

```python
CAP = 4
FLOOR_M = 50
ROWS = (("yard", 6, 200), ("ridge", 2, 800), ("post", 9, 40))
QUADS = (
    ("NE", (0, 0, 400, 400)),
    ("NW", (-400, 0, 0, 400)),
    ("SE", (0, -400, 400, 0)),
    ("SW", (-400, -400, 0, 0)),
)
CENTER = (300, 300)
RADIUS = 50
```

**Answer:** The yard splits. The ridge stays a leaf. The post stops, because 9 pins in a 40-meter box are past the count and already inside the floor. The circle sits inside NE. NW, SE, and SW miss it, so those three stay unread, including every pin under them. Pins inside NE still take a distance check. The floor is what keeps the post from splitting into a chain.

```python
CAP = 4
FLOOR_M = 50
ROWS = (("yard", 6, 200), ("ridge", 2, 800), ("post", 9, 40))
QUADS = (
    ("NE", (0, 0, 400, 400)),
    ("NW", (-400, 0, 0, 400)),
    ("SE", (0, -400, 400, 0)),
    ("SW", (-400, -400, 0, 0)),
)
CENTER = (300, 300)
RADIUS = 50


def action(count: int, width: int) -> str:
    if count > CAP and width > FLOOR_M:
        return "split"
    if count > CAP:
        return "stop"
    return "leaf"


def hits(box: tuple[int, int, int, int], center: tuple[int, int], radius: int) -> bool:
    x0, y0, x1, y1 = box
    cx, cy = center
    nearest_x = min(max(cx, x0), x1)
    nearest_y = min(max(cy, y0), y1)
    return (nearest_x - cx) ** 2 + (nearest_y - cy) ** 2 <= radius**2


opened = tuple(name for name, box in QUADS if hits(box, CENTER, RADIUS))
print(tuple(action(count, width) for _name, count, width in ROWS), opened)
# ('split', 'leaf', 'stop') ('NE',)
```

## Equal Area

Take a degree of longitude as 111 kilometers at the equator. How wide is that degree at 48°, and how wide at 78°? The valley catalog stays near 48°. The full catalog also includes the polar holding. Which index does each catalog use?

```python
import math

EQ_KM = 111
VALLEY_LAT = 48
POLAR_LAT = 78
```

**Answer:** The degree is about 74 kilometers wide at 48° and about 23 kilometers wide at 78°. North-south, a degree stays near 111 kilometers, so the polar degree-box covers less ground. A valley catalog can keep the prefix: every pin is near one latitude, and one cell size fits the radius. A catalog that also holds the polar pins wants equal-area cells, one S2 level, so the same radius covers a similar patch in both places. H3 would also hold area with hexes. This survey keeps that as a cousin of Google S2.

```python
import math

EQ_KM = 111
VALLEY_LAT = 48
POLAR_LAT = 78


def lon_km(lat: int) -> int:
    return round(EQ_KM * math.cos(math.radians(lat)))


def index_for(scope: str) -> str:
    if scope == "valley":
        return "prefix"
    return "equal-area"


print(lon_km(VALLEY_LAT), lon_km(POLAR_LAT), index_for("valley"), index_for("both"))
# 74 23 prefix equal-area
```

## Box then Radius

The prefix read returns the box from 0 to 100 on both axes. The caller stands at (50, 50) and asks for pins within 40 meters. The corner pin is (2, 2), the post is (60, 55), and the lane pin is (180, 50). Which pins did the box return, and which pins survive the radius?

```python
BOX = (0, 100, 0, 100)
CENTER = (50, 50)
RADIUS = 40
PINS = (("corner", (2, 2)), ("post", (60, 55)), ("lane", (180, 50)))
```

**Answer:** The box returns the corner and the post. The lane pin, at x 180, was never in the rectangles the prefix named. The corner is about 68 meters from the caller, past 40, so the distance check drops it. The post is about 11 meters away and stays. The prefix read is the box. The radius is the circle inside it.

```python
BOX = (0, 100, 0, 100)
CENTER = (50, 50)
RADIUS = 40
PINS = (("corner", (2, 2)), ("post", (60, 55)), ("lane", (180, 50)))


def in_box(pin: tuple[int, int], box: tuple[int, int, int, int]) -> bool:
    x, y = pin
    x0, x1, y0, y1 = box
    return x0 <= x <= x1 and y0 <= y <= y1


def within(pin: tuple[int, int], center: tuple[int, int], radius: int) -> bool:
    return (pin[0] - center[0]) ** 2 + (pin[1] - center[1]) ** 2 <= radius**2


boxed = tuple(name for name, pin in PINS if in_box(pin, BOX))
kept = tuple(name for name, pin in PINS if in_box(pin, BOX) and within(pin, CENTER, RADIUS))
print(boxed, kept)
# ('corner', 'post') ('post',)
```

## Prefix Shard

The shard key is the first five characters, the same length the survey queries. Where do `b7nq4c`, `b7nq4f`, `b7nq80`, and `c4ee10` land? Of 100 queries, 80 use the prefix `b7nq4`. What does that 80 do?

```python
CODES = ("b7nq4c", "b7nq4f", "b7nq80", "c4ee10")
YARD_SHARE = 80
```

**Answer:** The shed and the post land on `b7nq4`. The ridge lands on `b7nq8`. The polar code lands on `c4ee1`. A query for one prefix stays on one shard with the pins in that cell. Eighty of every hundred queries sit on `b7nq4`, the yard. That shard's disk and its processor are the hot spot, the same shape as a downtown cell that holds the dense blocks. The ridge is a neighbor prefix, so the nine-cell read can leave `b7nq4` and touch another shard. Lengthening the yard key past the query prefix splits that one query across child shards. Moving shards, and salting one key, stay on Horizontal Partitioning (Sharding) and Hot Partition Mitigation.

```python
CODES = ("b7nq4c", "b7nq4f", "b7nq80", "c4ee10")
YARD_SHARE = 80


def home(code: str) -> str:
    return code[:5]


print(*(home(code) for code in CODES), YARD_SHARE)
# b7nq4 b7nq4 b7nq8 c4ee1 80
```

## Ping or Rebuild

The pin table has 4,000 rows and 12 edits today. The catalog path rebuilds the index once and swaps it in. Lark emits 720 pings in the hour. How many rows does the rebuild write, and how many point-updates do the pings write?

```python
PINS = 4000
EDITS = 12
PINGS = 720
```

**Answer:** The rebuild writes 4,000 rows once and folds the 12 edits into that swap. Searches keep the previous index until the swap lands. The 720 pings write 720 point-updates, one memory entry each. A ping that took the catalog path would write 4,000 rows to move one crew. The socket that carries the ping is WebSockets and SSE. The radius read over those memory entries is the same box-then-distance path as the catalog.

```python
PINS = 4000
EDITS = 12
PINGS = 720


def rows(path: str) -> int:
    if path == "rebuild":
        return PINS
    return 1


print(rows("rebuild"), EDITS, rows("ping") * PINGS)
# 4000 12 720
```

## Fence Fire

The work ring is under 30 meters from (0, 0). Pip was at (40, 0) and is now at (10, 0). The frost hollow is the square (0, 0), (20, 0), (20, 20), (0, 20). Lark was at (10, 10) and is now at (30, 10). What does the survey record for each crew?

```python
RING_M = 30
PIP_PREV = (40, 0)
PIP_NOW = (10, 0)
HOLLOW = ((0, 0), (20, 0), (20, 20), (0, 20))
LARK_PREV = (10, 10)
LARK_NOW = (30, 10)
```

**Answer:** Pip was outside the ring and is inside, so the survey records an enter. Lark was inside the hollow and is outside, so the survey records an exit. The ring is a distance compare. The hollow counts edges a ray toward increasing x crosses, and an odd count is inside. The survey stops at those two decisions. The message either crew would receive is Push Notification System.

```python
RING_M = 30
PIP_PREV = (40, 0)
PIP_NOW = (10, 0)
HOLLOW = ((0, 0), (20, 0), (20, 20), (0, 20))
LARK_PREV = (10, 10)
LARK_NOW = (30, 10)


def in_ring(point: tuple[int, int], radius: int) -> bool:
    return point[0] ** 2 + point[1] ** 2 < radius**2


def in_polygon(point: tuple[int, int], polygon: tuple[tuple[int, int], ...]) -> bool:
    x, y = point
    inside = False
    for index, (x1, y1) in enumerate(polygon):
        x2, y2 = polygon[(index + 1) % len(polygon)]
        if (y1 > y) != (y2 > y):
            cross = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < cross:
                inside = not inside
    return inside


def crossed(was_in: bool, now_in: bool) -> str:
    if not was_in and now_in:
        return "enter"
    if was_in and not now_in:
        return "exit"
    return "still"


pip = crossed(in_ring(PIP_PREV, RING_M), in_ring(PIP_NOW, RING_M))
lark = crossed(in_polygon(LARK_PREV, HOLLOW), in_polygon(LARK_NOW, HOLLOW))
print(pip, lark)
# enter exit
```
