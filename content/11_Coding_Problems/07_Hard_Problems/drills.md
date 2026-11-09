# Hard Problems — Drills

Original drills for the tools on this topic. Each answer has an approach, a cost, and Python. No published book problems.

## Bits that differ

Firmware word `0b1100` was replaced by `0b1010`. Which bit indexes flipped?

**Answer:** XOR the words. `0b1100 ^ 0b1010` is `0b0110`, so bits 1 and 2 differ. Walk the set bits, or test each index up to the width. Cost is O(width), which is O(1) for a fixed word. XOR is the whole comparison. A loop that checks both words separately is the same answer and more code. Bit 0 is the least significant bit.

```python
def flipped(before: int, after: int) -> list[int]:
    diff = before ^ after
    return [i for i in range(diff.bit_length()) if diff >> i & 1]

print(flipped(0b1100, 0b1010))  # [1, 2]
```

## Parity of a sensor byte

A sensor byte is `0b1011_0001`. Is the number of set bits odd? Do it with a fold, not a full popcount table.

**Answer:** Even. `0b10110001` has bits 0, 4, 5, and 7 set, four of them. Fold the byte with `x ^= x >> 4`, then `>> 2`, then `>> 1`. The low bit is the parity, 0, so `odd_parity` is false. `bit_count() % 2` agrees. Cost is O(log width), constant for one byte. A shift of 1 only, repeated, is a different reduction and is easy to get wrong. Use the halving fold or the popcount.

```python
def odd_parity(word: int) -> bool:
    x = word
    x ^= x >> 4
    x ^= x >> 2
    x ^= x >> 1
    return x & 1 == 1

print(odd_parity(0b10110001), (0b10110001).bit_count() % 2 == 1)  # False False
```

## A scripted shuffle

Shuffle `[0, 1, 2, 3]` by Fisher-Yates. The random choices, one per index, are suffix indexes `[2, 1, 3]`. What order comes out, and why is "swap each item with a random earlier item" unfair to mention as a fix?

**Answer:** Start `[0, 1, 2, 3]`. Swap index 0 with 2, getting `[2, 1, 0, 3]`. Swap index 1 with 1, no change. Swap index 2 with 3, getting `[2, 1, 3, 0]`. Each choice was inside the not-yet-fixed suffix, so this is one legal fair shuffle, produced in O(n). Swapping `i` only with a smaller index cannot generate every permutation equally. Some orders become unreachable and others become too likely. The suffix rule is the fix, not a swap with the prefix.

```python
def shuffle(items: list[int], picks: list[int]) -> list[int]:
    data = list(items)
    for i, j in enumerate(picks):
        data[i], data[j] = data[j], data[i]
    return data

print(shuffle([0, 1, 2, 3], [2, 1, 3]))  # [2, 1, 3, 0]
```

## Two items from a stream

The stream is `a b c d` and you may keep only two items. The scripted draws, each uniform in `0 .. t` as item `t` arrives, are `0` for `c` (t = 2) and `1` for `d` (t = 3). What stays in the reservoir?

**Answer:** Start with `[a, b]`. For `c`, draw 0, which is inside the reservoir, so slot 0 becomes `c`: `[c, b]`. For `d`, draw 1, so slot 1 becomes `d`: `[c, d]`. A draw of 2 or 3 at the last step would have left the reservoir alone. Time is O(n). Memory is O(k) with k = 2. You never stored the whole stream. The same draws always give the same sample, which is how you test it.

```python
def reservoir(stream: list[str], k: int, picks: list[int]) -> list[str]:
    kept = list(stream[:k])
    for t in range(k, len(stream)):
        j = picks[t - k]
        if j < k:
            kept[j] = stream[t]
    return kept

print(reservoir(list("abcd"), 2, [0, 1]))  # ['c', 'd']
```

## Three coldest hours

Temperatures are `[5, 1, 8, 0, 3]`. Return the three coldest, coldest first, without sorting the whole list.

**Answer:** Keep a max-heap of size 3. Store negated values so Python's min-heap acts as a max-heap. The top is the warmest of the cold set. 5, 1, and 8 fill it. 0 is colder than 8, so 8 leaves. 3 is colder than 5, so 5 leaves. The heap holds 0, 1, and 3. Cost is O(n log k) with k = 3. Sorting is O(n log n) and is the check, not the tool, once `n` is large and `k` is small. Fewer than three hours returns whatever you saw.

```python
import heapq

def coldest(hours: list[int], k: int) -> list[int]:
    heap: list[int] = []
    for hour in hours:
        if len(heap) < k:
            heapq.heappush(heap, -hour)
        elif hour < -heap[0]:
            heapq.heapreplace(heap, -hour)
    return sorted(-value for value in heap)

print(coldest([5, 1, 8, 0, 3], 3))  # [0, 1, 3]
```

## Median after each arrival

