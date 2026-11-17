# Heaps

A heap answers "what is next" while the set keeps changing. The root is that next value. A size-k heap drops the weakest survivor, and the comparison has to be the drop order, not the report order. Heapify-then-pop is the other shape when every count fits. A k-way merge keeps one head from each sorted input. Two heaps keep a median only while a root moves after each insert. A window of `k + 1` sorts a list whose values barely moved. The sift and the array layout stay on the heaps and tries cards.

## Key Points

- **When the next value comes from a heap** — push and pop are O(log n), peek is O(1), and a bottom-up build sifts down from the last non-leaf in O(n). One minimum is a variable. The full order, once, is a sort.
- **The survivor you would drop** — report order and drop order are opposites. A higher count, then an earlier word, means the root is a lower count, then a later word. `(count, word)` gets the tie backwards.
- **Heapify the counts, then pop k** — `(-count, word)` already pops in report order. The build is O(U) and k pops are O(k log U). The size-k heap uses O(k) heap memory and can run on a stream.
- **One sorted list from k sorted lists** — one head per list. Each of N items moves once: O(N log k) time and O(k) extra memory. The list index sits in front of a node so equal values do not compare nodes.
- **The size fix after a direct push** — lower half in a max-heap, upper half in a min-heap, sizes equal or the lower half one ahead. An even count averages the two roots. Skipping the move leaves the wrong root.
- **The next value is in the next k + 1** — if every value moved at most k places, the next output is the min of the next `k + 1` unread values. A window of k drops a value that is still unread.
- **Heap, sort, quickselect, or buckets** — one extreme is `min`. The whole order is `sorted`. A stream of the k best is the size-k heap. The k-th value alone can be quickselect. Small integer keys are buckets.

## Example

```python
import heapq


def top_k_words(words: list[str], k: int) -> list[str]:
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    heap = [(-count, word) for word, count in counts.items()]
    heapq.heapify(heap)
    return [heapq.heappop(heap)[1] for _ in range(min(k, len(heap)))]


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

The word heap pops fig before apple, the earlier of the two strings that occur twice. The window of 4 puts the list that moved at most 3 places back into order. Both inputs are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the heap, the cost, and a Python check.
