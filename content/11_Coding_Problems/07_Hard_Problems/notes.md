# Hard Problems

A hard problem is one whose state is not obvious: a middle of two heaps, a cancelled count, a component root, the cell of a string table. These notes are those tools. They are not a list of published problems. Each tool has a slow version it must match on a small input, and several of them return a candidate that a second pass has to confirm.

## Key Points

- **Optimize brute force in steps** — write the correct slow answer and its cost, then remove one repeated scan. Keep the slow function until the fast one agrees.
- **Bit-level arithmetic** — XOR is add without carry. The carry is `(a & b) << 1`, folded back in until it is 0. XOR of two words is the bits that differ.
- **A fair shuffle** — Fisher-Yates swaps index `i` with a uniform choice in the suffix `i .. n - 1`. Every permutation is equally likely.
- **Reservoir sampling** — `k` items from a stream of unknown length, in O(k) memory. Item `t` replaces a reservoir slot with probability `k / (t + 1)`.
- **A heap for top-k** — a heap of size `k` is O(n log k). The top of the heap is the worst of the winners, ready to be replaced.
- **Two heaps for a running median** — a max-heap for the lower half, a min-heap for the upper half, sizes differing by at most one.
- **A trie for many patterns** — shared prefixes cost once. From each index in the text, walk while characters match and record end-of-word nodes.
- **Union-find** — `find` returns a root, `union` links roots. Use it for "joined or not," not for the path between them.
- **A monotonic stack** — pop shorter indexes when a taller one arrives. Each index is pushed and popped once. That index's next taller item is the one that popped it.
- **DP on strings** — `dp[i][j]` is the answer for two prefixes. A match takes the diagonal plus one. A miss takes the better neighbor.
- **Divide and conquer** — split, solve, combine. Merge sort counts inversions because a right-half value beats every still-waiting left value.
- **Search on a one-change graph** — codes that differ by one character are edges. BFS gives the fewest changes. Mark visited.
- **Majority vote** — cancel pairs of different items. Verify the candidate in a second pass unless a majority was promised and you trust that promise.
- **Counting and buckets** — small integer ranges sort in O(n + k). Ask for the range before you allocate the array.
- **A candidate is not an answer** — if the check fails, say none. Do not return the candidate anyway.

## Example

```python
"""Piers joined by ropes, and the three coldest hours, on inputs small enough to check."""
import heapq


def same_component(n: int, ropes: list[tuple[int, int]], a: int, b: int) -> bool:
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for left, right in ropes:
        parent[find(right)] = find(left)
    return find(a) == find(b)


def coldest(hours: list[int], k: int) -> list[int]:
    heap: list[int] = []
    for hour in hours:
        if len(heap) < k:
            heapq.heappush(heap, -hour)
        elif hour < -heap[0]:
            heapq.heapreplace(heap, -hour)
    return sorted(-value for value in heap)


print(same_component(6, [(1, 2), (3, 4), (2, 3)], 1, 4))  # True
print(same_component(6, [(1, 2), (3, 4), (2, 3)], 1, 5))  # False
print(coldest([5, 1, 8, 0, 3], 3))  # [0, 1, 3]
```

Joining 1-2, 3-4, and 2-3 puts piers 1 and 4 on one root and leaves 5 alone. The heap never holds more than three temperatures. Both are one idea plus a check you can do on five items.

## More practice

Work the original exercises on the **Drills** tab. Each one names the tool, the cost, and a Python check. None of them is a published problem from a book list.
