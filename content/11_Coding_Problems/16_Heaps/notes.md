# Heaps

A heap answers "what is next" while the set keeps changing. The root is that next value. A size-k heap keeps the survivors and drops the weakest. A k-way merge keeps one head from each sorted input. Two heaps keep a median. A window of k + 1 sorts a list whose values barely moved. The mechanics of sift and the array layout stay in the heaps and tries topic. These notes are the choice, the tie, and the cost.

## Key Points

- **When the next value comes from a heap** — push and pop are O(log n), peek is O(1), and a bottom-up build is O(n). One minimum is a variable. The full order, once, is a sort.
- **A bounded heap of the k best** — the k largest sit in a min-heap of size k, so the root is the weakest winner. The scan is O(n log k) time and O(k) memory.
- **The survivor you would drop** — report order and drop order are opposites. A higher count, then an earlier word, means the heap's root is a lower count, then a later word. `(count, word)` gets the tie backwards.
- **Heapify the counts, then pop k** — `(-count, word)` already pops in report order. The build is O(U) and k pops are O(k log U). The size-k heap uses less heap memory and can run on a stream.
- **Merge k sorted inputs** — one head per sequence in a min-heap. Each of N items moves once: O(N log k) time and O(k) extra memory. `heapq.merge` is that heap, and it skips an empty input.
- **Two heaps and the size fix** — lower half in a max-heap, upper half in a min-heap, sizes equal or the lower half one ahead. An even count averages the two roots. Skipping the move leaves the wrong root.
- **A second key for ties** — a counter between the priority and the payload stops `heapq` from comparing the payload. Strings cannot be negated. A wrapper carries `__lt__`.
- **The next value is in the next k + 1** — if every value moved at most k places, the next output is the min of the next k + 1 unread values. A window of k drops a value that is still unread.
- **The k strings that occur most** — count, then a size-k heap in drop order, then reverse the pops. Empty and a k of 0 return nothing.
- **One sorted list from k sorted lists** — the heap entry is value, list index, node. The index keeps equal values from comparing nodes. A dummy head covers the empty result.
- **The median as values arrive** — compare with the lower root, then rebalance. The exercise arrivals 4, 1, 7, 2 read 4, 2.5, 4, and 3. An empty tracker returns `None`.
- **Sort a list that is only k out of order** — the window is k + 1. The write index trails the read index, so writing back into the list is safe. The time is O(n log k).
- **Heap, sort, quickselect, or buckets** — one extreme is `min`. The whole order is `sorted`. A stream of the k best is the size-k heap. The k-th value alone can be quickselect. Small integer keys are buckets.

## Example

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


print(top_k_words(["pear", "fig", "apple", "pear", "fig", "apple", "fig"], 2))
print(sort_k_away([6, 5, 3, 2, 8, 10, 9], 3))
# ['fig', 'apple']
# [2, 3, 5, 6, 8, 9, 10]
```

The word heap drops pear, the later of the two strings that occur twice, and the reverse puts fig first. The window of 4 puts the list that moved at most 3 places back into order. Both inputs are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the heap, the cost, and a Python check. None of them is a published problem from a book list.
