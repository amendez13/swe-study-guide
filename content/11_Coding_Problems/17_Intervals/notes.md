# Intervals

An interval is a start and an end, and the first question is whether the ends count. Half-open ranges make a shared endpoint a miss. Closed ranges make that same point an overlap. The union of an unsorted list is [Merge intervals](#11_Coding_Problems/06_Moderate_Problems/concepts/merge-intervals). A sorted list takes one new interval in one scan. Two sorted lists meet by advancing the earlier end. A sweep counts how many cover one point. The largest equal-weight set that does not overlap, and the fewest arrows through closed balloons, both sort by the end and then disagree on a shared endpoint.

## Key Points

- **Closed and half-open intervals** — closed contains both ends, open contains neither, and half-open contains the start only. The intersection test rejects an empty half-open interval that the two comparisons accept. A normalized `TimeRanges` list is closed, ordered, and folded where a touch would have remained.
- **Intersection of two intervals** — the shared span is `[max(starts), min(ends)]` when that pair is still in order. A nest returns the inner interval. A half-open touch returns nothing. A closed touch returns the point.
- **Insert an interval** — copy the prefix that ends first, fold every overlap, and copy the suffix. O(n) when the list is already sorted. Half-open `[1, 3)` and `[3, 5)` share no point and still cover `[1, 5)`. The unsorted union is [Merge intervals](#11_Coding_Problems/06_Moderate_Problems/concepts/merge-intervals).
- **Overlaps between two lists** — each list is sorted and non-overlapping. Record the shared span, then advance the interval that ends first. Advancing the later end drops a later overlap. The scan is O(n + m).
- **Count overlapping intervals** — `+1` at each start and `-1` at each end. Half-open ranges process an end at t before a start at t. The max of the running count is the largest overlap. An empty half-open point emits no events.
- **Minimum intervals to remove** — sort by end and keep a half-open interval when `start >= last end`. The exchange swaps the optimal set's first interval for that earliest end. Sorting by start can keep one long interval and drop two short ones. Closed ranges use `start > last end`.
- **Minimum arrows** — sort closed balloons by end and shoot the end point. The next shot is the first start strictly after that point. `start >= last` fires an extra arrow into a balloon that the point already burst.

## Example

```python
def peak_overlap(spans: list[tuple[int, int]]) -> int:
    events: list[tuple[int, int, int]] = []
    for start, end in spans:
        if start >= end:
            continue
        events.append((start, 1, 1))
        events.append((end, 0, -1))
    events.sort()
    count = best = 0
    for _time, _order, delta in events:
        count += delta
        best = max(best, count)
    return best


def removals(spans: list[tuple[int, int]]) -> int:
    last = None
    kept = 0
    for start, end in sorted(spans, key=lambda span: span[1]):
        if last is None or start >= last:
            kept += 1
            last = end
    return len(spans) - kept


print(peak_overlap([(1, 4), (2, 6), (4, 7)]))
print(removals([(1, 10), (2, 3), (4, 5)]))
print(peak_overlap([(4, 4)]), removals([]))
# 2
# 1
# 0 0
```

The sweep processes the end at 4 before the start at 4, so the peak stays 2. The removal keeps the half-open intervals that end at 3 and at 5, and drops the long one. The empty point adds no event. Both inputs are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the comparison, the cost, and a Python check.
