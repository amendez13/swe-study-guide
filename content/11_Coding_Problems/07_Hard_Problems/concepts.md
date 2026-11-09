## Optimize brute force in steps

A hard problem still has a correct slow answer. Write that answer first, with its cost, on a tiny input you can check by hand. Then name the repeated work and remove one layer of it. A double loop that asks "do any two readings differ by at most 1" is O(n^2). Sorting makes the only pairs that can be that close into neighbors, and the check becomes O(n log n). You do not have to jump from the slow loop to the finished idea in one move.

Say which step you are on. "This is the correct O(n^2). The sort is the next step, and I have not written it yet" is a real answer. A half-written fast version that does not match the slow one on four elements is not. Keep the slow function until the fast one agrees with it.

```python
def close_pair_slow(values: list[int]) -> bool:
    return any(abs(values[i] - values[j]) <= 1 for i in range(len(values)) for j in range(i + 1, len(values)))

print(close_pair_slow([1, 5, 9]), close_pair_slow([1, 5, 6]))  # False True
```

## Bit-level arithmetic

XOR is addition without the carries. A carry happens where both bits are 1, which is `a & b`, and that carry lands one position higher, so `(a & b) << 1`. Adding in a loop is: sum without carry, then fold the carry back in, until the carry is 0. That is how hardware adds. It is also a way to see that a mask difference is just XOR: bits on in exactly one of two firmware words.

Use this when the data is flags or a fixed-width word. Do not use it to avoid the `+` operator in ordinary code. Python integers have no fixed width, so a teaching loop terminates. In a 32-bit language you mask after the shift or the carry walks off the top. Parity of a byte is the XOR of its bits, foldable in O(log width) by `x ^= x >> 1` repeatedly, or simply `x.bit_count() % 2`.

```python
def xor_add(a: int, b: int) -> int:
    while b:
        carry = (a & b) << 1
        a = a ^ b
        b = carry
    return a

print(xor_add(5, 3), 5 ^ 3)  # 8, and 6 is the bits that differ
```

## A fair shuffle

A fair shuffle gives every permutation the same chance. Fisher-Yates does that in one pass. For index `i` from 0 through n - 2, swap `i` with a uniformly chosen index in `i .. n - 1`, inclusive. The item at `i` is then fixed. Choosing from the whole array every time, or swapping `i` only with `i + 1`, does not give equal probability to every order.

The cost is O(n) swaps after you have the random indexes. In an interview, say "uniform among the not-yet-chosen suffix." A scripted list of those indexes makes the shuffle testable: the same choices always produce the same order. Do not sort by random keys unless you can say how ties and the random source behave. That sort is O(n log n) and easier to bias.

```python
def shuffle(items: list[int], picks: list[int]) -> list[int]:
    data = list(items)
    for i, j in enumerate(picks):
        data[i], data[j] = data[j], data[i]
    return data

print(shuffle([0, 1, 2, 3], [2, 1, 3]))  # [2, 1, 3, 0]
```

## Reservoir sampling

A reservoir sample picks `k` items uniformly from a stream whose length you do not know, using O(k) memory. Put the first `k` items in the reservoir. When item `t` arrives (`t` starting at 0), draw an integer `j` uniformly from `0 .. t`. If `j < k`, replace `reservoir[j]` with the new item. Each item seen so far then has probability `k / (t + 1)` of still being kept.

The cost is O(n) time and O(k) memory, one pass. You cannot do better on memory if you must return `k` items and you may not store the stream. Test it with scripted draws, not with a flaky assertion that a particular item "usually" appears. A sample of size 1 is the simple case: the first item starts as the answer, and item `t` replaces it with probability `1 / (t + 1)`.

```python
def reservoir(stream: list[str], k: int, picks: list[int]) -> list[str]:
    kept = list(stream[:k])
    for t in range(k, len(stream)):
        j = picks[t - k]  # uniform in 0 .. t
        if j < k:
            kept[j] = stream[t]
    return kept

print(reservoir(["a", "b", "c", "d"], 2, [0, 1]))  # ["c", "d"]
```

## A heap for top-k

A heap of size `k` tracks the best `k` items while you scan `n` of them. For the `k` coldest hours, keep a max-heap of the coldest so far. The warmest of those sits on top. A new hour colder than that top replaces it. Each of the `n` hours does O(log k) work, so the scan is O(n log k). Sorting the whole list is O(n log n), which is worse when `k` is much smaller than `n`.

