# Sorting and Searching — Drills

Original mini-drills for choosing sorts, partitioning, stability, and binary search boundaries. Each card is one exercise: read the prompt and snippet, commit to an answer, then check it. Each Answer has a short Python solution that runs on its own. No copyrighted book text.

## Pick the sort

A sensor log of 200 readings arrives already sorted by time except that a handful of readings are a few slots out of place. You must sort it in place with O(1) extra memory. Which of bubble, insertion, merge, or quick sort fits best, and why?

**Answer:** Insertion sort. Its cost is O(N + I) where I is the number of inversions (out-of-order pairs), and a nearly sorted log has only a few, so it runs in close to linear time with O(1) space. Merge sort needs O(N) extra memory, and quick sort does O(N log N) work no matter how ordered the input already is. The demo counts shifts to show how little insertion sort moves.

```python
def insertion_sort_shifts(arr: list[int]) -> int:
    """Sort arr in place and return how many element shifts it took."""
    shifts = 0
    for i in range(1, len(arr)):
        key, j = arr[i], i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
            shifts += 1
        arr[j + 1] = key
    return shifts

nearly = list(range(200))
nearly[10], nearly[11] = nearly[11], nearly[10]
nearly[150], nearly[152] = nearly[152], nearly[150]
print(insertion_sort_shifts(nearly), nearly == sorted(nearly))  # 4 True
print(insertion_sort_shifts(list(range(200, 0, -1))))  # 19900
```

## Turtles in bubble sort

Bubble sort (with the early exit on a pass that makes no swaps) is run on `[2, 3, 4, 5, 6, 1]`. How many passes does it make? What if the input is `[6, 1, 2, 3, 4, 5]`?

**Answer:** A large value near the front moves all the way to the end in one pass, but a small value near the back moves only one slot left per pass. In `[2, 3, 4, 5, 6, 1]` the 1 moves one slot left in each of passes 1 to 5, and the outer loop still runs its sixth pass, so 6 passes in total (the maximum). `[6, 1, 2, 3, 4, 5]` is sorted after pass 1, and pass 2 sees no swaps and exits early. Slow-moving small values ("turtles") are why bubble sort is so sensitive to where disorder sits.

```python
def bubble_passes(arr: list[int]) -> int:
    n, passes = len(arr), 0
    for i in range(n):
        passes += 1
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return passes

print(bubble_passes([2, 3, 4, 5, 6, 1]))  # 6
print(bubble_passes([6, 1, 2, 3, 4, 5]))  # 2
```

## Bug hunt: unstable merge

Records `(score, name)` are sorted by score with this merge sort, and records with equal scores come out in a different order than they went in. Find the one-character bug.

```python
def merge(left, right):
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i][0] < right[j][0]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]
```

**Answer:** On a tie the `else` branch takes from the right half first, so an equal record that started later jumps ahead of one that started earlier. Use `<=` so ties prefer the left half. That single comparison is what makes merge sort stable.

```python
def merge(left, right):
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i][0] <= right[j][0]:    # ties take from the left: stable
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]

def merge_sort(xs):
    if len(xs) <= 1:
        return xs
    mid = len(xs) // 2
    return merge(merge_sort(xs[:mid]), merge_sort(xs[mid:]))

rows = [(2, "ana"), (1, "bo"), (2, "cy"), (1, "di")]
print(merge_sort(rows))  # [(1, 'bo'), (1, 'di'), (2, 'ana'), (2, 'cy')]
```

## Sorted input, last-element pivot

A quick sort always takes the last element of the range as the pivot (Lomuto). Roughly how many comparisons does it make on an already sorted array of 1,000 items versus a shuffled one, and what is the one-line fix?

**Answer:** On sorted input the last element is the maximum, so every partition peels off just one element: (N-1) + (N-2) + ... = N(N-1)/2 ≈ 500,000 comparisons, and the recursion goes N deep. A shuffled array splits roughly in half each time, about 1.39·N·log2 N ≈ 11,000 to 14,000 comparisons. Swap a random element into the last slot before partitioning and the sorted case behaves like the shuffled one.

