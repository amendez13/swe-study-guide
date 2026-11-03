# Heaps and Tries — Drills

Original mini-drills for binary heap, priority queue, and trie skills. Each card is one exercise: read the prompt and snippet, commit to an answer, then check it. Each Answer has a short Python solution that runs on its own. No copyrighted book text.

## Is it a heap?

Which of these arrays is a valid min-heap? For the one that is not, name the first index that breaks the rule.

```text
A = [2, 4, 3, 9, 5, 7]
B = [1, 3, 2, 4, 0, 6]
```

**Answer:** A is valid: every index `i >= 1` is >= its parent at `(i - 1) // 2`. B fails at index 4: its value 0 is smaller than its parent at index 1 (value 3). You only need to check non-root indices against their parent, which is one O(N) pass; siblings are never compared.

```python
def is_min_heap(a: list[int]) -> int | None:
    """Return the first index that violates the min-heap rule, or None."""
    for i in range(1, len(a)):
        if a[i] < a[(i - 1) // 2]:
            return i
    return None

print(is_min_heap([2, 4, 3, 9, 5, 7]))  # None
print(is_min_heap([1, 3, 2, 4, 0, 6]))  # 4
```

## Trace sift up

Start with an empty min-heap and push 8, 4, 6, 2, 5, 1 in that order. Write the final array and the total number of swaps.

**Answer:** `[1, 4, 2, 8, 5, 6]` after 5 swaps. Pushing 4 swaps once with 8. Pushing 6 needs no swap. Pushing 2 climbs twice (past 8, then past 4). Pushing 5 stays put under 4. Pushing 1 climbs twice (past 6, then past 2) to the root. Each push only touches one leaf-to-root path.

```python
def push(h: list[int], x: int) -> int:
    h.append(x)
    i, swaps = len(h) - 1, 0
    while i > 0 and h[i] < h[(i - 1) // 2]:
        p = (i - 1) // 2
        h[i], h[p] = h[p], h[i]
        i, swaps = p, swaps + 1
    return swaps

h: list[int] = []
total = sum(push(h, x) for x in [8, 4, 6, 2, 5, 1])
print(h)      # [1, 4, 2, 8, 5, 6]
print(total)  # 5
```

## Trace extract

From the min-heap `[1, 4, 2, 8, 5, 6]`, pop the minimum twice. What does the array look like after each pop?

**Answer:** First pop returns 1: the last element 6 moves to the root, then swaps with the smaller child 2, giving `[2, 4, 6, 8, 5]`. Second pop returns 2: 5 moves to the root and swaps with the smaller child 4; its only remaining child is 8, so it stops at `[4, 5, 6, 8]`. Python's `heapq` follows the same rule, so it can confirm your trace.

```python
import heapq

h = [1, 4, 2, 8, 5, 6]
print(heapq.heappop(h), h)  # 1 [2, 4, 6, 8, 5]
print(heapq.heappop(h), h)  # 2 [4, 5, 6, 8]
```

## Bug hunt: the wrong child

This sift-down sometimes leaves a broken heap. Find an input that breaks it and fix it.

```python
def sift_down(h, i):
    n = len(h)
    while True:
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and h[l] < h[i]:
            h[i], h[l] = h[l], h[i]; i = l
        elif r < n and h[r] < h[i]:
            h[i], h[r] = h[r], h[i]; i = r
        else:
            return
```

**Answer:** It swaps with the left child whenever the left child is smaller than the parent, even when the right child is smaller still. With `[9, 3, 1]`, 3 moves up and becomes the parent of 1, which breaks the rule. Pick the smallest of parent, left, and right first, then swap once with that winner.

```python
def sift_down(h: list[int], i: int) -> None:
    n = len(h)
    while True:
        l, r, m = 2 * i + 1, 2 * i + 2, i
        if l < n and h[l] < h[m]:
            m = l
        if r < n and h[r] < h[m]:
            m = r
        if m == i:
            return
        h[i], h[m] = h[m], h[i]
        i = m

h = [9, 3, 1]
sift_down(h, 0)
print(h)  # [1, 3, 9]
```

## Build cost: pushes vs. heapify

