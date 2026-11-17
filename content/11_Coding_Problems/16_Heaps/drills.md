# Heaps — Drills

Original drills for a bounded heap, a smash simulation, a join cost, a range across lists, a tie that points the wrong way, a grid merge, meeting rooms, and the choice between a heap and something simpler. Each answer has an approach, a cost, and Python. The numbers are exercise numbers. None of these repeats the leaderboard cutoff, the merged logs, the median balance trace, the dict tie that crashes, the three coldest hours, or the median after 1, 8, 3, and 6.

## The k closest points

The exercise points are `(1, 2)`, `(3, 0)`, `(-1, 1)`, `(4, 4)`, and `(0, 1)`. Return the 2 closest to the origin, closest first. Distance is the square of the coordinates, so the square root is never required. Also answer a k of 0, an empty list, and `[(1, 1)]` with k of 3.

**Answer:** The squares are 5, 9, 2, 32, and 1. The two closest are `(0, 1)` and `(-1, 1)`. Keep a max-heap of size k, stored as negated squares so `heapq` can hold it. The root is the farthest point still kept. A closer point replaces it. Sort the survivors by square at the end. Each point costs O(log k), so the scan is O(n log k) time and O(k) memory. A k of 0 returns nothing. An empty list returns nothing. A k larger than the list returns every point. Equal squares on the boundary can keep either point. This input has no such tie. One closest point is the minimum square, and a heap is more structure than that question needs.

```python
import heapq


def k_closest(points: list[tuple[int, int]], k: int) -> list[tuple[int, int]]:
    if k <= 0:
        return []
    heap: list[tuple[int, int, int]] = []
    for x, y in points:
        dist = x * x + y * y
        if len(heap) < k:
            heapq.heappush(heap, (-dist, x, y))
        elif dist < -heap[0][0]:
            heapq.heapreplace(heap, (-dist, x, y))
    kept = [(x, y) for _dist, x, y in heap]
    return sorted(kept, key=lambda point: (point[0] * point[0] + point[1] * point[1], point))


print(k_closest([(1, 2), (3, 0), (-1, 1), (4, 4), (0, 1)], 2))
print(k_closest([(1, 2), (3, 0), (-1, 1), (4, 4), (0, 1)], 0), k_closest([], 2))
print(k_closest([(1, 1)], 3))
# [(0, 1), (-1, 1)]
# [] []
# [(1, 1)]
```

## The last stone

The exercise weights are `[9, 3, 6, 1]`. While two or more stones remain, smash the two heaviest. If they differ, the difference goes back. What weight remains? Also answer `[2, 2]`, an empty list, and `[7]`.

**Answer:** Smash 9 with 6 and put 3 back. The stones are then 3, 3, and 1. The two 3s cancel. The 1 remains. A max-heap of negated weights pops the heaviest twice per smash. Each smash is O(log n), and there are fewer than n smashes, so the time is O(n log n) and the memory is O(n). `[2, 2]` cancels to 0. An empty list is 0. One stone is that stone, with no smash. Sorting a fresh list on every smash is the slow version of the same rule.

```python
import heapq


def last_stone(weights: list[int]) -> int:
    heap = [-weight for weight in weights]
    heapq.heapify(heap)
    while len(heap) >= 2:
        heavier = -heapq.heappop(heap)
        lighter = -heapq.heappop(heap)
        if heavier != lighter:
            heapq.heappush(heap, -(heavier - lighter))
    return -heap[0] if heap else 0


print(last_stone([9, 3, 6, 1]), last_stone([2, 2]), last_stone([]), last_stone([7]))
# 1 0 0 7
```

## Cost of joining the ropes

The exercise lengths are `[4, 3, 2, 6]`. Joining two ropes costs their sum, and that new rope goes back into the pile. Repeat until one rope remains. The answer is the total of the join costs, not the final length. Also answer `[1]`, an empty list, and `[1, 2]`.

**Answer:** The cost is 29. Join 2 and 3 first, cost 5, and the pile is 4, 5, 6. Join 4 and 5, cost 9, running total 14, and the pile is 6 and 9. Join those, cost 15, total 29. The final length is 15, which is the sum of the lengths, and it is not the cost. Always join the two shortest. A min-heap pops them in O(log n). There are n - 1 joins, so the time is O(n log n) and the memory is O(n). One rope, or none, costs 0. `[1, 2]` costs 3. On this pile, joining 2 with 4 before 3 costs 30.

