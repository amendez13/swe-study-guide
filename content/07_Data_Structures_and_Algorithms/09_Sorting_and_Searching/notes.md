# Sorting and Searching

Sorting and searching are the two most fundamental algorithmic operations. Nearly every system relies on sorted data for efficient retrieval, and knowing which sort to reach for under different constraints separates mechanical coding from real engineering judgment. The core tension is between simplicity and performance: quadratic sorts are trivial to implement but collapse on large inputs, while O(N log N) sorts require more careful design but scale. Binary search then exploits sorted order to answer queries in logarithmic time, and its variants solve a surprising range of problems once you internalize the boundary-handling patterns.

## Key Points

- **Bubble sort** — swap adjacent out-of-order pairs until a pass makes no swaps; O(N^2) average, O(N) on sorted input with the early exit; small values near the end move only one slot per pass.
- **Selection sort** — repeatedly select the minimum of the unsorted suffix; always O(N^2) comparisons but at most N swaps; not stable.
- **Insertion sort** — shift each new element left into place; O(N + inversions), so near-linear on nearly sorted data; the small-run workhorse inside Timsort.
- **Merge sort** — split, sort halves, merge with two pointers; O(N log N) in every case and stable; O(N) extra for arrays, only the stack for linked lists.
- **Quick sort** — partition around a pivot and recurse; O(N log N) average with great cache behavior, O(N^2) with bad pivots; randomize the pivot and recurse into the smaller side first.
- **Partition schemes** — Lomuto (simple, one boundary), Hoare (two pointers, fewer swaps), three-way (`<`, `==`, `>` in one pass, essential with many duplicates).
- **Heap sort** — heapify in O(N), then extract the max N times; O(N log N) worst case in O(1) extra space, but not stable and cache-unfriendly.
- **Counting sort** — count keys in a small range `0..K`, prefix-sum to positions, place records; O(N + K) and stable.
- **Radix sort** — stable per-digit passes from least to most significant digit; O(kN); breaks the comparison bound for fixed-width keys.
- **Bucket sort** — scatter by value range, sort each bucket, concatenate; O(N) expected only when the input is close to uniform.
- **Comparison sort lower bound** — N! possible orders need at least log2(N!) ≈ N log2 N yes/no comparisons in the worst case.
- **Stability** — equal keys keep their input order; it is what makes multi-pass sorting by several keys work.
- **Custom sort keys** — use `key=` with tuples for multi-key order, negate numbers to flip one field, stable two-pass sorts or `cmp_to_key` for the rest.
- **Quickselect** — partition and recurse into one side to get the k-th smallest in expected O(N); a size-k heap is O(N log k) and stream-friendly.
- **Binary search** — halve a sorted range each step for O(log N); every branch must shrink the range.
- **Lower and upper bound** — first index `>= x` and first index `> x` (`bisect_left` / `bisect_right`); their difference counts occurrences.
- **Rotated sorted array** — one half around `mid` is always sorted; check its range to decide where to go; duplicates can force O(N).
- **Binary search on the answer** — search a value range with a monotone yes/no feasibility check instead of an array.
- **Merging sorted sequences** — two pointers for two lists, a K-entry min-heap for K lists (O(N log K)); sorted runs plus a K-way merge is how external sorting works.
- **Sorting algorithm comparison** — pick by size, existing order, memory, stability, and key type; in Python default to `sorted()` with a `key=`.

## Example

```python
"""
Demonstrates merge sort, quicksort with in-place partition,
binary search, and binary search for first occurrence.
"""


# --- Merge sort ---
def merge_sort(arr: list[int]) -> list[int]:
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    merged: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


# --- Quicksort (in-place, Lomuto partition) ---
def quicksort(arr: list[int], lo: int = 0, hi: int | None = None) -> None:
    if hi is None:
        hi = len(arr) - 1
    if lo >= hi:
        return
    pivot = arr[hi]
    i = lo
    for j in range(lo, hi):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[hi] = arr[hi], arr[i]
    quicksort(arr, lo, i - 1)
    quicksort(arr, i + 1, hi)


# --- Binary search (iterative) ---
def binary_search(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# --- Binary search: first occurrence ---
def find_first(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid
            hi = mid - 1       # keep searching left
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result


# --- Demo ---
data = [38, 27, 43, 3, 9, 82, 10]
print("merge_sort:", merge_sort(data))  # merge_sort: [3, 9, 10, 27, 38, 43, 82]

qs_data = [3, 7, 2, 8, 1, 5, 4]
quicksort(qs_data)
print("quicksort:", qs_data)  # quicksort: [1, 2, 3, 4, 5, 7, 8]

sorted_arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print("binary_search(23):", binary_search(sorted_arr, 23))  # binary_search(23): 5

dupes = [1, 2, 2, 2, 3, 4, 5]
print("find_first(2):", find_first(dupes, 2))  # find_first(2): 1
```

Each function demonstrates a core pattern: merge sort shows the divide-merge structure, quicksort shows in-place partitioning, binary search shows the halving loop with careful boundary updates, and the first-occurrence variant shows how to continue searching past a match to find the boundary.

## More practice

Work the original exercises on the **Drills** tab: read each prompt, commit to an answer, then open the card to check it. For background reading, open CTCI Chapter 10 on the private reader under `#chapter-10-sorting-and-searching`, with `#common-sorting-algorithms` and `#searching-algorithms`. Do not copy book text or solutions into these study files.
