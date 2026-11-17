## Closed, open, or half-open

An interval is a start and an end. Closed `[start, end]` contains both ends. Open `(start, end)` contains neither. Half-open `[start, end)` contains the start and excludes the end. The same two numbers are a different set under each rule, and a shared endpoint is the case that flips. The exercise pair `(2, 6)` and `(6, 9)` shares 6: the closed pair overlaps, and the half-open pair does not. `HTMLMediaElement.buffered` returns a normalized `TimeRanges`. Those ranges are ordered and do not overlap, each range includes its ends, and a range that would only touch the previous one is folded into it.

A tuple `(start, end)` holds the pair. A small class with `start` and `end` is that pair with names, which helps when a function takes several intervals and `span.start` is clearer than `span[0]`. Ask which rule applies before writing the comparison. A closed `[6, 6]` is the single point 6. A half-open `[6, 6)` is empty, so it overlaps nothing. No intervals is an empty list. One interval has no partner to test. The block checks the exercise pair under both rules, then the point against itself.

```python
class Span:
    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end


def overlaps(a: Span, b: Span, closed: bool) -> bool:
    if closed:
        return a.start <= b.end and b.start <= a.end
    return a.start < b.end and b.start < a.end


left, right = Span(2, 6), Span(6, 9)
point = Span(6, 6)
print(overlaps(left, right, True), overlaps(left, right, False))
print(overlaps(point, point, True), overlaps(point, point, False))
# True False
# True False
```

## The shared span

Two intervals overlap when some value sits in both. For half-open ranges the test is `a.start < b.end and b.start < a.end`. Closed ranges use `<=` in both comparisons, because an endpoint counts. The shared span is `[max(starts), min(ends)]`. It is a real interval when that start is strictly before the end for half-open ranges, or at or before the end for closed ranges. A pair built after the test has failed runs backwards, and a later scan will treat that backwards pair as a real span.

The test is symmetric, so swapping the arguments does not change the answer. A nested interval shares its whole span with the outer one, and the intersection is the inner interval. A partial overlap shares only the middle. Disjoint intervals, and half-open intervals that only touch, produce a start past the end, and the validity check rejects them. A single point is a valid closed intersection and an invalid half-open one. The exercise pairs below are `(1, 4)` with `(3, 8)`, `(1, 9)` with `(3, 4)`, and `(1, 3)` with `(3, 5)`.

```python
def shared(a: tuple[int, int], b: tuple[int, int], closed: bool) -> tuple[int, int] | None:
    start, end = max(a[0], b[0]), min(a[1], b[1])
    valid = start <= end if closed else start < end
    return (start, end) if valid else None


print(shared((1, 4), (3, 8), False), shared((1, 9), (3, 4), False))
print(shared((1, 3), (3, 5), True), shared((1, 3), (3, 5), False))
# (3, 4) (3, 4)
# (3, 3) None
```

## The end you keep is the later one

