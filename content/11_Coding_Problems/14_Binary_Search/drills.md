# Binary Search — Drills

Original drills for the four decisions, a rotated minimum, a search on a feasible speed, a predicate count, an insertion interval that stops one short, a matrix that is not one sorted sequence, a weighted draw, a peak trace, and a rotated array whose duplicates hide the sorted half. Each answer has an approach, a cost, and Python. The lists are exercise inputs, not measured data. None of these repeats the never-ending lower bound, the sorted-total count, the integer square root, the split across D days, or the smallest daily capacity already in the pattern catalog.

## The four decisions for the last index

For the last index whose value is less than or equal to the target, write the search space, the narrowing rule, the exit test, and the return value. Then run that loop on the exercise list `[8, 8, 11, 15, 15, 20]` for targets 15, 7, 20, and 12. What do an empty list, a single 8 against a target of 8, and a single 8 against a target of 9 return?

**Answer:** The search space is the closed interval from -1 through `n - 1`. The answer -1 means every value is greater than the target. The midpoint is the upper one, `left + (right - left + 1) // 2`. When `values[mid]` is at most the target, `left` becomes `mid`, because that index might be the last feasible one. Otherwise `right` becomes `mid - 1` and `mid` is excluded. The loop stops when `left == right`, which is the test `while left < right`. The return value is `left`. On the exercise list the last index at most 15 is 4, at most 7 is -1, at most 20 is 5, and at most 12 is 2, the 11. An empty list returns -1. A single 8 returns 0 for both a matching target and a larger target, because 8 is at most 9. `bisect_right(target) - 1` is the same index. The loop is O(log n) time and O(1) extra memory. The [Lower and upper bound](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card names the upper bound as the first index strictly greater than the target. This drill returns that index minus one, directly.

```python
import bisect


def last_at_most(values: list[int], target: int) -> int:
    left, right = -1, len(values) - 1
    while left < right:
        mid = left + (right - left + 1) // 2
        if values[mid] <= target:
            left = mid
        else:
            right = mid - 1
    return left


data = [8, 8, 11, 15, 15, 20]
print(last_at_most(data, 15), bisect.bisect_right(data, 15) - 1)
print(last_at_most(data, 7), last_at_most(data, 20), last_at_most(data, 12))
print(last_at_most([], 15), last_at_most([8], 8), last_at_most([8], 9))
# 4 4
# -1 5 2
# -1 0 0
```

## The minimum after a rotation

The exercise list `[6, 8, 11, 2, 3, 4]` is a sorted list of distinct values, cut and restacked. Return the minimum value. Also return the minimum of the unrotated list `[2, 3, 4, 6, 8, 11]`, of every cut of that list, of `[13]`, of `[6, 1]`, and of `[1, 6]`.

**Answer:** Compare the midpoint with the right end. When `values[mid]` is greater than `values[right]`, the drop that holds the minimum is to the right of `mid`, so `left` becomes `mid + 1`. Otherwise the minimum is at `mid` or to its left, so `right` becomes `mid`. The lower midpoint is safe because the rising branch excludes `mid` and the falling branch keeps it. The first midpoint of `[6, 8, 11, 2, 3, 4]` is index 2, value 11, which is greater than the right end 4, so the left edge moves to 3. The next midpoint is index 4, value 3, which is not greater than 4, so the right edge moves to 4. Then index 3, value 2, is not greater than 3, and the right edge meets the left edge at 3. The minimum is 2. An unrotated list keeps moving the right edge left until index 0. Every cut of `[2, 3, 4, 6, 8, 11]` has minimum 2. A single 13 is 13. `[6, 1]` drops across the midpoint, so the minimum is the right value, 1. `[1, 6]` does not drop, so the minimum is the left value, 1. The time is O(log n) and the extra memory is O(1). LeetCode 153, Find Minimum in Rotated Sorted Array, returns this value for distinct values, length 1 through 5000, and values from -5000 through 5000. Its rotations include the unrotated array, because a list can be rotated `n` times. LeetCode 154 allows duplicates, and the comparison with the right end no longer tells you which side holds the minimum. On the exercise list `[2, 2, 2, 0, 2]` the same loop returns 2. The minimum is 0, at index 3. The first midpoint is index 2. Its value equals the right end, so `values[mid] > values[right]` fails and the right edge moves to 2. Indexes 3 and 4, including the 0, are discarded. The loop still terminates: the lower midpoint either steps `left` past `mid` or moves `right` onto `mid`. It returns the wrong value. The distinct cuts above are the contract this drill solves. The [Rotated sorted array](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card searches for a target. This drill searches for the cut.

```python
def find_min(values: list[int]) -> int:
    left, right = 0, len(values) - 1
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] > values[right]:
            left = mid + 1
        else:
            right = mid
    return values[left]


base = [2, 3, 4, 6, 8, 11]
print(find_min([6, 8, 11, 2, 3, 4]))
print(find_min(base))
print([find_min(base[k:] + base[:k]) for k in range(len(base))])
print(find_min([13]), find_min([6, 1]), find_min([1, 6]))
print(find_min([2, 2, 2, 0, 2]), min([2, 2, 2, 0, 2]))
# 2
# 2
# [2, 2, 2, 2, 2, 2]
# 13 1 1
# 2 0
```

## The slowest speed that finishes in time

The exercise piles are `[5, 8, 10]`. In one hour a worker finishes `speed` items from a single pile and does not start another pile in that hour. A pile of 5 at speed 4 takes two hours, because the second hour finishes the remainder. What is the slowest integer speed that finishes all three piles within 6 hours? Also answer 3 hours, 2 hours, and 100 hours.

**Answer:** If a speed finishes in time, every faster speed does too, so the predicate flips once and the answer is the first true speed. The range is 1 through the largest pile. The check sums `ceil(pile / speed)` over the piles, which for positive integers is `(pile + speed - 1) // speed`. Speed 4 takes 2 + 2 + 3 = 7 hours, which misses 6. Speed 5 takes 1 + 2 + 2 = 5 hours, which fits. The loop returns 5. Three hours is one hour per pile, so the speed is the largest pile, 10. Two hours is fewer than the three piles, and each pile costs at least one hour, so no speed works and the function returns -1. One hundred hours is enough for speed 1, which takes 23 hours. The time is O(n log M + n) when the largest pile M is at least 1. The linear term finds that pile, including when every pile is 1 and the search range is a single speed. The extra memory is O(1). LeetCode 875, Koko Eating Bananas, is this speed. Its length is from 1 through 10^4, each pile is from 1 through 10^9, and the hour limit is from the number of piles through 10^9, so two hours on three piles is outside that contract. The hour sum can exceed a 32-bit integer when the piles are at the top of that contract. Python's `int` does not wrap. The published samples use different piles. The [Binary search on the answer](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card is the first-true loop. The capacity drills on that topic and on the pattern page split a sequence into days. This drill is a per-pile ceiling.

```python
def hours_needed(piles: list[int], speed: int) -> int:
    return sum((pile + speed - 1) // speed for pile in piles)


def min_speed(piles: list[int], hours: int) -> int:
    if not piles or hours < len(piles):
        return -1
    left, right = 1, max(piles)
    while left < right:
        mid = left + (right - left) // 2
        if hours_needed(piles, mid) <= hours:
            right = mid
        else:
            left = mid + 1
    return left


print(min_speed([5, 8, 10], 6))
print(hours_needed([5, 8, 10], 4), hours_needed([5, 8, 10], 5))
print(min_speed([5, 8, 10], 3), min_speed([5, 8, 10], 2), min_speed([5, 8, 10], 100))
# 5
# 7 5
# 10 -1 1
```

## The first bad build in a thousand versions

Versions 1 through 1000 are exercise build numbers. A version is bad when it is at least 700, and every later version stays bad. How many times does the predicate run before the loop returns 700? How many times does it run when the first bad version is 501, when it is 1, and when it is 1000?

**Answer:** This is the first-true search on `[1, 1001)`. A bad midpoint might be the first bad version, so the right edge moves onto it. A good midpoint is excluded by moving the left edge to `mid + 1`. The lower midpoint is the one that matches those updates. The first bad version 700 takes 10 predicate calls. The midpoints are 501, 751, 626, 689, 720, 705, 697, 701, 699, and 700. Version 501 takes 9 calls. Versions 1 and 1000 take 10. Across every first-bad version from 1 through 1000, 22 answers take 9 calls and the other 978 take 10. The block prints that midpoint list and those two counts. The cost stays logarithmic, and it is not the same count for every answer. The extra memory is O(1). `git bisect` is this walk on a line of commits: you mark the checked-out commit good or bad, and the remaining range is the commits that can still be the first bad one. LeetCode 278, First Bad Version, is the same predicate. Its `n` can be 2147483647, so a 32-bit midpoint has to be `left + (right - left) // 2`. The half-open end used here is `n + 1`. When `n` is 2147483647 that end does not fit in a signed 32-bit integer, so the loop that fits keeps `right` at `n` and still uses the lower midpoint. This drill's `n` is 1000, and the predicate reads a known threshold so the call count can be checked. The [Binary search on answer](../../07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/) card uses the same loop on a different predicate.

```python
def first_bad(n: int, bad_at: int) -> tuple[int, int]:
    calls = 0

    def is_bad(version: int) -> bool:
        nonlocal calls
        calls += 1
        return version >= bad_at

    left, right = 1, n + 1
    while left < right:
        mid = left + (right - left) // 2
        if is_bad(mid):
            right = mid
        else:
            left = mid + 1
    return left, calls


def midpoints(n: int, bad_at: int) -> list[int]:
    seen: list[int] = []
    left, right = 1, n + 1
    while left < right:
        mid = left + (right - left) // 2
        seen.append(mid)
        if mid >= bad_at:
            right = mid
        else:
            left = mid + 1
    return seen


print(first_bad(1000, 700))
print(first_bad(1000, 501))
print(first_bad(1000, 1), first_bad(1000, 1000))
print(midpoints(1000, 700))
counts = [first_bad(1000, bad)[1] for bad in range(1, 1001)]
print(counts.count(9), counts.count(10))
# (700, 10)
# (501, 9)
# (1, 10) (1000, 10)
# [501, 751, 626, 689, 720, 705, 697, 701, 699, 700]
# 22 978
```

## The insertion index that cannot land past the end

This insertion search sets the right edge to `n - 1` and stops when the two edges meet. On the exercise list `[3, 5, 9]` and a target of 12 it returns 2. The insertion index is 3. Why does the loop miss, and what does the same function return for a target of 4? What do the repaired half-open search and this loop return for a single `[8]` and a target of 9?

```python
def insert_closed(values: list[int], target: int) -> int:
    if not values:
        return 0
    left, right = 0, len(values) - 1
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left
```

**Answer:** The interval is `[0, n - 1]`. The index `n` is not a candidate, so a target greater than every value cannot be returned. On `[3, 5, 9]` and a target of 12 the only step sets `left` to 2, the edges meet, and the function returns 2 without ever asking whether 9 is still too small. The value at that index is less than the target. A target of 4 belongs at index 1, in front of 5, and that index is inside the interval, so the same loop returns 1. The repair is the half-open interval `[0, n)`. It excludes index 2 when 9 is too small and returns 3. On `[8]` and a target of 9 the closed loop never enters, because the edges already meet at 0, and it returns 0. The half-open loop returns 1. An empty list happens to return 0 from either start, because there is no index to misread. The repaired search is O(log n) time and O(1) extra memory. LeetCode 35, Search Insert Position, includes the slot after the last value and starts at length 1. The [Bug hunt: binary search never ends](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) drill sticks by assigning an edge to `mid`. This bug terminates and returns the wrong index.

```python
import bisect


def insert_closed(values: list[int], target: int) -> int:
    if not values:
        return 0
    left, right = 0, len(values) - 1
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left


def insert_index(values: list[int], target: int) -> int:
    left, right = 0, len(values)
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left


print(insert_closed([3, 5, 9], 12), insert_index([3, 5, 9], 12), bisect.bisect_left([3, 5, 9], 12))
print(insert_closed([3, 5, 9], 4), insert_index([3, 5, 9], 4))
print(insert_closed([8], 9), insert_index([8], 9))
print(insert_closed([], 4), insert_index([], 4))
# 2 3 3
# 1 1
# 0 1
# 0 0
```

## A matrix binary search that walks off the sorted order

The exercise matrix below has every row and every column sorted. It is not one sorted sequence in row-major order, because 10 is followed by 3. A flattened binary search for 3 returns -1. A staircase walk finds 3. What does each method return for 11?

```text
2  6  10
3  7  12
4  8  13
```

**Answer:** The flat list is `[2, 6, 10, 3, 7, 12, 4, 8, 13]`. The first midpoint is index 4, value 7, which is greater than 3, so the search steps left. The next midpoint is index 1, value 6, still greater, so the right edge moves to 0. The last step sees 2 and steps right into an empty interval. Index 3, which holds 3, was discarded because a larger value sat to its right in a list that is not sorted. The staircase starts at the top-right 10. 10 is greater than 3, and the column below it is larger still, so the walk steps left to 6, then left to 2. 2 is smaller than 3, and the row to its left is smaller still, so the walk steps down onto 3. A target of 11 is absent from the matrix. The flat search returns -1, and the staircase also returns false: 10 steps down to 12, 12 steps left to 7, and 7 steps down through 8 and off the bottom. The flat search is not a correct algorithm on this promise, so its -1 is not evidence. The staircase is O(rows + cols) and uses constant extra memory. LeetCode 240, Search a 2D Matrix II, is this promise. LeetCode 74, Search a 2D Matrix, adds the promise that the next row starts after the previous row ends, which this matrix does not have. The concept card shows the same miss for a different matrix and the target 8.

```python
def flatten_search(matrix: list[list[int]], target: int) -> int:
    flat = [value for row in matrix for value in row]
    left, right = 0, len(flat) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if flat[mid] == target:
            return mid
        if flat[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def staircase(matrix: list[list[int]], target: int) -> bool:
    row, col = 0, len(matrix[0]) - 1
    while row < len(matrix) and col >= 0:
        value = matrix[row][col]
        if value == target:
            return True
        if value > target:
            col -= 1
        else:
            row += 1
    return False


matrix = [
    [2, 6, 10],
    [3, 7, 12],
    [4, 8, 13],
]
print(flatten_search(matrix, 3), staircase(matrix, 3))
print(flatten_search(matrix, 11), staircase(matrix, 11))
# -1 True
# -1 False
```

## Which weight the draw lands in

The exercise weights are `[3, 6, 1]`. Build the prefix totals. For each integer draw from 1 through the total, which index wins? How many draws does each index receive?

**Answer:** The prefix is `[3, 9, 10]`. A draw in 1 through the total lands on the first prefix greater than or equal to the draw. Draws 1, 2, and 3 land on index 0. Draws 4 through 9 land on index 1. Draw 10 lands on index 2. The counts are 3, 6, and 1, which are the weights. The setup is O(n) time and O(n) extra memory. Each draw is O(log n). A linear scan of the prefix is the check for a total this small. A zero weight would not advance the prefix and would receive no draws. This list has none. LeetCode 528, Random Pick with Weight, requires every weight to be at least 1 and draws at random, so a checker looks at frequencies rather than at one sequence. The map below is every integer draw, in order. The [Prefix sums](../06_Moderate_Problems/) card is the array this search reads.

```python
def prefix_of(weights: list[int]) -> list[int]:
    totals: list[int] = []
    running = 0
    for weight in weights:
        running += weight
        totals.append(running)
    return totals


def index_for(prefix: list[int], draw: int) -> int:
    left, right = 0, len(prefix)
    while left < right:
        mid = left + (right - left) // 2
        if prefix[mid] < draw:
            left = mid + 1
        else:
            right = mid
    return left


prefix = prefix_of([3, 6, 1])
picks = [index_for(prefix, draw) for draw in range(1, prefix[-1] + 1)]
print(prefix)
print(picks)
print([picks.count(i) for i in range(len(prefix))])
# [3, 9, 10]
# [0, 0, 0, 1, 1, 1, 1, 1, 1, 2]
# [3, 6, 1]
```

## The half a peak search throws away

On the exercise list `[3, 5, 4, 2, 1]`, adjacent values differ. Walk the peak search. At each step, name the midpoint, which side you discard, and why a peak remains in the side you keep. Which index does the loop return?

**Answer:** The outside neighbor of an endpoint counts as smaller, so a peak exists. The first midpoint is index 2, value 4, and the next value is 2. The slope falls, so a peak remains at index 2 or to its left, and indexes 3 and 4 are discarded. The next midpoint is index 1, value 5, and the next value is 4. The slope falls again, so index 2 is discarded and the interval is `[0, 1]`. The next midpoint is index 0, value 3, and the next value is 5. The slope rises, so index 0 is not a peak and the left edge moves to 1. The only remaining index is 1. The value 5 is greater than 3 and greater than 4. The first step discards indexes 3 and 4. That discard is safe because the slope falls, so a peak remains at index 2 or to its left. Discarding the left side on that same step would drop the peak at index 1. The time is O(log n) and the extra memory is O(1). LeetCode 162, Find Peak Element, returns any peak, requires distinct neighbors, and starts at one element. This list has one peak. A linear scan that returns the first index greater than its right neighbor is the check, and it also returns 1.

```python
def peak_trace(values: list[int]) -> tuple[list[tuple[int, str, int, int]], int]:
    left, right = 0, len(values) - 1
    steps: list[tuple[int, str, int, int]] = []
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] < values[mid + 1]:
            steps.append((mid, "right", mid + 1, right))
            left = mid + 1
        else:
            steps.append((mid, "left", left, mid))
            right = mid
    return steps, left


print(peak_trace([3, 5, 4, 2, 1]))
# ([(2, 'left', 0, 2), (1, 'left', 0, 1), (0, 'right', 1, 1)], 1)
```

## Repeated values hide the sorted half

The distinct-value rotated search treats a side as sorted when its left end is less than or equal to the midpoint. On the exercise list `[4, 1, 4, 4, 4]` it returns -1 for the target 1. The value is present. Which comparison called a side sorted, and where does a linear scan find 1?

**Answer:** The list is `[1, 4, 4, 4, 4]` cut so that 1 sits at index 1. The first midpoint is index 2. Both `values[0]` and `values[2]` are 4, so `4 <= 4` calls indexes 0 through 2 sorted. That slice is `[4, 1, 4]`, which is not sorted, and 1 sits inside it. The target is not in the range `[4, 4)`, so the search steps right and then sees only 4s. It returns -1. A linear scan returns index 1. A target of 4 is present in several cells. The same loop happens to stop on the midpoint, index 2, because that cell equals 4. A linear scan returns the first 4, at index 0. The miss is the value hidden in the side the equal ends called sorted, not every value in the list. An absent 0 returns -1 from both. Equal ends are why the logarithmic worst case is gone: the comparison no longer proves which side is sorted, and shrinking one index at a time is O(n). LeetCode 33, Search in Rotated Sorted Array, promises distinct values, so this list is outside that contract. LeetCode 81, Search in Rotated Sorted Array II, allows the duplicates and asks you to notice the bound. The concept card misses 3 in `[2, 3, 2, 2, 2]` for the same reason. This drill is a different list. The [Rotated sorted array](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card names the same fallback.

```python
def search_rotated(values: list[int], target: int) -> int:
    left, right = 0, len(values) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if values[mid] == target:
            return mid
        if values[left] <= values[mid]:
            if values[left] <= target < values[mid]:
                right = mid - 1
            else:
                left = mid + 1
        elif values[mid] < target <= values[right]:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def linear_index(values: list[int], target: int) -> int:
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


print(search_rotated([4, 1, 4, 4, 4], 1), linear_index([4, 1, 4, 4, 4], 1))
print(search_rotated([4, 1, 4, 4, 4], 4), linear_index([4, 1, 4, 4, 4], 4))
print(search_rotated([4, 1, 4, 4, 4], 0), linear_index([4, 1, 4, 4, 4], 0))
# -1 1
# 2 0
# -1 -1
```