```python
import random

def quicksort_count(arr: list[int], randomize: bool) -> int:
    comparisons, stack = 0, [(0, len(arr) - 1)]   # explicit stack avoids deep recursion
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        if randomize:
            p = random.randint(lo, hi)
            arr[p], arr[hi] = arr[hi], arr[p]
        pivot, i = arr[hi], lo
        for j in range(lo, hi):
            comparisons += 1
            if arr[j] < pivot:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
        arr[i], arr[hi] = arr[hi], arr[i]
        stack += [(lo, i - 1), (i + 1, hi)]
    return comparisons

print(quicksort_count(list(range(1000)), randomize=False))  # 499500
print(quicksort_count(list(range(1000)), randomize=True) < 20000)  # True
```

## Is selection sort stable?

Selection sort is run on `[(2, "a"), (2, "b"), (1, "c")]`, comparing only the number. Show the result and say whether selection sort is stable.

**Answer:** The first pass finds `(1, "c")` as the minimum and swaps it with the element at index 0, which is `(2, "a")`. That long-distance swap throws `(2, "a")` behind `(2, "b")`, so the output is `[(1, 'c'), (2, 'b'), (2, 'a')]`: the two 2s swapped relative order. Selection sort is not stable; a single counterexample is enough to prove it.

```python
def selection_sort(arr: list[tuple[int, str]]) -> None:
    for i in range(len(arr)):
        m = min(range(i, len(arr)), key=lambda k: arr[k][0])
        arr[i], arr[m] = arr[m], arr[i]

rows = [(2, "a"), (2, "b"), (1, "c")]
selection_sort(rows)
print(rows)  # [(1, 'c'), (2, 'b'), (2, 'a')]
```

## Six comparisons for five items

A colleague claims a clever comparison sort that orders any 5 distinct values using at most 6 comparisons. Without seeing the code, show that the claim is impossible, and give the minimum worst-case comparisons the bound allows.

**Answer:** Each comparison has two outcomes, so 6 comparisons can distinguish at most 2^6 = 64 cases, but 5 distinct values can arrive in 5! = 120 orders, and each order needs a different rearrangement. Some two inputs would get the same treatment, so one of them ends up unsorted. The bound is ceil(log2(N!)) comparisons in the worst case: 7 for N = 5. The same counting gives log2(N!) ≈ N log2 N for large N, which is the comparison sort lower bound.

```python
import math

def min_comparisons(n: int) -> int:
    return math.ceil(math.log2(math.factorial(n)))

print(2 ** 6, math.factorial(5))  # 64 120
print([min_comparisons(n) for n in range(1, 9)])  # [0, 1, 3, 5, 7, 10, 13, 16]
```

## Bug hunt: binary search never ends

This search for the first index with `arr[i] >= target` hangs on some inputs. Find an input that hangs and fix it.

```python
def first_at_least(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid
        else:
            hi = mid
    return lo
```

**Answer:** With two elements left, `mid` rounds down to `lo`; if `arr[mid] < target` then `lo = mid` changes nothing and the loop spins forever (for example `arr = [1, 3]`, `target = 3`). Every branch must shrink the range: since `arr[mid] < target` rules `mid` out, set `lo = mid + 1`. Using a half-open `hi = len(arr)` also lets the function return `len(arr)` when every value is smaller than the target.

```python
def first_at_least(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1      # mid is ruled out
        else:
            hi = mid          # mid may be the answer
    return lo

print(first_at_least([1, 3], 3))  # 1
print(first_at_least([1, 3, 3, 8], 4))  # 3
print(first_at_least([1, 3], 9))  # 2
```

## Count in a sorted array

A sorted list holds a million order totals in cents. How do you count how many orders are exactly 1999 cents, and how many fall in the range 1000 to 4999 inclusive, both in O(log N)?

**Answer:** Two boundary searches answer both. The count of a value is `bisect_right(x) - bisect_left(x)`. A closed range `[a, b]` holds `bisect_right(b) - bisect_left(a)` items. No scan is needed because the boundaries alone tell you how many items lie between them.

```python
from bisect import bisect_left, bisect_right

totals = [500, 999, 1000, 1999, 1999, 1999, 2500, 4999, 5000, 7200]

def count_value(xs: list[int], x: int) -> int:
    return bisect_right(xs, x) - bisect_left(xs, x)

def count_range(xs: list[int], a: int, b: int) -> int:
    return bisect_right(xs, b) - bisect_left(xs, a)

print(count_value(totals, 1999))  # 3
print(count_range(totals, 1000, 4999))  # 6
print(count_value(totals, 1234))  # 0
```

## Integer square root

Without `math.isqrt` or floating point, return the largest integer `r` with `r * r <= n` for any `n >= 0`, in O(log n) steps.