Sort by start so the next interval is the next one on the line. A tie on the start breaks by end, so the shorter interval at that start comes first. The merge walk is [Merge intervals](#11_Coding_Problems/06_Moderate_Problems/concepts/merge-intervals): a start still inside the current span extends it, and any other start opens a new span. [Sort, then scan](#11_Coding_Problems/06_Moderate_Problems/concepts/sort-then-scan) is why the neighbors are adjacent only after the sort. The sort is O(n log n) and the walk is O(n). In Python the sort uses O(n) extra memory, separate from the output list.

The stored end is the max of the current end and the new end. Writing the new end chops a nested span that finished earlier. On the exercise list `(1, 10), (2, 3), (4, 6)`, that write returns `(1, 3), (4, 6)`, because 4 now looks disjoint. The max of the ends keeps `(1, 10)`. Closed ranges extend when `start <= current end`. Half-open ranges extend when `start < current end`. Empty input stays empty. One interval is that interval. The [Kiln bookings that overlap](#11_Coding_Problems/06_Moderate_Problems) drill uses another list.

```python
def merge(spans: list[tuple[int, int]], later: bool) -> list[tuple[int, int]]:
    ordered = sorted(spans)
    merged: list[tuple[int, int]] = []
    for start, end in ordered:
        if merged and start <= merged[-1][1]:
            kept = max(merged[-1][1], end) if later else end
            merged[-1] = (merged[-1][0], kept)
        else:
            merged.append((start, end))
    return merged


sample = [(1, 10), (2, 3), (4, 6)]
print(merge(sample, False), merge(sample, True), merge([], True))
# [(1, 3), (4, 6)] [(1, 10)] []
```

## A sweep of starts and ends

Split each half-open interval into two events, `+1` at the start and `-1` at the end. Sort by time, and when the time ties process the end before the start. A half-open interval that ends at t does not cover t, so a start at t must see that interval already closed. Add the delta to a running count after each event. The maximum of that count is the largest overlap. Sorting the 2n events is O(n log n) time and O(n) memory.

Processing a start before an end at the same time answers the closed question, where the point t belongs to an interval ending at t and to one starting at t. Two sorted arrays, one of starts and one of ends, compute the same peak: advance a start while it is strictly before the next end, and drop one when an end is due. A min-heap of end times answers the same count. That version is the [Rooms for the meetings](#11_Coding_Problems/16_Heaps) drill. The exercise list `(1, 4), (2, 6), (4, 7)` peaks at 2 when ends win the tie and at 3 when starts win it. An empty list peaks at 0.

```python
def peak(spans: list[tuple[int, int]], ends_first: bool) -> int:
    events: list[tuple[int, int, int]] = []
    for start, end in spans:
        events.append((start, 1 if ends_first else 0, 1))
        events.append((end, 0 if ends_first else 1, -1))
    events.sort()
    count = best = 0
    for _time, _order, delta in events:
        count += delta
        best = max(best, count)
    return best


sample = [(1, 4), (2, 6), (4, 7)]
print(peak(sample, True), peak(sample, False), peak([], True))
# 2 3 0
```

## Overlaps between two sorted lists

Each list is already sorted by start and does not overlap itself. A pointer sits on each list. The shared span of the two current intervals, when its start is strictly before its end, is one answer for half-open ranges. Then advance the pointer whose interval ends first. That interval cannot meet anything later in the other list: later intervals there start at or after the one still open, and this one has already ended. Each pointer moves once per interval, so the scan is O(n + m) time and O(1) extra memory past the output. [Two pointers](#11_Coding_Problems/06_Moderate_Problems/concepts/two-pointers) on one sorted array discards an end of that array. The move here is the earlier of two ends, which is a different discard.

Advancing the interval that ends later skips a pair that still overlaps the one left behind. On the exercise lists `(1, 4), (7, 10)` and `(3, 6), (8, 11)`, the overlaps are `(3, 4)` and `(8, 10)`. Either list empty returns nothing. Half-open `(1, 5)` and `(5, 8)` share no value, so the check rejects the point `(5, 5)`. A list that overlaps itself is outside this scan. Merge that list first.

```python
def pair_overlaps(left: list[tuple[int, int]], right: list[tuple[int, int]]) -> list[tuple[int, int]]:
    i = j = 0
    out: list[tuple[int, int]] = []
    while i < len(left) and j < len(right):
        start, end = max(left[i][0], right[j][0]), min(left[i][1], right[j][1])
        if start < end:
            out.append((start, end))
        if left[i][1] <= right[j][1]:
            i += 1
        else:
            j += 1
    return out


print(pair_overlaps([(1, 4), (7, 10)], [(3, 6), (8, 11)]))
print(pair_overlaps([], [(1, 2)]), pair_overlaps([(1, 2)], []), pair_overlaps([(1, 5)], [(5, 8)]))
# [(3, 4), (8, 10)]
# [] [] []
```

## Insert one interval into a sorted list

The list is sorted and already non-overlapping, so one new interval is three phases of one left-to-right scan. A fresh sort of n + 1 items is the slow version of the same result. Copy every interval that ends at or before the new start. Fold the new interval into every interval it overlaps, taking the minimum start and the maximum end. Copy whatever remains, unchanged and still in order. The scan is O(n) time. The new list is the output. Extra memory besides that list is O(1). Sorting again costs O(n log n) and spends the sort's O(n) memory to rediscover an order the input already had.

For half-open ranges, "ends before the new start" is `end <= start`. For closed ranges it is `end < start`, because a shared endpoint overlaps and must be folded in. The exercise list `(1, 3), (6, 8), (10, 12)` with half-open `(4, 7)` overlaps only `(6, 8)`, so the result is `(1, 3), (4, 8), (10, 12)`. `(3, 5)` into `(1, 2), (6, 8)` lands between them. `(0, 10)` into `(1, 3), (6, 8)` is the only span. An empty list with `(2, 5)` is that one span.

```python
def insert(spans: list[tuple[int, int]], new: tuple[int, int]) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    start, end = new
    index = 0
    while index < len(spans) and spans[index][1] <= start:
        out.append(spans[index])
        index += 1
    while index < len(spans) and spans[index][0] < end:
        start = min(start, spans[index][0])
        end = max(end, spans[index][1])
        index += 1
    out.append((start, end))
    out.extend(spans[index:])
    return out


print(insert([(1, 3), (6, 8), (10, 12)], (4, 7)))
print(insert([(1, 2), (6, 8)], (3, 5)), insert([(1, 3), (6, 8)], (0, 10)), insert([], (2, 5)))
# [(1, 3), (4, 8), (10, 12)]
# [(1, 2), (3, 5), (6, 8)] [(0, 10)] [(2, 5)]
```

## How many fit, and how many shots

[Greedy choice](#07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/concepts/greedy-choice) already keeps the largest set of non-overlapping intervals by taking the one that ends first. Sort by end. Keep an interval when its start is at or after the last kept end. That comparison is the half-open rule: a start on the previous end does not overlap it. The number to remove is n minus the number kept. A line of closed balloons uses the same sort and a different test. A shot is the point at a kept end, and it bursts every balloon that contains that point. The next shot is the first balloon whose start is strictly after that point. Both counts are O(n log n) from the sort, with O(1) extra memory besides the sort's own space.

The reason the earliest end is safe is on that card. On the exercise list `(0, 5), (3, 6), (5, 8)`, the half-open rule keeps `(0, 5)` and `(5, 8)` and removes 1. One closed shot at 5 bursts all three, so the arrow count is 1. Swapping the comparisons, `>` for a removal keep and `>=` for a new shot, makes both answers 2. An empty list removes nothing. One balloon needs one shot.

```python
def removals(spans: list[tuple[int, int]], touch_ok: bool = True) -> int:
    last = None
    kept = 0
    for start, end in sorted(spans, key=lambda span: span[1]):
        if last is None or (start >= last if touch_ok else start > last):
            kept += 1
            last = end
    return len(spans) - kept


def arrows(balloons: list[tuple[int, int]], point: bool = True) -> int:
    last = None
    shots = 0
    for start, end in sorted(balloons, key=lambda span: span[1]):
        if last is None or (start > last if point else start >= last):
            shots += 1
            last = end
    return shots


sample = [(0, 5), (3, 6), (5, 8)]
print(removals(sample), arrows(sample), removals(sample, False), arrows(sample, False))
print(removals([]), arrows([(2, 4)]))
# 1 1 2 2
# 0 1
```