Python's `heapq` is a min-heap, so store negated temperatures to get a max-heap. At the end, negate them back and sort if the caller wants coldest-first. An empty log returns an empty list. If `n < k`, the heap simply holds everything. Do not use a heap to get the single minimum. One variable does that.

```python
import heapq

def coldest(hours: list[int], k: int) -> list[int]:
    heap: list[int] = []  # max-heap of the k coldest, via negation
    for hour in hours:
        if len(heap) < k:
            heapq.heappush(heap, -hour)
        elif hour < -heap[0]:
            heapq.heapreplace(heap, -hour)
    return sorted(-value for value in heap)

print(coldest([5, 1, 8, 0, 3], 3))  # [0, 1, 3]
```

## Two heaps for a running median

One heap holds the lower half as a max-heap. The other holds the upper half as a min-heap. Their tops are the middle. Add a value to the lower half, then move the lower top onto the upper half so the upper half stays all-greater. If the upper half is longer, move its top back. The sizes differ by at most one.

The median is the lower top when that heap is longer, and the average of the two tops when the sizes match. Each insert is O(log n). A sorted list would be O(n) per insert. After `[1, 8, 3, 6]` the halves are `{1, 3}` and `{6, 8}`, and the median is `(3 + 6) / 2 = 4.5`. Odd counts return the lower top with no average. Say whether the problem wants a float average or the lower middle.

## A trie for many patterns

A trie is a tree of characters. Each path from the root is a prefix. A node marked end-of-word is a whole pattern. Inserting `p` patterns of length up to `L` costs O(p L). Checking a prefix is O(L). To find which alarm codes appear in a log line, insert the codes, then from each index in the line walk the trie while the characters match. Every time you land on an end-of-word node, you have a hit.

That scan is O(n L) for a line of length `n`. It beats running a separate search per pattern when many patterns share prefixes (`pip` and `pit` share `pi`). It loses to a single `in` check when you have one pattern. A trie does not by itself skip ahead the way a full automaton does. For an interview, the walk from each index is the version to draw. Say that overlapping hits are allowed: the walk reports every match, not the longest only, unless you ask it to.

## Union-find

Union-find tracks components that merge. Each pier starts alone. `find` follows parent pointers to a root. `union` links one root under the other. Two piers are connected when they share a root. Path compression points a node at its grandparent, or at the root, on the way up. Union by rank attaches the shorter tree under the taller one so the trees stay flat.

A sequence of `n` piers and `m` ropes is nearly O(m + n). Use this when the only questions are "join these two" and "are these two joined," and you do not need the path between them. If you need the actual route, build the graph and search. If you need to split a component, union-find is the wrong structure. It only merges.

```python
def connected(n: int, ropes: list[tuple[int, int]], query: tuple[int, int]) -> bool:
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in ropes:
        parent[find(b)] = find(a)
    return find(query[0]) == find(query[1])

print(connected(6, [(1, 2), (3, 4), (2, 3)], (1, 4)))  # True
```

## A monotonic stack

A monotonic stack keeps indexes whose values are in order, usually strictly decreasing. Walk left to right. Before you push index `i`, pop every index whose crate is shorter than `heights[i]`. Each popped index has just found its next taller crate: it is `i`. Indexes left on the stack have no taller crate to the right.

Each index is pushed once and popped once, so the walk is O(n). A nested loop that searches to the right for each crate is O(n^2). The stack works because a shorter crate hidden behind a taller one can never be the "next taller" for something further left. If the problem wants the next shorter crate, the inequality flips. Equal heights need a decision: `<=` pops ties, `<` leaves them.

```python
def next_taller(heights: list[int]) -> list[int]:
    answer = [-1] * len(heights)
    stack: list[int] = []
    for i, height in enumerate(heights):
        while stack and heights[stack[-1]] < height:
            answer[stack.pop()] = i
        stack.append(i)
    return answer

print(next_taller([2, 1, 4, 3]))  # [2, 2, -1, -1]
```

## DP on strings

When the answer for two strings depends on answers for their prefixes, store those answers in a table. The longest common subsequence of `stone` and `notes` uses `dp[i][j]`, the best for the first `i` characters of one and the first `j` of the other. If the characters match, the cell is one plus the diagonal. If they do not, it is the better of the cell above and the cell to the left.

The table is O(n m) time and space. Two rolling rows drop the space to O(min(n, m)) when you only need the length. The recurrence is the whole idea. If you cannot say what `dp[i][j]` means in one sentence, the table will be wrong. Subsequence, not substring: the characters need not be contiguous. A contiguous run is a different recurrence. Check the table on two strings of length three before you trust a longer pair.