**Answer:** The predicate `r * r > n` is false up to the answer and true after it, so binary-search for the first `r` where it becomes true and subtract one. The range `[0, n + 1]` always contains that point. Using integers only avoids float rounding on large `n`.

```python
def isqrt(n: int) -> int:
    lo, hi = 0, n + 1                # first r with r*r > n lies in [0, n+1]
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid > n:
            hi = mid
        else:
            lo = mid + 1
    return lo - 1

print(isqrt(0), isqrt(1), isqrt(15), isqrt(16), isqrt(17))  # 0 1 3 4 4
print(isqrt(10**30 + 5))  # 1000000000000000
```

## Split into D days

A to-do list of task durations must be done in the given order across `D` days; each day takes a consecutive block of tasks. Find the smallest possible length of the busiest day for `[4, 7, 2, 5, 8, 3]` and `D = 3`.

**Answer:** Guess a cap `c` and check feasibility greedily: fill each day until the next task would exceed `c`, then start a new day. If that uses at most `D` days, any larger cap also works, so feasibility is monotone and you can binary-search `c` between `max(tasks)` and `sum(tasks)`. Cost is O(N log S) where S is the total duration. Here the answer is 11: `[4, 7] [2, 5] [8, 3]`.

```python
def days_needed(tasks: list[int], cap: int) -> int:
    days, load = 1, 0
    for t in tasks:
        if load + t > cap:
            days, load = days + 1, 0
        load += t
    return days

def min_busiest_day(tasks: list[int], d: int) -> int:
    lo, hi = max(tasks), sum(tasks)
    while lo < hi:
        mid = (lo + hi) // 2
        if days_needed(tasks, mid) <= d:
            hi = mid
        else:
            lo = mid + 1
    return lo

print(min_busiest_day([4, 7, 2, 5, 8, 3], 3))  # 11
print(min_busiest_day([4, 7, 2, 5, 8, 3], 1))  # 29
```

## Three status codes in one pass

An array holds only the status codes `0` (queued), `1` (running), and `2` (done). Sort it in place in a single pass with O(1) extra space.

**Answer:** Use the three-way partition with pivot 1: keep `low` (end of the 0s), `i` (scanner), and `high` (start of the 2s). A 0 swaps to `low` and both advance; a 2 swaps to `high` and only `high` moves, because the value swapped in has not been examined; a 1 just advances `i`. Each element is touched a constant number of times, so it is O(N) time and O(1) space, without counting first.

```python
def sort_status(codes: list[int]) -> None:
    low, i, high = 0, 0, len(codes) - 1
    while i <= high:
        if codes[i] == 0:
            codes[low], codes[i] = codes[i], codes[low]
            low += 1
            i += 1
        elif codes[i] == 2:
            codes[i], codes[high] = codes[high], codes[i]
            high -= 1
        else:
            i += 1

codes = [2, 0, 1, 2, 1, 0, 0, 2]
sort_status(codes)
print(codes)  # [0, 0, 0, 1, 1, 2, 2, 2]
```

## Median without sorting

Find the median of an odd-length unsorted list of latencies in expected O(N) time. Why is that better than sorting, and when would a heap of size k be the better tool?

**Answer:** The median is the element at index `N // 2` of the sorted order, so quickselect it: partition around a random pivot and continue only on the side holding that index, for N + N/2 + ... = O(N) expected work. Sorting does O(N log N) to order everything you will throw away. Prefer a size-k heap when data streams in, or when k is tiny and you must not reorder the input.

```python
import random

def kth_smallest(xs: list[int], k: int) -> int:
    pivot = random.choice(xs)
    lower = [x for x in xs if x < pivot]
    equal = [x for x in xs if x == pivot]
    if k < len(lower):
        return kth_smallest(lower, k)
    if k < len(lower) + len(equal):
        return pivot
    return kth_smallest([x for x in xs if x > pivot], k - len(lower) - len(equal))

latencies = [120, 35, 98, 210, 64, 35, 77]
print(kth_smallest(latencies, len(latencies) // 2))  # 77
print(sorted(latencies)[3])  # 77
```

## Counting sort by age

Sort five million customer records by age (an integer 0 to 120), keeping records with the same age in their original order. What is the cost compared with a comparison sort?

