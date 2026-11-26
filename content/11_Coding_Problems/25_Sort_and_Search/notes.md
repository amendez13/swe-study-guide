# Sort and Search

Sort and search problems either make sorting the key step or ask you to implement one well: sort a linked list, sort an array in place, find the k-th largest value, or put three kinds of values in order in one pass. The algorithms themselves are taught on [Sorting and Searching](#07_Data_Structures_and_Algorithms/09_Sorting_and_Searching), the heap side of top-k is on [Heaps](#11_Coding_Problems/16_Heaps), and sorted lookups are on [Binary Search](#11_Coding_Problems/14_Binary_Search). This topic is the problem set: sorting as a first step, choosing a sort by its constraints, the cost table and the comparison lower bound, merging runs, merge sort on a list, partitioning, pivot choice, quicksort with duplicates, counting sort, the k-th largest by heap and by quickselect, the three-value sort, searching after a sort, and how to choose between sorting, a heap, and selection. The two decisions are how much order the question really needs and which constraint (stability, memory, value range, streaming) picks the method.

## Key Points

- **Sorting as a first step** — after a sort, neighbours are the closest values and one scan replaces a nested loop; O(n log n) dominates.
- **Picking a sort by the constraints** — stable for multi-key sorts, in place for memory, merge sort for lists, counting sort for small ranges; Python's Timsort is stable.
- **Sort costs at a glance** — quadratic simple sorts, O(n log n) merge, quick, and heap sort, linear non-comparison sorts; comparisons need at least log₂(n!).
- **Merging two sorted runs** — dummy head, take the left value on ties to stay stable, attach the leftover run; O(n + m).
- **Sort a linked list** — split with fast and slow pointers, cut at the middle, sort halves, merge; O(n log n) time, O(log n) stack.
- **Partitioning around a pivot** — Lomuto keeps a boundary of smaller values and places the pivot at its final index in one O(n) pass.
- **Pivot choice and the worst case** — last-element pivot on sorted input costs n(n − 1)/2 comparisons; a random pivot removes the bad inputs.
- **Sort an array with quicksort** — random pivot plus a three-way partition; in place, O(n log n) expected, O(n) on identical values.
- **Counting sort for small ranges** — count, offset by the minimum for negatives, write back; O(n + k).
- **Kth largest with a heap** — keep a size-k min-heap whose root is the answer; O(n log k) time, O(k) space, works on streams.
- **Quickselect** — partition and keep only the side with index n − k; O(n) expected, mutates the input.
- **Three values in one pass** — `low`, `i`, `high`; do not advance `i` after swapping with `high`; loop while `i <= high`.
- **Search after a sort** — one sort, then O(log n) `bisect` lookups for counts, ranges, and nearest values.
- **Sort, heap, or select** — full order: sort; one k-th value: quickselect; stream or small k: heap; small integers: counting.

## Example

```python
import random


def k_closest(points: list[tuple[int, int]], k: int) -> list[tuple[int, int]]:
    pts = list(points)
    dist = lambda p: p[0] * p[0] + p[1] * p[1]
    lo, hi = 0, len(pts) - 1
    while lo < hi:
        r = random.randint(lo, hi)
        pts[r], pts[hi] = pts[hi], pts[r]
        store = lo
        for i in range(lo, hi):
            if dist(pts[i]) < dist(pts[hi]):
                pts[i], pts[store] = pts[store], pts[i]
                store += 1
        pts[store], pts[hi] = pts[hi], pts[store]
        if store == k - 1:
            break
        if store < k - 1:
            lo = store + 1
        else:
            hi = store - 1
    return sorted(pts[:k], key=dist)


stops = [(3, 4), (-1, 1), (5, -2), (0, -2), (2, 2), (-6, 0)]
print(k_closest(stops, 3))
print(k_closest(stops, 1), k_closest([], 0))
# [(-1, 1), (0, -2), (2, 2)]
# [(-1, 1)] []
```

Delivery stops are points on a grid, and the depot is at the origin. Quickselect on squared distance (no square root needed, because it keeps the order) partitions the stops until the k nearest occupy the first k slots, which takes O(n) expected time; only those k are then sorted for display, O(k log k). A size-k max-heap would give the same answer in O(n log k) and could take stops from a stream. The coordinates are exercise values.

## More practice

Work the original exercises on the **Drills** tab. Each one names the approach, the cost, and a Python check.