You need a min-heap of 1023 values that arrive in descending order (1023, 1022, ..., 1). Compare the number of swaps from pushing them one by one against bottom-up heapify. Which grows like N log N?

**Answer:** Pushing costs about 8,200 swaps: every new value is the new minimum, so it climbs all the way to the root, roughly log N swaps each. Bottom-up heapify needs about 1,000 swaps, under N, because half the nodes are leaves that never move and only a few nodes sit high enough to sink far. When all the data is available up front, call `heapify`.

```python
def push_swaps(xs: list[int]) -> int:
    h: list[int] = []
    swaps = 0
    for x in xs:
        h.append(x)
        i = len(h) - 1
        while i > 0 and h[i] < h[(i - 1) // 2]:
            p = (i - 1) // 2
            h[i], h[p] = h[p], h[i]
            i, swaps = p, swaps + 1
    return swaps

def heapify_swaps(xs: list[int]) -> int:
    a, n, swaps = list(xs), len(xs), 0
    for i in range(n // 2 - 1, -1, -1):
        while True:
            l, r, m = 2 * i + 1, 2 * i + 2, i
            if l < n and a[l] < a[m]:
                m = l
            if r < n and a[r] < a[m]:
                m = r
            if m == i:
                break
            a[i], a[m] = a[m], a[i]
            i, swaps = m, swaps + 1
    return swaps

xs = list(range(1023, 0, -1))
print(push_swaps(xs))     # 8194
print(heapify_swaps(xs))  # 1013
```

## Max-heap of strings

You want to pop words in reverse alphabetical order using `heapq`. Negating works for numbers, but `-"pear"` is an error. What do you do?

**Answer:** Wrap each value in a small class whose `__lt__` is reversed, so the min-heap's "smallest" is the largest word. This works for any comparable type (strings, tuples, dates). For numbers alone, negation is still simpler.

```python
import heapq

class Rev:
    __slots__ = ("v",)
    def __init__(self, v):
        self.v = v
    def __lt__(self, other):
        return self.v > other.v

h = [Rev(w) for w in ["kiwi", "apple", "pear", "fig"]]
heapq.heapify(h)
print([heapq.heappop(h).v for _ in range(len(h))])  # ['pear', 'kiwi', 'fig', 'apple']
```

## Ties that crash

This works until two jobs share a priority. What error appears, and what is the one-line fix?

```python
import heapq
q = []
heapq.heappush(q, (1, {"id": "a"}))
heapq.heappush(q, (1, {"id": "b"}))
```

**Answer:** Tuples compare element by element. With equal priorities, Python compares the dicts and raises `TypeError: '<' not supported between instances of 'dict' and 'dict'`. Insert a unique, increasing sequence number between the priority and the payload: ties are then broken by arrival order (FIFO) and the payload is never compared.

```python
import heapq
from itertools import count

q, seq = [], count()
for prio, job in [(1, {"id": "a"}), (1, {"id": "b"}), (0, {"id": "c"})]:
    heapq.heappush(q, (prio, next(seq), job))
print([heapq.heappop(q)[2]["id"] for _ in range(3)])  # ['c', 'a', 'b']
```

## Leaderboard cutoff

Scores arrive one at a time. After each score, report the score needed to enter the top 3 (the current 3rd best), or `None` while fewer than 3 scores exist. Scores: 40, 75, 60, 90, 55, 80.

**Answer:** Keep a min-heap holding at most 3 scores; its root is the cutoff. A new score only enters if it beats the root, and `heapreplace` swaps it in with one sift. Cutoffs: None, None, 40, 60, 60, 75. Each score costs O(log 3), effectively constant, however long the stream.

```python
import heapq

top: list[int] = []
cutoffs = []
for s in [40, 75, 60, 90, 55, 80]:
    if len(top) < 3:
        heapq.heappush(top, s)
    elif s > top[0]:
        heapq.heapreplace(top, s)
    cutoffs.append(top[0] if len(top) == 3 else None)
print(cutoffs)  # [None, None, 40, 60, 60, 75]
```

## Merge sorted logs

Three servers each give you a log already sorted by timestamp. Produce one combined log in timestamp order without concatenating and re-sorting. What is the cost for N total lines across K logs?