Values arrive as `1`, then `8`, then `3`, then `6`. What is the median after all four, using two heaps?

**Answer:** 4.5. The lower max-heap ends as `{1, 3}` and the upper min-heap as `{6, 8}`. The sizes match, so the median is the average of the tops, 3 and 6. Each insert is O(log n). After one value the median is that value. After two it is their average. Do not sort the prefix on every arrival. That is O(n^2). If the problem wants the lower middle on an odd count, return the lower top and do not average.

```python
import heapq

def medians(values: list[int]) -> list[float]:
    low: list[int] = []
    high: list[int] = []
    out: list[float] = []
    for value in values:
        heapq.heappush(low, -value)
        heapq.heappush(high, -heapq.heappop(low))
        if len(high) > len(low):
            heapq.heappush(low, -heapq.heappop(high))
        if len(low) > len(high):
            out.append(float(-low[0]))
        else:
            out.append((-low[0] + high[0]) / 2)
    return out

print(medians([1, 8, 3, 6]))  # [1.0, 4.5, 3.0, 4.5]
```

## Alarm codes in a log line

The codes are `pip`, `pit`, and `tap`. The line is `tap the pit`. Which codes appear? A separate search per code works here. When would the trie be the thing you build?

**Answer:** `tap` and `pit` appear. `pip` does not. Insert the codes into a trie, then from each character of the line walk while the trie has that child, and record a hit at each end-of-word node. Cost is O(n L) for line length `n` and code length `L`. One or two codes do not need a trie. A few hundred codes that share prefixes do: the shared `pi` of `pip` and `pit` is stored once, and the walk still stops when the next character is missing. Report every match, including overlaps.

```python
class Trie:
    def __init__(self) -> None:
        self.kids: dict[str, "Trie"] = {}
        self.end = False

    def insert(self, word: str) -> None:
        node = self
        for char in word:
            node = node.kids.setdefault(char, Trie())
        node.end = True

def appearing(text: str, words: list[str]) -> list[str]:
    root = Trie()
    for word in words:
        root.insert(word)
    hits: set[str] = set()
    for start in range(len(text)):
        node = root
        for end in range(start, len(text)):
            node = node.kids.get(text[end])  # type: ignore[assignment]
            if node is None:
                break
            if node.end:
                hits.add(text[start : end + 1])
    return sorted(hits)

print(appearing("tap the pit", ["pip", "pit", "tap"]))  # ['pit', 'tap']
```

## Ropes between piers

Piers are numbered 0 through 5. Ropes join `(1, 2)`, `(3, 4)`, and `(2, 3)`. Is pier 1 connected to pier 4? Is pier 1 connected to pier 5?

**Answer:** Yes, and no. Union-find links roots. 1 and 2 share a root, 3 and 4 share a root, then linking 2 and 3 merges those components, so 1 and 4 match. Pier 5 was never in a rope, so its root is itself. Nearly O(1) per rope and query with path compression. This does not produce the path `1-2-3-4`. If the question asks for the route, search the graph. Union-find only answers membership.

```python
def joined(n: int, ropes: list[tuple[int, int]], a: int, b: int) -> bool:
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for left, right in ropes:
        parent[find(right)] = find(left)
    return find(a) == find(b)

ropes = [(1, 2), (3, 4), (2, 3)]
print(joined(6, ropes, 1, 4), joined(6, ropes, 1, 5))  # True False
```

## Next taller crate

Heights from the left are `[2, 1, 4, 3]`. For each crate, what is the index of the next strictly taller crate to its right, or -1 if none?

**Answer:** Indexes `[2, 2, -1, -1]`. The 2 and the 1 are both popped by the 4. The 4 and the 3 have nothing taller after them. A decreasing stack of indexes does this in O(n): each index is pushed once and popped once. The nested scan to the right is O(n^2) and is the brute force to match on this four-crate row. Ties are not taller. `<=` would be the wrong test if the problem says strictly taller.

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

## A common subsequence

What is the length of the longest common subsequence of `stone` and `notes`? The characters need not be contiguous.

**Answer:** 2. One such subsequence is `t, e`. Another is `o, e` or `n, e`. There is no common subsequence of length 3: the shared letters do not line up in one order in both strings. Fill `dp[i][j]` from the prefixes. A matching character adds one to the diagonal. Otherwise take the larger neighbor. Time and space are O(n m), here 5 by 5. A rolling row stores only the length. If you needed the actual string, keep parent pointers. Do not confuse this with a contiguous substring. `on` is contiguous in `stone` and is not in order inside `notes`.

```python
def lcs_length(left: str, right: str) -> int:
    prev = [0] * (len(right) + 1)
    for a in left:
        curr = [0]
        for j, b in enumerate(right, 1):
            curr.append(prev[j - 1] + 1 if a == b else max(prev[j], curr[-1]))
        prev = curr
    return prev[-1]

print(lcs_length("stone", "notes"))  # 2
```

