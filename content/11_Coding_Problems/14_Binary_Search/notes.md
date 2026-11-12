# Binary Search

Binary search discards half of an ordered set of candidates after one check. The candidates may be indexes in a sorted array, the integers in a range whose feasibility flips once, or the cut in a shorter sorted array. The loop is four decisions: the search space, which side of the midpoint is discarded, when the loop stops, and what is returned. A lower midpoint is safe when a kept left side excludes the midpoint. An upper midpoint is required when a feasible midpoint becomes the new left edge. These notes are the decisions, the bounds, and the checks. They are not a catalog of published problems.

## Key Points

- **Binary search over a search space** — one comparison discards the side that cannot hold the answer. `git bisect` keeps the commits reachable from a bad commit and not from a good one. `bisect_left` returns an insertion index. PostgreSQL's `_bt_binsrch` binary-searches the keys on one B-tree page. The iterative loop is logarithmic and uses constant extra memory. Sorted arrays, numeric ranges, rotated arrays, two sorted arrays, and matrices are the five shapes below.
- **Four decisions that define the loop** — the space, the narrowing, the exit, and the return. An exact search uses a closed interval, excludes the midpoint on every miss, stops when the interval is empty, and returns the index or -1. If the target occurs, its index is still inside `[left, right]`.
- **The midpoint, overflow, and the upper midpoint** — `left + (right - left) // 2` stays in range for nonnegative endpoints that fit. Adding 1500000000 and 1500000020 wraps, in a language that wraps, to a negative midpoint. The lower midpoint of two adjacent indexes is the left one. `left = mid` then sticks. The upper midpoint is the right one.
- **Lower bound and upper bound** — the first index greater than or equal to the target, and the first index strictly greater. Both use `[0, n)` and a lower midpoint. The last index at most the target is the upper bound minus one, and the direct loop uses an upper midpoint. `bisect_left` and `bisect_right` match the two half-open searches.
- **A monotone predicate, searched for the boundary** — the first true value uses the lower-bound loop. The last true value is the first false minus one, or a loop that sets `left = mid`. Versions 1 through 16 with the first bad version at 11 return 11 after 4 calls. LeetCode 278 allows `n` at the top of a signed 32-bit integer. The end `n + 1` does not fit in that type. The loop that fits keeps `right` at `n` because a bad version is guaranteed.
- **The index where a value would be inserted (LeetCode-style: Search Insert Position)** — the lower bound, including `n`. A target past the last value of `[2, 6, 10, 14, 18]` returns 5. LeetCode 35 promises distinct values and a length of at least 1. This function also returns 0 for an empty list.
- **The first and last index of a value (LeetCode-style: Find First and Last Position of Element in Sorted Array)** — two bounds. The run of 6 in `[4, 6, 6, 6, 8, 10]` is `[1, 3]`. An absent target is `[-1, -1]`. Expanding from one hit is linear on an all-equal list. LeetCode 34 allows an empty list.
- **The highest blade that still yields the wood** — wood only shrinks as the blade rises, so the answer is the last true height, with an upper midpoint. Trunks `[8, 12, 6, 15]` and a requirement of 10 return blade 8, which yields 11. A requirement above the total returns -1. The checks cost O(n log (M + 1)), plus a linear pass to find the tallest trunk. The lower midpoint sticks on the last two heights. LeetCode 875 searches a speed with a different check.
- **A target in a rotated sorted array (LeetCode-style: Search in Rotated Sorted Array)** — one side of the midpoint is sorted when the values are distinct. The test is `<=`, because the midpoint can be the left index. A strict `<` misses 1 in `[3, 1]`. Duplicates can hide the target: `[2, 3, 2, 2, 2]` misses 3. LeetCode 33 requires distinct values. Its stated pivot starts at 1, and the array is only possibly rotated, so the unrotated array is still in the contract. LeetCode 81 does not require distinct values, and the worst case is linear.
- **The median of two sorted arrays (LeetCode-style: Median of Two Sorted Arrays)** — binary-search a cut in the shorter array so the left half holds `(m + n + 1) // 2` values and each left edge is at most the other right edge. Empty sides of the cut compare as infinity. `[2, 6, 10]` and `[3, 7]` have median 6.0. A cut of 0 on the longer of `[1, 4, 8]` and `[2, 6]` asks the shorter array for index 3. The swap keeps the partner index in range. The merge is the O(m + n) baseline. LeetCode 4 allows either array to be empty.
- **A matrix sorted in row-major order (LeetCode-style: Search a 2D Matrix)** — flat index `i` is row `i // cols` and column `i % cols`. Using the row count as the stride reports 16 absent on the 3 by 4 exercise matrix. When only rows and columns are sorted, the flat search for 8 first keeps index 5, where 8 sits. The next midpoint is the value 3, and that comparison discards index 5. A top-right staircase finds 8. LeetCode 74 is the flat search. LeetCode 240 is the staircase.
- **Any index that is a local peak (LeetCode-style: Find Peak Element)** — a rise keeps the right side, and a fall keeps the midpoint and the left side. Outside neighbors count as smaller. `[2, 6, 8, 5, 1]` peaks at index 2. Several peaks make any of them legal. Equal neighbors are outside the contract. LeetCode 162 starts at one element.
- **A pick whose chance follows the weight (LeetCode-style: Random Pick with Weight)** — prefix totals, then a lower bound. Draws 1 through 10 on weights `[4, 1, 5]` hit indexes with counts 4, 1, and 5. Draws 0 through 9 steal one outcome from the last weight. A zero total is not a draw. LeetCode 528 requires positive weights. CPython 3.12's `random.choices` uses a float draw and a capped `bisect`.
- **What to run before you trust the loop** — empty, one element, two elements, all equal, absent below and above and between, both ends, and every cut of a short rotated array. Compare bounds with `bisect`. The exercise checker on that set reports 0 mismatches.

## Example

```python
import bisect


def insert_index(values: list[int], target: int) -> int:
    left, right = 0, len(values)
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left


def first_greater(values: list[int], target: int) -> int:
    left, right = 0, len(values)
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] <= target:
            left = mid + 1
        else:
            right = mid
    return left


def wood_above(heights: list[int], blade: int) -> int:
    return sum(max(height - blade, 0) for height in heights)


def highest_blade(heights: list[int], need: int) -> int:
    if not heights:
        return -1
    if need <= 0:
        return max(heights)
    if wood_above(heights, 0) < need:
        return -1
    left, right = 0, max(heights)
    while left < right:
        mid = left + (right - left + 1) // 2
        if wood_above(heights, mid) >= need:
            left = mid
        else:
            right = mid - 1
    return left


pages = [2, 6, 10, 14, 18]
print(insert_index(pages, 7), bisect.bisect_left(pages, 7))
print(insert_index(pages, 20), first_greater([4, 6, 6, 6, 8, 10], 6) - 1)
print(highest_blade([8, 12, 6, 15], 10), wood_above([8, 12, 6, 15], 8))
# 2 2
# 5 3
# 8 11
```

The insertion index is a lower bound, and `bisect_left` agrees. The last 6 in the second list is one before the first strictly greater value. The blade search uses the upper midpoint because a feasible height moves the left edge onto the midpoint. The lists are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the search space, the cost, and a Python check. None of them is a published problem from a book list.
