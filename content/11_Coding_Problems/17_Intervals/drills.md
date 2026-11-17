# Intervals — Drills

Original drills for a shared endpoint, a nested end, an insert, a free gap, a person who wants every meeting, a removal count, a sweep of stream logs, and shots along a line of balloons. Each answer has an approach, a cost, and Python. The numbers are exercise numbers.

## One person, every meeting

The exercise meetings are half-open `(0, 5)`, `(5, 8)`, and `(7, 9)`. Can one person attend every meeting? Also answer `(0, 2)` then `(2, 4)`, `(1, 3)` then `(2, 4)`, and an empty list.

**Answer:** No. After a sort by start, `(0, 5)` ends where `(5, 8)` starts, which half-open ranges allow, and `(5, 8)` overlaps `(7, 9)`. Each meeting must start at or after the previous end. The sort is O(n log n) and the scan is O(n), with O(1) extra memory besides the sort. `(0, 2)` then `(2, 4)` is a yes. `(1, 3)` then `(2, 4)` is a no. An empty list is a yes, because there is no pair that can overlap. Counting how many rooms a heap of end times needs is the [Rooms for the meetings](#11_Coding_Problems/16_Heaps) drill. This check is the case where that count is 1, and the adjacent scan is enough.

```python
def can_attend(meetings: list[tuple[int, int]]) -> bool:
    ordered = sorted(meetings)
    return all(ordered[i][1] <= ordered[i + 1][0] for i in range(len(ordered) - 1))


print(can_attend([(0, 5), (5, 8), (7, 9)]))
print(can_attend([(0, 2), (2, 4)]), can_attend([(1, 3), (2, 4)]), can_attend([]))
# False
# True False True
```

## Insert a span across the middle

The exercise list is half-open, sorted, and non-overlapping: `(0, 2)`, `(3, 6)`, `(9, 11)`. Insert `(5, 10)`. Also insert `(12, 14)` into the original list, and insert `(1, 2)` into an empty list.

**Answer:** `(0, 2)` and `(3, 11)`. `(0, 2)` ends before 5, so it is copied. `(3, 6)` overlaps `(5, 10)`, and `(9, 11)` overlaps the widened span, so the folded interval runs from 3 to 11. `(12, 14)` starts after every existing end, so the original three intervals stay and `(12, 14)` is appended. An empty list becomes `(1, 2)` alone. The scan is O(n) time. The new list is the output, and extra memory besides it is O(1). A fresh sort of the old list plus the new interval is O(n log n) and spends sort memory on an order the input already had. Half-open "ends before" is `end <= new start`. A closed list would fold a neighbor that only touches.

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


base = [(0, 2), (3, 6), (9, 11)]
print(insert(base, (5, 10)))
print(insert(base, (12, 14)), insert([], (1, 2)))
# [(0, 2), (3, 11)]
# [(0, 2), (3, 6), (9, 11), (12, 14)] [(1, 2)]
```

## How many meetings to drop

The exercise meetings are half-open `(0, 4)`, `(1, 2)`, `(2, 5)`, and `(6, 8)`. How many must be removed so the rest do not overlap? Also answer `(0, 5)`, `(1, 4)`, `(2, 3)`, the single meeting `(4, 7)`, and an empty list.

**Answer:** Remove 1. Sort by end and keep `(1, 2)`, then `(2, 5)`, then `(6, 8)`. `(0, 4)` starts before 2, so it is the one that goes. The second list keeps only `(2, 3)` and removes 2. One meeting removes 0. An empty list removes 0. The sort is O(n log n). The scan is O(n) and the counter is O(1) extra memory besides the sort. The keep test is `start >= last end`, the half-open rule. A closed list uses `start > last end`, because a shared endpoint overlaps. Keeping the interval that starts first, instead of the one that ends first, can drop two short meetings to save one long one. The selection rule is [Greedy choice](#07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/concepts/greedy-choice).

```python
def removals(spans: list[tuple[int, int]]) -> int:
    last = None
    kept = 0
    for start, end in sorted(spans, key=lambda span: span[1]):
        if last is None or start >= last:
            kept += 1
            last = end
    return len(spans) - kept


print(removals([(0, 4), (1, 2), (2, 5), (6, 8)]))
print(removals([(0, 5), (1, 4), (2, 3)]), removals([(4, 7)]), removals([]))
# 1
# 2 0 0
```

## Free gaps inside a window

Two exercise calendars, half-open, inside the window `(0, 14)`. The first is `(1, 4)` and `(8, 10)`. The second is `(3, 6)` and `(12, 13)`. What are the free gaps? Also answer a window `(0, 4)` whose only busy block is `(0, 4)`, and busy `(0, 2)`, `(2, 5)` inside the window `(0, 5)`. A free/busy query returns busy blocks. These hours are exercise hours.

**Answer:** The gaps are `(0, 1)`, `(6, 8)`, `(10, 12)`, and `(13, 14)`. Merge the busy blocks first: `(1, 4)` and `(3, 6)` become `(1, 6)`, then `(8, 10)` and `(12, 13)` stay. Walk a cursor from the window start. A busy start past the cursor is a gap, and the cursor then jumps to that block's end. The window that is busy from end to end has no gap. `(0, 2)` and `(2, 5)` only touch. Half-open ranges do not overlap, so they need not become one block, and the cursor still lands on the next start, so the gap list is empty. The merge and the walk are O(n) after an O(n log n) sort. The merged list is O(n) memory. The occupied blocks themselves are [Merge intervals](#11_Coding_Problems/06_Moderate_Problems/concepts/merge-intervals). This walk is the holes between them.

```python
def free_gaps(
    calendars: list[list[tuple[int, int]]], window: tuple[int, int]
) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(span for calendar in calendars for span in calendar):
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    gaps: list[tuple[int, int]] = []
    cursor = window[0]
    for start, end in merged:
        if cursor < start:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < window[1]:
        gaps.append((cursor, window[1]))
    return gaps


print(free_gaps([[(1, 4), (8, 10)], [(3, 6), (12, 13)]], (0, 14)))
print(free_gaps([[(0, 4)]], (0, 4)), free_gaps([[(0, 2), (2, 5)]], (0, 5)))
# [(0, 1), (6, 8), (10, 12), (13, 14)]
# [] []
```

## A shared endpoint

The exercise intervals are `(4, 8)` and `(8, 11)`. Merge them if they are closed. Merge them if they are half-open. Also merge a single closed `(4, 8)`, and merge an empty list.

**Answer:** Closed, they share 8 and become `(4, 11)`. Half-open, 8 belongs only to the second interval, so both remain. One interval is that interval. An empty list stays empty. Sort by start, then extend when the next start is still inside the current span: `<=` for closed, `<` for half-open. The sort is O(n log n) and the walk is O(n). In Python the sort uses O(n) extra memory, separate from the output. The full walk, including a nested end, is [Merge intervals](#11_Coding_Problems/06_Moderate_Problems/concepts/merge-intervals). The [Kiln bookings that overlap](#11_Coding_Problems/06_Moderate_Problems) drill merges a different list, and its test treats a touch as an overlap.

```python
def merge(spans: list[tuple[int, int]], closed: bool) -> list[tuple[int, int]]:
    ordered = sorted(spans)
    merged: list[tuple[int, int]] = []
    for start, end in ordered:
        if merged and (start <= merged[-1][1] if closed else start < merged[-1][1]):
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


pair = [(4, 8), (8, 11)]
print(merge(pair, True), merge(pair, False))
print(merge([(4, 8)], True), merge([], True))
# [(4, 11)] [(4, 8), (8, 11)]
# [(4, 8)] []
```

## The merge that chops a nested span

The exercise intervals are `(0, 9)`, `(2, 3)`, and `(4, 5)`. The merge writes the new end whenever the next start falls inside the current span. What does that return, and what is the repaired result? Also run both functions on `(0, 2)`, `(3, 5)`, which has no nested interval.

**Answer:** The buggy merge returns `(0, 3)` and `(4, 5)`. `(2, 3)` replaces the end 9 with 3, and `(4, 5)` then starts after that chopped end, so it opens a second block. The repaired result is `(0, 9)`, because the stored end is the max of the two ends. On `(0, 2)`, `(3, 5)` both functions return the same two intervals. A disjoint example does not catch this bug. The sort is O(n log n) and the walk is O(n). Empty input stays empty for both. The repaired walk is [Merge intervals](#11_Coding_Problems/06_Moderate_Problems/concepts/merge-intervals).

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


nested = [(0, 9), (2, 3), (4, 5)]
apart = [(0, 2), (3, 5)]
print(merge(nested, False), merge(nested, True))
print(merge(apart, False), merge(apart, True))
# [(0, 3), (4, 5)] [(0, 9)]
# [(0, 2), (3, 5)] [(0, 2), (3, 5)]
```

## Peak concurrent streams

The exercise streams are half-open `(0, 3)`, `(1, 4)`, `(3, 6)`, and `(6, 8)`. What is the peak if an end is processed before a start at the same time? What is the peak if the start is processed first? Also answer one stream `(2, 5)` and an empty log. The counts are exercise counts.

**Answer:** The half-open peak is 2. At time 3 the stream that started at 0 ends before the stream that starts at 3, so the count goes 2, then 1, then 2. At time 6 the same tie keeps the count from reaching 2 again. Processing starts first at those ties reaches 3. One stream peaks at 1. An empty log peaks at 0. Sort the 2n events by time, with the tie order in the second field. The sort is O(n log n) time and the event list is O(n) memory. A min-heap of end times answers the same half-open count. That version is the [Rooms for the meetings](#11_Coding_Problems/16_Heaps) drill.

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


streams = [(0, 3), (1, 4), (3, 6), (6, 8)]
print(peak(streams, True), peak(streams, False), peak([(2, 5)], True), peak([], True))
# 2 3 1 0
```

## Shots along the balloons

The exercise balloons are closed `[1, 5]`, `[2, 3]`, `[3, 7]`, `[6, 9]`, and `[10, 12]`. An arrow at a point bursts every balloon that contains that point. What is the minimum number of arrows? Also answer the single balloon `[8, 8]` and an empty list.

**Answer:** Three arrows, at 3, then 9, then 12. Sort by end. The first shot is the point 3, and it bursts `[2, 3]`, `[1, 5]`, and `[3, 7]`. `[6, 9]` starts after 3, so the next shot is 9. `[10, 12]` starts after 9, so the last shot is 12. A balloon that is a single point still needs one shot. An empty list needs none. The sort is O(n log n). The scan is O(n) and uses O(1) extra memory besides the sort. The new-shot test is `start > last shot`, because the balloons are closed and the shot is a point. Half-open meetings that may touch use `start >= last end` when the question is how many to keep. That selection is [Greedy choice](#07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/concepts/greedy-choice).

```python
def arrows(balloons: list[tuple[int, int]]) -> int:
    last = None
    shots = 0
    for start, end in sorted(balloons, key=lambda span: span[1]):
        if last is None or start > last:
            shots += 1
            last = end
    return shots


print(arrows([(1, 5), (2, 3), (3, 7), (6, 9), (10, 12)]))
print(arrows([(8, 8)]), arrows([]))
# 3
# 1 0
```