```python
import heapq


def join_cost(lengths: list[int]) -> int:
    heap = list(lengths)
    heapq.heapify(heap)
    cost = 0
    while len(heap) >= 2:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        cost += left + right
        heapq.heappush(heap, left + right)
    return cost


print(join_cost([4, 3, 2, 6]), join_cost([1]), join_cost([]), join_cost([1, 2]))
# 29 0 0 3
```

## Smallest range across the lists

The exercise lists are `[4, 10, 15]`, `[0, 9, 12]`, and `[5, 18]`. Each list is sorted. Find the shortest inclusive window that contains at least one value from each list. Report the start and end the scan keeps. Also answer one list, `[1, 3]`, and an empty collection of lists.

**Answer:** The window is 0 through 5. Its length is 5. Other windows of that length exist, including 4 through 9. The scan keeps the first minimum it sees. Put the first value of each list in a min-heap, and remember the largest value currently in the heap. The heap's root and that largest value are a candidate window. Pop the root and push the next value from the same list, updating the largest. Stop when a list runs out, because a later window would miss that list. Each value is pushed once, the heap holds one value per list, and the time is O(N log k) with O(k) extra memory. One sorted list is the window from its first value to itself. No lists means there is no window.

```python
import heapq


def smallest_range(rows: list[list[int]]) -> tuple[int, int] | None:
    if not rows:
        return None
    heap: list[tuple[int, int, int]] = []
    current_max = rows[0][0]
    for index, row in enumerate(rows):
        heapq.heappush(heap, (row[0], index, 0))
        current_max = max(current_max, row[0])
    best = (heap[0][0], current_max)
    while True:
        _value, index, place = heapq.heappop(heap)
        if place + 1 == len(rows[index]):
            break
        nxt = rows[index][place + 1]
        heapq.heappush(heap, (nxt, index, place + 1))
        current_max = max(current_max, nxt)
        if current_max - heap[0][0] < best[1] - best[0]:
            best = (heap[0][0], current_max)
    return best


print(smallest_range([[4, 10, 15], [0, 9, 12], [5, 18]]))
print(smallest_range([[1, 3]]), smallest_range([]))
# (0, 5)
# (1, 1) None
```

## The tie that keeps the later word

Consider the exercise counts in this order: ash 2, elm 2, oak 2. Keep the 2 most frequent words. A higher count comes first, and a tie goes to the earlier word. The heap stores `(count, word)` and replaces the root when the new tuple is greater. What does that return, and what should it return?

**Answer:** It returns oak then elm. The correct pair is ash then elm. After ash and elm are pushed, the root is ash, because the word is compared in alphabetical order and ash is earlier. Oak compares greater than ash, so ash is the one that leaves. The root of a size-2 heap has to be the word you would drop. On a tie that word is the later one, oak, not the earlier one. Invert the word: `__lt__` is a lower count, or the same count and a later word. Replace the root when the root is worse than the new word, then reverse the pops. After the counts exist, the time is O(u log k) for u distinct words and the heap memory is O(k). The wrong tuple still runs. It fails the tie.

```python
import heapq


class Weaker:
    def __init__(self, count: int, word: str) -> None:
        self.count = count
        self.word = word

    def __lt__(self, other: "Weaker") -> bool:
        if self.count != other.count:
            return self.count < other.count
        return self.word > other.word


def wrong(pairs: list[tuple[str, int]], k: int) -> list[str]:
    heap: list[tuple[int, str]] = []
    for word, count in pairs:
        item = (count, word)
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)
    out = [heapq.heappop(heap)[1] for _ in range(len(heap))]
    out.reverse()
    return out


def right(pairs: list[tuple[str, int]], k: int) -> list[str]:
    heap: list[Weaker] = []
    for word, count in pairs:
        item = Weaker(count, word)
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif heap[0] < item:
            heapq.heapreplace(heap, item)
    out = [heapq.heappop(heap).word for _ in range(len(heap))]
    out.reverse()
    return out


counts = [("ash", 2), ("elm", 2), ("oak", 2)]
print(wrong(counts, 2), right(counts, 2))
# ['oak', 'elm'] ['ash', 'elm']
```

## k-th smallest in a sorted grid

