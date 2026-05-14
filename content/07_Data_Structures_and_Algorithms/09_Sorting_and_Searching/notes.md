# Sorting and Searching

Sorting and searching are the two most fundamental algorithmic operations. Nearly every system relies on sorted data for efficient retrieval, and knowing which sort to reach for under different constraints separates mechanical coding from real engineering judgment. The core tension is between simplicity and performance: quadratic sorts are trivial to implement but collapse on large inputs, while O(N log N) sorts require more careful design but scale. Binary search then exploits sorted order to answer queries in logarithmic time, and its variants solve a surprising range of problems once you internalize the boundary-handling patterns.

## Key Points

- **Quadratic sorts are for small inputs only** - Bubble, selection, and insertion sort all run in O(N^2) worst case and O(1) space; insertion sort is the best of the three because it runs in O(N) on nearly-sorted data and is used as the base case in Timsort.
- **Merge sort guarantees O(N log N) and stability** - It divides the array in half, sorts each half recursively, and merges; the tradeoff is O(N) auxiliary space for the merge buffer.
- **Quick sort is fastest in practice but has a weak worst case** - Average O(N log N) with low constant factors and good cache behavior, but O(N^2) when pivots are chosen poorly; randomized pivot selection effectively eliminates this risk.
- **Radix sort breaks the comparison bound** - O(kN) time by sorting digit-by-digit with counting sort; useful when k (number of digits) is small relative to log N, such as sorting IP addresses or fixed-width IDs.
- **No comparison sort beats O(N log N) worst case** - The decision-tree argument proves this: N! permutations require at least log2(N!) comparisons to distinguish, and log2(N!) = O(N log N).
- **Stability preserves relative order of equal elements** - This matters for multi-key sorting; merge sort and insertion sort are stable, quick sort and selection sort are not.
- **Binary search halves the range each step** - O(log N) in a sorted array; the classic pitfall is boundary bugs, so always use `lo <= hi` with `lo = mid + 1` and `hi = mid - 1`.
- **Binary search variants handle duplicates and rotations** - Finding first/last occurrence requires continuing the search past a match; rotated array search checks which half is sorted to decide direction.
- **Python's built-in sort is Timsort** - A hybrid of merge sort and insertion sort that is stable, O(N log N) worst case, and O(N) on nearly-sorted data; default to it unless you have a specific reason not to.
- **Choose the sort by the constraints** - Small or nearly sorted: insertion sort; guaranteed worst case needed: merge sort; general purpose in-memory: quicksort or Timsort; large fixed-width keys: radix sort.

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
print("merge_sort:", merge_sort(data))
# merge_sort: [3, 9, 10, 27, 38, 43, 82]

qs_data = [3, 7, 2, 8, 1, 5, 4]
quicksort(qs_data)
print("quicksort:", qs_data)
# quicksort: [1, 2, 3, 4, 5, 7, 8]

sorted_arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print("binary_search(23):", binary_search(sorted_arr, 23))
# binary_search(23): 5

dupes = [1, 2, 2, 2, 3, 4, 5]
print("find_first(2):", find_first(dupes, 2))
# find_first(2): 1
```

Each function demonstrates a core pattern: merge sort shows the divide-merge structure, quicksort shows in-place partitioning, binary search shows the halving loop with careful boundary updates, and the first-occurrence variant shows how to continue searching past a match to find the boundary.
