# Binary Search

Binary search discards half of an ordered set of candidates after one check. The candidates may be indexes in a sorted array, the integers in a range whose feasibility flips once, or the cut in a shorter sorted array. The loop is four decisions: the search space, which side of the midpoint is discarded, when the loop stops, and what is returned. A lower midpoint is safe when a kept left side excludes the midpoint. An upper midpoint is required when a feasible midpoint becomes the new left edge. These notes are the decisions, the bounds, and the checks. They are not a catalog of published problems.

## Key Points

- **Binary search** — one comparison discards the side that cannot hold the answer. `git bisect` keeps the commits reachable from a bad commit and not from a good one. Straight history halves, and several parents make the remainder a graph. `bisect_left` returns an insertion index and does not ask whether the value is present. PostgreSQL's `_bt_binsrch` binary-searches the keys on one B-tree page. The iterative loop is logarithmic and uses constant extra memory. A hash set does not return an insertion index, a run's ends, or the smallest feasible value. Sorted arrays, numeric ranges, rotated arrays, two sorted arrays, and matrices are the five shapes below.
- **Exact match in a sorted array** — the space, the narrowing, the exit, and the return. The interval is closed, every miss excludes the midpoint, and the loop ends when `left > right`. If the target occurs, its index is still inside `[left, right]`. An empty interval returns -1. Assigning an edge to `mid` under `while left <= right` stops shrinking. Excluding `mid` on both sides of `while left < right` can skip the last candidate.
- **Lower and upper bound** — the first index greater than or equal to the target, and the first index strictly greater. Both use `[0, n)` and a lower midpoint, and the answer stays in `[left, right)` until the edges meet. The meeting index is the insertion point, including `n`. The last index at most the target is the upper bound minus one, and the direct loop uses an upper midpoint. `left + (right - left) // 2` stays in range for nonnegative endpoints that fit. Adding 1500000000 and 1500000020 wraps, in a language that wraps, to a negative midpoint. `left = mid` with the lower midpoint sticks. Empty, one cell, two cells, equals, and targets below, between, and above agree with `bisect`. Using -1 as an index reads the last cell.
- **First and last index of a value** — two bounds. The run of 6 in `[4, 6, 6, 6, 8, 10]` is `[1, 3]`. An absent target is `[-1, -1]`. Read the lower bound only when it is still an index. Expanding from one hit is linear on an all-equal list. Subtracting one from a loop that already returns the last index shifts the end. LeetCode 34 allows an empty list.
- **Smallest value that passes a monotone test** — the predicate is false on one side of a threshold and true on the other. A second flip drops a real answer. The first true value lies in `[left, right)` and uses the lower midpoint. The last true value is the first false minus one, or a loop that sets `left = mid`. Versions 1 through 16 with the first bad version at 11 return 11 after 4 calls. LeetCode 278 allows `n` at the top of a signed 32-bit integer. The end `n + 1` does not fit in that type. The loop that fits keeps `right` at `n` because a bad version is guaranteed.
- **Largest cut height that still yields enough** — wood only shrinks as the blade rises, so the answer is the last true height, with an upper midpoint. Trunks `[8, 12, 6, 15]` sum to 41, and a requirement of 10 returns blade 8, which yields 11. A requirement above the total returns -1. The first height that works is 0 whenever 0 already works. The checks cost O(n log (M + 1)), plus a linear pass to find the tallest trunk. The lower midpoint sticks on the last two heights. The dangerous add is inside the predicate. LeetCode 875 searches a speed with a different check.
- **Search a rotated sorted array** — one side of the midpoint is sorted when the values are distinct. The test is `<=`, because the midpoint can be the left index. A strict `<` misses 1 in `[3, 1]`. Duplicates can hide the target: `[2, 3, 2, 2, 2]` misses 3. On distinct values the minimum compares the midpoint with the right end. `[2, 2, 2, 0, 2]` makes that minimum loop return 2. LeetCode 33 requires distinct values and allows the unrotated array. LeetCode 81 does not require distinct values, and the worst case is linear. Every cut of `[10, 20, 30, 40]` agrees with a scan and with `min`.
- **Median of two sorted arrays** — binary-search a cut in the shorter array so the left half holds `(m + n + 1) // 2` values and each left edge is at most the other right edge. With the shorter length `m` at most `n`, the partner index `j` stays in `0` through `n`. Empty sides of the cut compare as infinity. `[2, 6, 10]` and `[3, 7]` have median 6.0. A cut of 0 on the longer of `[1, 4, 8]` and `[2, 6]` asks the shorter array for index 3. The swap keeps the partner index in range. Each step excludes the cut. An unsorted pair can return the wrong median: `[1, 3]` and `[4, 2]` give 3.5, not 2.5. The merge is the O(m + n) baseline. LeetCode 4 allows either array to be empty.
- **Search a row-major matrix** — flat index `i` is row `i // cols` and column `i % cols`. Using the row count as the stride reports 16 absent on the 3 by 4 exercise matrix. When only rows and columns are sorted, the flat search for 8 first keeps index 5. The next midpoint is index 6, value 3, and that comparison discards index 5. A top-right staircase finds 8. LeetCode 74 is the flat search. LeetCode 240 is the staircase.
- **Any index greater than its neighbors** — a rise keeps the right side, and a fall keeps the midpoint and the left side. Walking uphill reaches a descent or the end, so a peak remains. The maximum on a falling side is a peak because that side steps down at its right edge. Outside neighbors count as smaller. `[2, 6, 8, 5, 1]` peaks at index 2. Several peaks make any of them legal. Equal neighbors are outside the contract. LeetCode 162 starts at one element.
- **Random pick by weight** — prefix totals, then a lower bound. Setup is O(n) time and O(n) memory. Draws 1 through 10 on weights `[4, 1, 5]` hit indexes with counts 4, 1, and 5. Draws 0 through 9 steal one outcome from the last weight. A zero weight is skipped. A zero total is not a draw. A negative weight breaks the non-decreasing prefix. LeetCode 528 requires positive weights. CPython 3.12's `random.choices` uses a float draw and a capped `bisect`.

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