## Pairs out of order

The row `[2, 4, 1, 3]` has an inversion wherever an earlier value is greater than a later one. How many inversions, counted while merging?

**Answer:** Three: `(2, 1)`, `(4, 1)`, and `(4, 3)`. Merge sort counts them. When the merge takes a value from the right half, that value is smaller than every value still waiting on the left, and each waiting value is one inversion. A range of one item has zero inversions. The sort is O(n log n). The double loop is O(n^2) and is how you check this four-item row: three pairs qualify, and `(2, 3)` does not.

```python
def inversions(values: list[int]) -> int:
    buf = list(values)

    def sort(lo: int, hi: int) -> int:
        if hi - lo <= 1:
            return 0
        mid = (lo + hi) // 2
        count = sort(lo, mid) + sort(mid, hi)
        i, j = lo, mid
        merged: list[int] = []
        while i < mid and j < hi:
            if buf[i] <= buf[j]:
                merged.append(buf[i])
                i += 1
            else:
                merged.append(buf[j])
                j += 1
                count += mid - i
        merged.extend(buf[i:mid])
        merged.extend(buf[j:hi])
        buf[lo:hi] = merged
        return count

    return sort(0, len(buf))

print(inversions([2, 4, 1, 3]))  # 3
```

## Fewest code changes

Allowed dock codes are `rib`, `rid`, `rod`, `red`, and `bed`. One change may replace a single character, and the result must be an allowed code. How many changes turn `rib` into `red`?

**Answer:** Two: `rib` to `rid` (the last character) to `red` (the middle character). The path through `rod` is longer, and BFS must not return it. `bed` sits beside `red` and is not needed. Build an edge when two allowed codes differ in exactly one position, then BFS from `rib`. Every edge costs 1, so the first time `red` is dequeued, or the first time it is seen, is a shortest path. With five codes, comparing every pair is fine, O(N^2 L). A visited set stops the walk from bouncing between `rib` and `rid`. If `red` were absent, the answer would be that no path exists, not a partial walk.

```python
from collections import deque

def changes(start: str, goal: str, allowed: set[str]) -> int | None:
    if start == goal:
        return 0
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        code, dist = queue.popleft()
        for other in allowed:
            if other in seen:
                continue
            if sum(a != b for a, b in zip(code, other)) == 1:
                if other == goal:
                    return dist + 1
                seen.add(other)
                queue.append((other, dist + 1))
    return None

codes = {"rib", "rid", "rod", "red", "bed"}
print(changes("rib", "red", codes))  # 2
```

## Is the candidate a majority?

Paint cans pass as `red, blue`. Boyer-Moore still returns a candidate. Is it a majority? What about `red, red, blue, red`?

**Answer:** `red, blue` has no majority. Each color is half, and the rule is more than half. The algorithm's candidate must be counted. One of two is not enough, so the answer is none. `red, red, blue, red` has red three times out of four, which is a majority. The first pass is O(n) and O(1) memory. The verify pass is another O(n). Skip the verify only when the problem promises a majority exists. Otherwise "none" is a real output.

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
    if items and items.count(candidate) * 2 > len(items):
        return candidate
    return None

print(majority(["red", "blue"]), majority(["red", "red", "blue", "red"]))
# None red
```

## Ticket sizes in a small range

Sizes are `[3, 1, 2, 3, 1]`, each between 1 and 3. Sort them without a comparison sort.

**Answer:** Count each size, then write the counts back in order: two 1s, one 2, two 3s, so `[1, 1, 2, 3, 3]`. Time is O(n + k) with k = 3. A comparison sort is O(n log n) and is unnecessary once the range is this small. If the range were a million wide and only five tickets appeared, a map of the values you actually saw beats a dense array. Negative sizes need an offset before they can index the array. Ask for the range before you allocate.

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

## The slow check, then the sort

Readings are `[1, 5, 9]` and `[1, 5, 6]`. Are any two within 1 of each other? Show a correct O(n^2) check and the O(n log n) version, and show they agree.

**Answer:** No pair in the first list is within 1. In the second, 5 and 6 are. The slow check tries every pair. The fast check sorts and looks only at neighbors, because a non-neighbor gap is at least as large as the gaps it spans. Both return false, then true. Sort is O(n log n). The pair loop is the specification. If they ever disagree, the neighbor test is wrong, often because it forgot that equal values are within 1. An empty list and a single reading have no pair and return false.

```python
def close_slow(values: list[int]) -> bool:
    return any(
        abs(values[i] - values[j]) <= 1
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )

def close_fast(values: list[int]) -> bool:
    ordered = sorted(values)
    return any(b - a <= 1 for a, b in zip(ordered, ordered[1:]))

print(close_slow([1, 5, 9]), close_fast([1, 5, 9]))  # False False
print(close_slow([1, 5, 6]), close_fast([1, 5, 6]))  # True True
```