**Answer:** Put the first line of each log into a min-heap keyed by `(timestamp, log index)`. Pop the smallest, emit it, and push the next line from the same log. The heap never holds more than K entries, so the total is O(N log K) time and O(K) extra space, versus O(N log N) for re-sorting.

```python
import heapq

logs = [
    [(1, "a: boot"), (7, "a: ok")],
    [(2, "b: boot"), (3, "b: warn"), (9, "b: ok")],
    [(5, "c: boot")],
]
heap = [(log[0][0], k, 0) for k, log in enumerate(logs) if log]
heapq.heapify(heap)
merged = []
while heap:
    ts, k, i = heapq.heappop(heap)
    merged.append(logs[k][i][1])
    if i + 1 < len(logs[k]):
        heapq.heappush(heap, (logs[k][i + 1][0], k, i + 1))
print(merged)  # ['a: boot', 'b: boot', 'b: warn', 'c: boot', 'a: ok', 'b: ok']
```

## Two heaps: trace the balance

Using the low max-heap / high min-heap layout (push into low, move low's root to high, move back if high is bigger), add 4, 10, 2, 7. After each add, list both halves and the middle value.

**Answer:** After 4: low `[4]`, high `[]`, middle 4. After 10: low `[4]`, high `[10]`, middle 7.0. After 2: low `[2, 4]`, high `[10]`, middle 4. After 7: low `[2, 4]`, high `[7, 10]`, middle 5.5. Low always holds the smaller half and is never smaller than high, so with an odd count the middle is low's root.

```python
import heapq

low: list[int] = []   # negated values: max-heap
high: list[int] = []
for x in [4, 10, 2, 7]:
    heapq.heappush(low, -x)
    heapq.heappush(high, -heapq.heappop(low))
    if len(high) > len(low):
        heapq.heappush(low, -heapq.heappop(high))
    mid = -low[0] if len(low) > len(high) else (-low[0] + high[0]) / 2
    print(sorted(-v for v in low), sorted(high), mid)
# [4] [] 4
# [4] [10] 7.0
# [2, 4] [10] 4
# [2, 4] [7, 10] 5.5
```

## Cancel a queued job

A print queue is a heap of `(priority, job_id)`. Users may cancel jobs. A teammate cancels with `q.remove(entry)` followed by `heapq.heapify(q)`. What does that cost, and what is cheaper?

**Answer:** `list.remove` is an O(N) scan and `heapify` is another O(N), so every cancel is linear. With lazy deletion, cancelling just records the id in a set (O(1)); `pop` discards cancelled entries when they reach the root. Each entry is popped at most once, so pops stay O(log N) amortized.

```python
import heapq

q = [(2, "j1"), (1, "j2"), (3, "j3"), (1, "j4")]
heapq.heapify(q)
cancelled = {"j2"}

def next_job() -> str | None:
    while q:
        _, job = heapq.heappop(q)
        if job not in cancelled:
            return job
    return None

print([next_job() for _ in range(4)])  # ['j4', 'j1', 'j3', None]
```

## Heap sort: build phase

To sort `[3, 1, 6, 5, 2, 4]` ascending in place, which kind of heap do you build, and what does the array look like right after the build phase?

**Answer:** A max-heap. Each round moves the largest remaining value to the end of the array, so the sorted part grows from the right with no extra memory. Sifting down from index 2, then 1, then 0 gives `[6, 5, 4, 1, 2, 3]`; five swap-and-sift rounds then finish the sort.

```python
def sift_down(a: list[int], i: int, n: int) -> None:
    while True:
        l, r, m = 2 * i + 1, 2 * i + 2, i
        if l < n and a[l] > a[m]:
            m = l
        if r < n and a[r] > a[m]:
            m = r
        if m == i:
            return
        a[i], a[m] = a[m], a[i]
        i = m

a = [3, 1, 6, 5, 2, 4]
for i in range(len(a) // 2 - 1, -1, -1):
    sift_down(a, i, len(a))
print(a)  # [6, 5, 4, 1, 2, 3]
for end in range(len(a) - 1, 0, -1):
    a[0], a[end] = a[end], a[0]
    sift_down(a, 0, end)
print(a)  # [1, 2, 3, 4, 5, 6]
```

## Prefix counts in O(P)

You need `count_prefix(p)`: how many stored words start with `p`. Collecting the subtree on every call is too slow. What do you store instead?

**Answer:** Keep a `passes` counter on every node and increment it on each node you walk through during insert. The answer is the counter on the prefix node, so a query costs O(P) no matter how many words match. The same trick gives "how many words end here" with a second counter.

```python
class Node:
    __slots__ = ("kids", "passes")
    def __init__(self):
        self.kids: dict[str, "Node"] = {}
        self.passes = 0

root = Node()
for w in ["app", "apple", "apply", "ape", "bat"]:
    node = root
    for ch in w:
        node = node.kids.setdefault(ch, Node())
        node.passes += 1

def count_prefix(p: str) -> int:
    node = root
    for ch in p:
        node = node.kids.get(ch)
        if node is None:
            return 0
    return node.passes

print(count_prefix("ap"))    # 4
print(count_prefix("appl"))  # 2
print(count_prefix("c"))     # 0
```

## Bug hunt: a prefix is not a word

After inserting only "card", `search("car")` returns True. Find the bug.

```python
def search(root, word):
    node = root
    for ch in word:
        if ch not in node.children:
            return False
        node = node.children[ch]
    return True
```

**Answer:** Reaching the last node only proves that some stored word *starts with* `word`. Exact search must also check the end-of-word marker. Returning `True` unconditionally turns `search` into `starts_with`.

```python
class Node:
    def __init__(self):
        self.children: dict[str, "Node"] = {}
        self.is_end = False

def insert(root: Node, word: str) -> None:
    node = root
    for ch in word:
        node = node.children.setdefault(ch, Node())
    node.is_end = True

def search(root: Node, word: str) -> bool:
    node = root
    for ch in word:
        if ch not in node.children:
            return False
        node = node.children[ch]
    return node.is_end

root = Node()
insert(root, "card")
print(search(root, "car"), search(root, "card"))  # False True
```

## Longest prefix match

A router stores bit-string prefixes and their next hop: `1 -> A`, `10 -> B`, `1011 -> C`, `0 -> D`. For an address, the most specific (longest) matching prefix wins. Which hop do `1010`, `10111`, and `111` get?

**Answer:** `1010 -> B`, `10111 -> C`, `111 -> A`. Walk the trie along the address bits and remember the value of the last terminal node you passed; stop when the next bit has no child. The walk is O(address length) regardless of table size, which is why routers use tries for this.

```python
root: dict = {}
for prefix, hop in [("1", "A"), ("10", "B"), ("1011", "C"), ("0", "D")]:
    node = root
    for bit in prefix:
        node = node.setdefault(bit, {})
    node["$"] = hop                       # terminal marker holds the value

def route(addr: str) -> str | None:
    node, best = root, None
    for bit in addr:
        node = node.get(bit)
        if node is None:
            break
        best = node.get("$", best)
    return best

print(route("1010"), route("10111"), route("111"))  # B C A
```

## Delete without collateral damage

A trie holds "to", "tea", "ted", and "ten" (7 nodes including the root). A naive delete removes every node on the path of the word. What breaks when you delete "tea" that way, and how many nodes should actually go?

**Answer:** The naive version removes `t` and `e` too, losing "to", "ted", and "ten". Only the `a` node should go: `e` still has children, and `t` leads to other words. Prune bottom-up and stop at the first node that has other children or ends another word. Deleting "to" afterwards removes just `o`.

```python
def build(words: list[str]) -> dict:
    root: dict = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = True
    return root

def delete(node: dict, word: str, i: int = 0) -> bool:
    if i == len(word):
        node.pop("$", None)
    elif word[i] in node and delete(node[word[i]], word, i + 1):
        del node[word[i]]
    return not node                       # empty: parent may remove it

def size(node: dict) -> int:
    return 1 + sum(size(c) for k, c in node.items() if k != "$")

root = build(["to", "tea", "ted", "ten"])
print(size(root))  # 7
delete(root, "tea")
print(size(root))  # 6
delete(root, "to")
print(size(root))  # 5
```
