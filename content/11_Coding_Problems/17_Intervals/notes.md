# Intervals

An interval is a start and an end, and the first question is whether the ends count. Half-open ranges make a shared endpoint a clean miss. Closed ranges make that same point an overlap. Sort by start to merge or to insert. Split starts and ends when the question is how many cover one point. Two sorted lists meet with two pointers. The largest set that does not overlap keeps the interval that ends first.

## Key Points

- **Closed, open, or half-open** — closed contains both ends, open contains neither, and half-open contains the start only. A shared endpoint is the case that changes. A small class is the same pair with names.
- **The shared span** — half-open overlap is `a.start < b.end and b.start < a.end`. The intersection is `[max(starts), min(ends)]` when that pair is still in order.
- **The end you keep is the later one** — sort by start, then extend with the max of the two ends. Writing the new end chops a nested span. The walk is Merge intervals.
- **A sweep of starts and ends** — `+1` at each start and `-1` at each end. For half-open ranges, an end at time t is processed before a start at t. The max of the running count is the largest overlap.
- **Overlaps between two sorted lists** — each list is sorted and non-overlapping. Record the shared span, then advance the interval that ends first. The scan is O(n + m).
- **Insert one interval into a sorted list** — copy the prefix that ends first, fold every overlap into one span, and copy the suffix. The scan is O(n) when the list is already sorted.
- **How many fit, and how many shots** — sort by end. Half-open meetings stay when `start >= last end`. A closed balloon needs a new shot when `start > last shot`.

## Example

```python
def peak_overlap(spans: list[tuple[int, int]]) -> int:
    events: list[tuple[int, int, int]] = []
    for start, end in spans:
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
print(removals([(0, 5), (3, 6), (5, 8)]))
# 2
# 1
```

The sweep processes the end at 4 before the start at 4, so the peak stays 2. The removal keeps the half-open intervals that end at 5 and at 8. Both inputs are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the comparison, the cost, and a Python check.