**Answer:** Counting sort: one pass to count each age, a prefix sum over 121 slots to find where each age starts, and one pass that places each record at its age's next slot. That is O(N + K) with K = 121, effectively linear, versus O(N log N) ≈ 22 comparisons per record for a comparison sort. Walking the input in order keeps it stable.

```python
def sort_by_age(records: list[dict]) -> list[dict]:
    counts = [0] * 121
    for r in records:
        counts[r["age"]] += 1
    starts, running = [0] * 121, 0
    for age in range(121):
        starts[age], running = running, running + counts[age]
    out = [None] * len(records)
    for r in records:
        out[starts[r["age"]]] = r
        starts[r["age"]] += 1
    return out

people = [{"id": 1, "age": 34}, {"id": 2, "age": 19}, {"id": 3, "age": 34}, {"id": 4, "age": 7}]
print([p["id"] for p in sort_by_age(people)])  # [4, 2, 1, 3]
```

## Radix pass by pass

Run LSD radix sort (base 10) on `[512, 38, 271, 94, 106, 45]`. Write the array after the ones pass, the tens pass, and the hundreds pass.

**Answer:** Each pass stably groups by one digit, and stability is what preserves the order earned in earlier passes. Ones digits 2, 8, 1, 4, 6, 5 give `[271, 512, 94, 45, 106, 38]`. Tens digits (7, 1, 9, 4, 0, 3) give `[106, 512, 38, 45, 271, 94]`. Hundreds digits give the sorted `[38, 45, 94, 106, 271, 512]`.

```python
def radix_passes(nums: list[int]) -> None:
    exp = 1
    while max(nums) // exp > 0:
        buckets: list[list[int]] = [[] for _ in range(10)]
        for n in nums:                    # appending in order = stable
            buckets[(n // exp) % 10].append(n)
        nums = [n for b in buckets for n in b]
        print(nums)
        exp *= 10

radix_passes([512, 38, 271, 94, 106, 45])
# [271, 512, 94, 45, 106, 38]
# [106, 512, 38, 45, 271, 94]
# [38, 45, 94, 106, 271, 512]
```

## Leaderboard order

Sort leaderboard rows `(name, points)` by points high to low, breaking ties by name A to Z. Then do it again with ties broken by name Z to A.

**Answer:** For the first order, one key does it: `(-points, name)`, since negating flips only the numeric field. Strings cannot be negated, so for points descending with names descending you can sort by name descending first and then stably sort by points descending; the second sort keeps the name order within each tie. (Here both fields go the same way, so `reverse=True` on `(points, name)` would also work.)

```python
rows = [("mia", 40), ("ann", 55), ("zed", 40), ("bob", 55), ("kai", 40)]

print(sorted(rows, key=lambda r: (-r[1], r[0])))  # [('ann', 55), ('bob', 55), ('kai', 40), ('mia', 40), ('zed', 40)]

by_name_desc = sorted(rows, key=lambda r: r[0], reverse=True)
print(sorted(by_name_desc, key=lambda r: r[1], reverse=True))  # [('bob', 55), ('ann', 55), ('zed', 40), ('mia', 40), ('kai', 40)]
```

## Merge sorted server logs

Three servers each produce a log already sorted by timestamp. Produce one combined log in timestamp order without loading everything and calling `sort()`. What does it cost for N total lines and K servers?

**Answer:** Keep a min-heap with the next unread line from each server. Pop the smallest, emit it, and push the next line from the same server. The heap never holds more than K entries, so each line costs O(log K): O(N log K) total with O(K) extra memory, and it works on streams. Include the server index in the heap entry so equal timestamps compare cleanly.

```python
import heapq

def merge_logs(logs: list[list[tuple[int, str]]]) -> list[tuple[int, str]]:
    heap = [(log[0][0], k, 0) for k, log in enumerate(logs) if log]
    heapq.heapify(heap)
    out = []
    while heap:
        ts, k, i = heapq.heappop(heap)
        out.append(logs[k][i])
        if i + 1 < len(logs[k]):
            heapq.heappush(heap, (logs[k][i + 1][0], k, i + 1))
    return out

a = [(1, "a-boot"), (7, "a-ok")]
b = [(3, "b-boot"), (4, "b-warn"), (9, "b-ok")]
c = [(2, "c-boot")]
print([msg for _, msg in merge_logs([a, b, c])])  # ['a-boot', 'c-boot', 'b-boot', 'b-warn', 'a-ok', 'b-ok']
```