```python
def lcs_length(left: str, right: str) -> int:
    prev = [0] * (len(right) + 1)
    for i, a in enumerate(left, 1):
        curr = [0]
        for j, b in enumerate(right, 1):
            curr.append(prev[j - 1] + 1 if a == b else max(prev[j], curr[-1]))
        prev = curr
    return prev[-1]

print(lcs_length("stone", "notes"))  # 2, for example t-e or o-e or n-e
```

## Divide and conquer

Divide and conquer splits the input, solves the halves, and combines them. An inversion is a pair `i < j` with `value[i] > value[j]`. Merge sort counts them while it merges. A value taken from the right half is greater than every still-unmerged value in the left half, and each of those is an inversion. The sort is O(n log n). The naive double loop is O(n^2) and is the check on a four-element list.

The combine step is where this technique succeeds or fails. If combining the halves costs more than the split saved, you do not have an improvement. Quickselect, which partitions like quicksort and only recurses into the side that holds the k-th item, is the same family and is expected O(n) for one order statistic. Say the split, the combine, and the base case (a range of length 0 or 1 has zero inversions).

## Search on a one-change graph

Some searches are graphs you build as you go. Dock codes are short strings. An edge exists between two codes in the allowed set when they differ by exactly one character. The fewest changes from `rib` to `red` is what a breadth-first search returns on that graph. BFS is the right search because every edge has cost 1, so the first time you reach a code you reached it by a shortest path.

The cost is O(N L^2 A) if you generate neighbors by trying each position and each character, over `N` codes of length `L` and alphabet size `A`, with a set for "is this code allowed." For a handful of codes, compare each pair in O(N^2 L). Draw the codes and the edges for a set of five before you write the queue. A visited set is required. Without it a cycle of two codes that differ by one character never ends.

## Majority vote

Boyer-Moore finds a majority candidate in one pass and O(1) memory. A majority item appears more than `n / 2` times. Walk the stream. When the count is 0, the current item becomes the candidate and the count becomes 1. A matching item increments the count. Any other item decrements it. Pairs of different items cancel. If a majority exists, it is the candidate at the end.

The candidate is not yet an answer. On `[red, blue]` the count ends at 0 or on a non-majority, depending on the last cancellation, and neither color is a majority. Count the candidate in a second pass, or refuse if you were not promised a majority. The algorithm does not tell you the count. It tells you the only value that could possibly be one. Two passes are still O(n) time and O(1) extra memory.

```python
def majority(items: list[str]) -> str | None:
    candidate = ""
    count = 0
    for item in items:
        if count == 0:
            candidate = item
            count = 1
        elif item == candidate:
            count += 1
        else:
            count -= 1
    if items.count(candidate) * 2 > len(items):
        return candidate
    return None

print(majority(["red", "red", "blue", "red"]))  # red
```

## Counting and buckets

When the values are small integers, a count array sorts them without comparisons. Ticket sizes in `1 .. 5` get a slot per size. One pass increments the slot. A second pass writes the values back in order. Time is O(n + k) for `k` possible sizes. Comparison sort is O(n log n) and loses when `k` is tiny. A hash map is the same idea when the integers are sparse. Then you pay for the keys you actually see, not for a dense array.

Buckets also place values into a fixed number of bins when you only need a histogram, not a full sort. Do not allocate a million slots for a range you were not given. Ask for the range. Negative sizes need an offset so the index stays non-negative. The stable version writes from the count prefixes if equal keys must keep their original order. For plain integers, stability does not matter.

```python
def counting_sort(sizes: list[int], upper: int) -> list[int]:
    counts = [0] * (upper + 1)
    for size in sizes:
        counts[size] += 1
    ordered: list[int] = []
    for size, count in enumerate(counts):
        ordered.extend([size] * count)
    return ordered

print(counting_sort([3, 1, 2, 3, 1], 3))  # [1, 1, 2, 3, 3]
```

## A candidate is not an answer

Several of these tools return a candidate you still have to check. The majority algorithm returns a value that might not be a majority. A heuristic trie walk can report a prefix that is not a full code. A quickselect pivot can land on the wrong side if the partition is off by one. The check is a second linear pass, a membership test, or the slow function on a tiny input.

Ship the check. It is usually cheaper than the search and it is the difference between a plausible value and a correct one. If the check fails, the honest result is "no such item," not the candidate with a comment. State that case out loud: no majority, no path between the codes, no pair within 1.