Each row of the exercise grid is sorted, left to right. The grid is `[[1, 5, 9], [4, 8, 12], [11, 13, 15]]`. What is the 4th smallest value, counting from 1? Also answer k of 1 and k of 9.

**Answer:** The 4th smallest is 8. The sorted values are 1, 4, 5, 8, 9, 11, 12, 13, 15. Treat each row as a sorted list and run a k-way merge from the first column. The heap starts with `(row[0], row index, column 0)` for every row. Pop k times. After each pop, push the next column of that same row when one remains. The row index is the tie-break, so equal values do not compare the rows themselves. Heapify is O(rows). k pops are O(k log rows). The extra memory is O(rows). The first pop is 1. The ninth pop is 15. A column that is also sorted is not what this scan uses. It only needs each row to be sorted.

```python
import heapq


def kth_smallest(grid: list[list[int]], k: int) -> int:
    heap = [(row[0], row_index, 0) for row_index, row in enumerate(grid) if row]
    heapq.heapify(heap)
    value = 0
    for _ in range(k):
        value, row_index, column = heapq.heappop(heap)
        if column + 1 < len(grid[row_index]):
            heapq.heappush(heap, (grid[row_index][column + 1], row_index, column + 1))
    return value


grid = [[1, 5, 9], [4, 8, 12], [11, 13, 15]]
print(kth_smallest(grid, 4), kth_smallest(grid, 1), kth_smallest(grid, 9))
# 8 1 15
```

## Rooms for the meetings

The exercise meetings are `(1, 4)`, `(2, 5)`, `(3, 6)`, and `(7, 9)`. A meeting occupies a room from its start up to, but not including, its end, so a meeting that ends at t frees the room for one that starts at t. How many rooms are needed at once? Also answer `(1, 2)` followed by `(2, 3)`, `(1, 3)` followed by `(2, 4)`, and an empty list.

**Answer:** Three rooms. Sorted by start, the first three meetings overlap, and the meeting at 7 reuses the room that freed at 4. A min-heap of end times holds the rooms in use. If the earliest end is at or before the new start, replace that end. Otherwise push a new end. The heap's length after the last meeting is the number of rooms. Sorting is O(n log n), and each meeting does one heap operation, so the time stays O(n log n). The heap holds one end per room, O(n) when every meeting overlaps. `(1, 2)` then `(2, 3)` needs one room. `(1, 3)` then `(2, 4)` needs two. An empty list needs none. Merging overlapping spans, on the [Merge intervals](../06_Moderate_Problems/) card, tells you the occupied blocks. It does not count how many meetings share an instant.

```python
import heapq


def rooms(meetings: list[tuple[int, int]]) -> int:
    heap: list[int] = []
    for start, end in sorted(meetings):
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)
        else:
            heapq.heappush(heap, end)
    return len(heap)


print(rooms([(1, 4), (2, 5), (3, 6), (7, 9)]))
print(rooms([(1, 2), (2, 3)]), rooms([(1, 3), (2, 4)]), rooms([]))
# 3
# 1 2 0
```

## Heap, sort, selection, or buckets

Four exercise questions. Which tool answers each one?

1. The third-smallest reading from a stream of a million integers, keeping only a handful of them.
2. Every reading, printed once, in order.
3. The minimum of a list.
4. How many times each score from 0 through 100 appears.

**Answer:** A max-heap of size 3, because the stream is long and only three survivors matter. A sort, because the whole order is the output. One variable, updated when a reading is smaller, because a single minimum is one pass. Counting buckets, one slot per score from 0 through 100, because the keys are a small integer range. The size-3 heap is O(n log 3) time and O(1) memory past those three slots. The sort is O(n log n). The minimum is O(n) time and O(1) extra memory. The buckets are O(n + 101). Quickselect would answer "the third-smallest" if the million readings were already stored and nothing else was required. It does not keep a stream, and it does not count the scores.

```python
def choose(question: str) -> str:
    return {
        "third-smallest of a stream": "max-heap of size 3",
        "every reading in order": "sort",
        "the minimum": "one variable",
        "scores from 0 through 100": "counting buckets",
    }[question]


print(choose("third-smallest of a stream"))
print(choose("every reading in order"))
print(choose("the minimum"))
print(choose("scores from 0 through 100"))
# max-heap of size 3
# sort
# one variable
# counting buckets
```
