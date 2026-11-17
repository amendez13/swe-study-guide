## When the next value comes from a heap

A heap is a complete binary tree in an array, and the root is the best item under one order. A min-heap's root is the smallest item. A max-heap's root is the largest. Push and pop each follow one path, so each costs O(log n). Reading the root costs O(1). Building from n unsorted items by sifting upward from the bottom costs O(n). The shape, the child indexes, and those sifts are the [Binary heap](../../07_Data_Structures_and_Algorithms/06_Heaps_and_Tries/), [Array representation](../../07_Data_Structures_and_Algorithms/06_Heaps_and_Tries/), [Heap insert (sift up)](../../07_Data_Structures_and_Algorithms/06_Heaps_and_Tries/), [Extract min (sift down)](../../07_Data_Structures_and_Algorithms/06_Heaps_and_Tries/), and [Bottom-up heapify](../../07_Data_Structures_and_Algorithms/06_Heaps_and_Tries/) cards.

Reach for the root when the statement asks for the k best, the k-th, repeated removal of the current smallest, a merge of sorted inputs, or a middle value kept current as numbers arrive. [Dijkstra's algorithm](../../07_Data_Structures_and_Algorithms/07_Graphs/) settles the unsettled vertex with the smallest distance. One minimum is a variable. The full order, once, is a sort. Python's `heapq` is a min-heap: after `heapify`, index 0 is the peek and the rest of the list is not sorted. Go 1.24's `src/runtime/time.go` keeps timers in a per-processor 4-ary min-heap (`timerHeapN` is 4; the parent of index `i` is `(i - 1) / 4`). libuv v1.x `src/heap-inl.h` is a binary min-heap, and `uv__next_timeout` reads that root. The four values below are exercise numbers.

```python
import heapq

pending = [4, 1, 7, 3]
heapq.heapify(pending)
print(pending, pending[0])
# [1, 3, 7, 4] 1
```

## A bounded heap of the k best

The k largest values from a scan of n values sit in a min-heap that never grows past k. The root is the smallest winner, so it is the value a newcomer has to beat. A larger newcomer replaces it through `heapreplace`. A smaller one is ignored. The k smallest values flip the heap: a max-heap, so the largest of the small set sits on top and a colder or smaller newcomer can evict it. [A heap for top-k](../07_Hard_Problems/) is that flipped scan for the k coldest hours. [Top-K with a bounded heap](../../07_Data_Structures_and_Algorithms/06_Heaps_and_Tries/) is the same cap. Python's `heapq` has no max-heap type, so the max-heap is stored as negated numbers.

Each of the n values does at most one sift on a heap of size k: O(n log k) time and O(k) extra memory. Sorting is O(n log n), simpler when k is close to n. The heap is the tool that can drop values on a stream. Fewer than k arrivals means the heap holds every arrival. An empty scan, or a k of 0, returns nothing. One minimum does not need this structure. In CPython 3.12, `heapq.nsmallest` uses `min` for a single item, `sorted` when the request is at least the input length, and otherwise a max-heap of the winners with an index so equal values are not compared further. The scores below are exercise numbers.

```python
import heapq


def k_largest(values: list[int], k: int) -> list[int]:
    if k <= 0:
        return []
    heap: list[int] = []
    for value in values:
        if len(heap) < k:
            heapq.heappush(heap, value)
        elif value > heap[0]:
            heapq.heapreplace(heap, value)
    return sorted(heap, reverse=True)


print(k_largest([4, 9, 2, 8, 7], 2))
print(k_largest([4, 9, 2, 8, 7], 0), k_largest([], 2), k_largest([4], 3))
# [9, 8]
# [] [] [4]
```

## The survivor you would drop

A heap of size k stores the survivors, and its root is the survivor you would drop first. That order is the reverse of the report. A report of "higher count first, and on a tie the earlier word" drops "lower count first, and on a tie the later word." A min-heap of `(count, word)` gets the count right and the tie wrong. Tuples compare from the left, so a later word looks larger, and replacing the root when the new tuple is greater treats the later word as the better one. On the exercise counts apple 2, fig 2, and pear 2, considered in that order with k of 2, the root after two pushes is apple. Pear compares greater, apple leaves, and the reversed pops are pear then fig.

The word has to be inverted inside the comparison. A class whose `__lt__` means "lower count, or the same count and a later word" makes the later word the smaller item, so it sits at the root. Replace the root only when the root is worse than the new item. The pops then come out worst-first, and the report is those pops reversed. Negating the count, as `(-count, word)`, is a different heap: it already pops in report order, because the minus flips the count and the word stays alphabetical. That shape cannot evict inside a heap of size k. A string has no negation. `-"pear"` raises `TypeError`. The counts below are exercise numbers.

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


def wrongly(pairs: list[tuple[str, int]], k: int) -> list[str]:
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


def keep(pairs: list[tuple[str, int]], k: int) -> list[str]:
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


pairs = [("apple", 2), ("fig", 2), ("pear", 2)]
print(wrongly(pairs, 2), keep(pairs, 2))
# ['pear', 'fig'] ['apple', 'fig']
```

## Heapify the counts, then pop k

When the distinct items already fit in memory, build one heap of all of them and pop k times. For the strings that occur most often, each heap item is `(-count, word)`. Counting N strings into U distinct pairs is O(N) time and O(U) memory. `heapify` is O(U), the bound on the [Bottom-up heapify](../../07_Data_Structures_and_Algorithms/06_Heaps_and_Tries/) card, not U separate pushes. Each pop is O(log U), so k pops are O(k log U). The total is O(N + k log U) time, and the heap holds every distinct word. The minus sign puts the higher count first. An equal count then compares the word in alphabetical order, so the earlier word pops first. The pop order is the report order. Nothing is reversed, and the word is not wrapped.

The size-k heap costs O(U log k) after the same count. Once k is at least 3 and still small beside U, U + k log U is the smaller bound. The bounds meet when k is a large fraction of U. The size-k heap is the one that runs on a stream, with O(k) heap memory past the counts. Use the full build when the words fit and `(-count, word)` is enough. If k exceeds U, pop U times. A k of 0 pops nothing. The exercise strings `pear`, `fig`, `apple`, `pear`, `fig`, `apple`, `fig` give fig three times and apple and pear twice, with apple the earlier tie.

```python
import heapq


def most_frequent(words: list[str], k: int) -> list[str]:
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    heap = [(-count, word) for word, count in counts.items()]
    heapq.heapify(heap)
    return [heapq.heappop(heap)[1] for _ in range(min(k, len(heap)))]


sample = ["pear", "fig", "apple", "pear", "fig", "apple", "fig"]
print(most_frequent(sample, 2), most_frequent(sample, 3), most_frequent(sample, 0))
# ['fig', 'apple'] ['fig', 'apple', 'pear'] []
```

## Merge k sorted inputs

K-way merge reads k sequences that are each already sorted and writes one sorted sequence. A min-heap holds the head of each sequence, so it holds at most k items. Pop the smallest head, write it, and push the next item from that same sequence. Each of the N items is pushed once and popped once. The time is O(N log k) and the heap uses O(k) extra memory. Concatenating and sorting is O(N log N). Pairwise merging is the same O(N log k) time: every round walks every item, and a balanced pairing has log k rounds. The [Merging sorted sequences](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card is the two-list merge and this heap. The [Priority queue with heapq](../../07_Data_Structures_and_Algorithms/06_Heaps_and_Tries/) card includes the library call.

`heapq.merge` is that heap. In CPython 3.12 it returns a generator, so listing the result is what pulls the values. It takes one value from each iterable up front and skips an iterable that is already empty. The heap entry is the value, an input index, and the iterator's `next`. Equal values are ordered by that index, and the merge does not need a further comparison. The inputs have to be sorted already. An unsorted input is not sorted by the merge. The lists below are exercise numbers.

```python
import heapq

print(list(heapq.merge([1, 4, 9], [2, 2, 8], [], [3])))
# [1, 2, 2, 3, 4, 8, 9]
```

## Two heaps and the size fix

A running median keeps the lower half in a max-heap and the upper half in a min-heap. In `heapq` the lower half is stored negated. Every lower value is less than or equal to every upper value, and the lower half has the same size as the upper half or one extra value. The median is the lower root when the lower half is longer, and the average of the two roots when the sizes match. That average is a float. [Two heaps (running median)](../../07_Data_Structures_and_Algorithms/06_Heaps_and_Tries/) and [Two heaps for a running median](../07_Hard_Problems/) push each arrival into the lower heap, move that root to the upper heap, and move it back if the upper half became longer. The placement below compares first, then repairs the sizes. Both placements keep the same two rules.

A value less than or equal to the lower root joins the lower half. A greater value joins the upper half. If the lower half is then more than one ahead, its root moves up. If the upper half is longer, its root moves down. An insert crosses at most once, so it is O(log n), and the read is O(1). Memory is O(n). The empty tracker has no median. Leaving the sizes wrong is the bug: pushing the exercise arrivals 1 and then 9 into the lower heap and never moving a root leaves 9 on top. The median of those two arrivals is 5.

```python
import heapq


def medians(values: list[int]) -> list[float]:
    low: list[int] = []
    high: list[int] = []
    out: list[float] = []
    for value in values:
        if not low or value <= -low[0]:
            heapq.heappush(low, -value)
        else:
            heapq.heappush(high, value)
        if len(low) > len(high) + 1:
            heapq.heappush(high, -heapq.heappop(low))
        elif len(high) > len(low):
            heapq.heappush(low, -heapq.heappop(high))
        if len(low) > len(high):
            out.append(float(-low[0]))
        else:
            out.append((-low[0] + high[0]) / 2)
    return out


stuck: list[int] = []
for value in [1, 9]:
    heapq.heappush(stuck, -value)
print(medians([1, 9]), -stuck[0])
# [1.0, 5.0] 9
```

## A second key for ties

`heapq` orders items with `<`. A tuple compares fields from the left and stops at the first difference, so the priority belongs in the first field. When two items can share that priority, the next field has to be something `<` can compare. A dict, a node, or any other payload in that field raises `TypeError` once the priorities match. An increasing counter from `itertools.count`, placed between the priority and the payload, never ties, so the payload is never compared. Equal priorities then come out in arrival order. `sched.Event` is this tuple: time, priority, sequence, action, argument, kwargs. The sequence comes from `count()`. At the same time, the smaller priority number runs first.

Numbers can be negated to flip a min-heap into a max-heap. Strings cannot. A wrapper whose `__lt__` encodes the order is the comparison a minus sign cannot write. libuv's v1.x `timer_less_than` is the same two-key rule: the earlier timeout wins, and equal timeouts compare `start_id`, which `uv_timer_start` copies from an increasing counter. CPython 3.12's `asyncio.TimerHandle.__lt__` compares only `_when`. `BaseEventLoop.call_later` documents that two callbacks set for the same time have no defined order. The job names below are exercise labels. The smaller priority number runs first.

```python
import heapq
from itertools import count

seq = count()
jobs: list[tuple[int, int, str]] = []
for priority, name in [(2, "mail"), (2, "page"), (1, "disk")]:
    heapq.heappush(jobs, (priority, next(seq), name))
print([heapq.heappop(jobs)[2] for _ in range(len(jobs))])
# ['disk', 'mail', 'page']
```

## The next value is in the next k + 1

A list is k-sorted when each value sits at most k indexes away from the index a full sort would give it. The smallest value not yet written is then inside the next k + 1 unread values. A value that belongs in the next output slot cannot have started more than k places further right. A min-heap of those k + 1 values keeps that smallest at the root. Pop it into the output, push the next unread value, and repeat. Every value enters the heap once, so the time is O(n log k) and the extra memory is O(k). Sorting the whole list is O(n log n), which is the bound you pay when you do not have the promise about k.

A window of k, rather than k + 1, is the off-by-one. On the exercise list `[3, 1, 4, 2]` with k of 2, the 2 sits two places after its sorted index. Width 2 writes `[1, 3, 2, 4]`. Width 3 writes `[1, 2, 3, 4]`. An in-place write is safe because the write index trails the read index by the window width, so the overwritten cell is already in the heap. A shorter list is the whole heap. The promise is part of the contract: a too-small k does not sort an arbitrary list, and a k of 0 is a window of one that only preserves a list already sorted.

```python
import heapq


def nearly_sorted(values: list[int], width: int) -> list[int]:
    data = list(values)
    window = data[:width]
    heapq.heapify(window)
    write = 0
    for read in range(width, len(data)):
        data[write] = heapq.heapreplace(window, data[read])
        write += 1
    while window:
        data[write] = heapq.heappop(window)
        write += 1
    return data


print(nearly_sorted([3, 1, 4, 2], 2))
print(nearly_sorted([3, 1, 4, 2], 3))
# [1, 3, 2, 4]
# [1, 2, 3, 4]
```

## The k strings that occur most

Return the k strings that occur most often. A higher count comes first. On a tie, the earlier word in alphabetical order comes first. Count the list, then keep a min-heap of size k in the drop order from the survivor card: a lower count is worse, and the same count with a later word is worse. The root is the word you would drop. A new word enters only when the root is worse than it. Pops come out worst-first, so reverse them. On the exercise list `pear`, `fig`, `apple`, `pear`, `fig`, `apple`, `fig`, the counts are fig 3, apple 2, and pear 2. Size 2 keeps fig and apple. The first pop is apple, and the reverse is fig then apple.

Forgetting the reverse returns apple then fig. A tuple `(count, word)` drops apple and keeps pear, the failure on the survivor card. The heapify card's `(-count, word)`, popped k times, returns fig then apple and does not reverse. Counting N strings is O(N). The size-k heap over U words is O(U log k). Memory is O(U) for the counts and O(k) for the heap. An empty list or a k of 0 returns nothing. A k larger than U returns every word, still in report order.

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


def top_k_words(words: list[str], k: int) -> list[str]:
    if k <= 0:
        return []
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    heap: list[Weaker] = []
    for word, count in counts.items():
        item = Weaker(count, word)
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif heap[0] < item:
            heapq.heapreplace(heap, item)
    out = [heapq.heappop(heap).word for _ in range(len(heap))]
    out.reverse()
    return out


sample = ["pear", "fig", "apple", "pear", "fig", "apple", "fig"]
print(top_k_words(sample, 2), top_k_words(sample, 3))
print(top_k_words([], 2), top_k_words(sample, 0), top_k_words(["fig", "pear"], 5))
# ['fig', 'apple'] ['fig', 'apple', 'pear']
# [] [] ['fig', 'pear']
```

## One sorted list from k sorted lists

Merge k linked lists, each already sorted, into one sorted list. This is k-way merge with a node at each head. The heap entry is the node's value, the list's index, and the node. The index sits before the node so two equal values never ask `heapq` to compare two nodes. That comparison raises `TypeError`. Skip a list that starts empty, or the first push stores `None`. A dummy node in front of the output gives every real node a predecessor, including the first, and `dummy.next` is `None` when every input was empty. [A dummy head when the head can change](../11_Linked_Lists/) is that node. The output reuses the input nodes. It does not copy their values into new nodes.

Each of the N nodes is pushed once and popped once, and the heap never holds more than one node per list. The time is O(N log k) and the extra memory is O(k). Pairwise merging of the lists is also O(N log k): each round walks every node, and there are log k rounds. The heap is the form to write when you want one pass and a dummy. The exercise lists are `1, 4, 7`, `2, 2`, an empty list, and `3, 8`. The two 2s are the tie the index has to absorb.

```python
import heapq


class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None) -> None:
        self.val = val
        self.next = nxt


def from_list(values: list[int]) -> ListNode | None:
    head: ListNode | None = None
    for value in reversed(values):
        head = ListNode(value, head)
    return head


def to_list(head: ListNode | None) -> list[int]:
    values: list[int] = []
    while head is not None:
        values.append(head.val)
        head = head.next
    return values


def merge_k(lists: list[ListNode | None]) -> ListNode | None:
    heap: list[tuple[int, int, ListNode]] = []
    for index, node in enumerate(lists):
        if node is not None:
            heapq.heappush(heap, (node.val, index, node))
    dummy = ListNode()
    tail = dummy
    while heap:
        _value, index, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next is not None:
            heapq.heappush(heap, (node.next.val, index, node.next))
    return dummy.next


rows = [from_list([1, 4, 7]), from_list([2, 2]), from_list([]), from_list([3, 8])]
print(to_list(merge_k(rows)))
print(to_list(merge_k([])), to_list(merge_k([None, None])), to_list(merge_k([from_list([4])])))
# [1, 2, 2, 3, 4, 7, 8]
# [] [] [4]
```

## The median as values arrive

Add integers one at a time and return the median after each add. The two heaps from the size-fix card are the whole structure. Compare the new value with the lower root, push it onto that side, then move one root if the sizes broke the rule. Read the lower root when it is the only middle, and average the two roots when the halves match. Keep the average as a float so an even count is not an integer division. The exercise arrivals are 4, then 1, then 7, then 2.

After 4 the lower root is 4, and the median is 4. After 1 the halves are `{1}` and `{4}`, and the average is 2.5. After 7 the lower half is `{1, 4}` and the upper root is 7, so the median is the lower root, 4. After 2 the halves are `{1, 2}` and `{4, 7}`, and the average is 3. An empty tracker returns `None` rather than a root it does not have. One arrival returns that arrival. Two arrivals return their average. Duplicates stay valid because the lower half may hold values equal to the upper root. Each add is O(log n) and each read is O(1). A sorted list of the arrivals so far would re-sort, or insert, on every add.

```python
import heapq


class RunningMedian:
    def __init__(self) -> None:
        self.low: list[int] = []
        self.high: list[int] = []

    def add(self, value: int) -> None:
        if not self.low or value <= -self.low[0]:
            heapq.heappush(self.low, -value)
        else:
            heapq.heappush(self.high, value)
        if len(self.low) > len(self.high) + 1:
            heapq.heappush(self.high, -heapq.heappop(self.low))
        elif len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def median(self) -> float | None:
        if not self.low:
            return None
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2


tracker = RunningMedian()
seen: list[float] = []
for value in [4, 1, 7, 2]:
    tracker.add(value)
    seen.append(tracker.median())
print(seen, RunningMedian().median())
# [4.0, 2.5, 4.0, 3.0] None
```

## Sort a list that is only k out of order

Each value in the list lies at most k indexes away from its sorted index. Sort the list. The window card is the reason a min-heap of width k + 1 is enough: the next output is the smallest of the next k + 1 unread values. Heapify that prefix, then walk the rest of the list. `heapreplace` writes the root into the output cell and pushes the newly read value in one sift. When the unread side is finished, pop the heap empty into the remaining cells. On the exercise list `[6, 5, 3, 2, 8, 10, 9]` the farthest move is 3, so k is 3 and the window holds 4. The sorted list is `[2, 3, 5, 6, 8, 9, 10]`.

The write index starts at 0 and the read index starts at k + 1, so an in-place write never covers a value the heap has not taken yet. A window of width k on a list that really did move k places drops a value that was still unread, which is the `[1, 3, 2, 4]` result on the window card. The time is O(n log k) and the extra memory is the O(k) window. An empty list stays empty. A single value stays that value, whatever k is, because the window is the whole list. A k of 0 only preserves a list that is already sorted. The promise has to be true. This pass does not discover k.

```python
import heapq


def sort_k_away(values: list[int], k: int) -> list[int]:
    data = list(values)
    window = data[: k + 1]
    heapq.heapify(window)
    write = 0
    for read in range(k + 1, len(data)):
        data[write] = heapq.heapreplace(window, data[read])
        write += 1
    while window:
        data[write] = heapq.heappop(window)
        write += 1
    return data


print(sort_k_away([6, 5, 3, 2, 8, 10, 9], 3))
print(sort_k_away([], 2), sort_k_away([4], 3), sort_k_away([1, 2, 3], 0))
# [2, 3, 5, 6, 8, 9, 10]
# [] [4] [1, 2, 3]
```

## Heap, sort, quickselect, or buckets

The question decides the tool. One minimum or one maximum is `min` or `max`: one pass, O(1) extra memory. Every value in order, once, is `sorted`, O(n log n) time. The k best, with k well below n, or a stream you will not store, is the size-k heap: O(n log k) time and O(k) extra memory. The k-th value alone, when the values are already in a list you may reorder and you do not need the other values in order, is [Quickselect](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/): expected O(n), worst case O(n^2). Keys that are small integers, such as scores from 0 through 100, are counting buckets, O(n + range) time, on the [Counting sort](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card. [When not to use a heap](../../07_Data_Structures_and_Algorithms/06_Heaps_and_Tries/) is this choice beside the heap operations. [A heap for top-k](../07_Hard_Problems/) is the coldest-hours case of the size-k row.

CPython 3.12 follows the same split inside `heapq.nlargest` and `heapq.nsmallest`. A count of 1 calls `max` or `min`. A count at least as large as a sized input calls `sorted`. Anything between those keeps a heap. Building a heap in order to read one root, or sorting in order to read one minimum, pays for an order the question did not ask for. The scores below are exercise numbers.

```python
import heapq

scores = [4, 9, 2, 8, 7]
print(min(scores), heapq.nlargest(2, scores), sorted(scores))
# 2 [9, 8] [2, 4, 7, 8, 9]
```
