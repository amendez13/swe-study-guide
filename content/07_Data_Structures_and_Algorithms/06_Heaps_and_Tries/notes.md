# Heaps and Tries

Heaps and tries are specialized tree structures that trade general-purpose flexibility for targeted efficiency. A heap gives you constant-time access to the minimum or maximum element and O(log N) insertion and extraction, making it the backbone of priority queues and algorithms like Dijkstra's shortest path and heap sort. A trie stores strings character by character so that shared prefixes are stored only once, enabling O(K) lookups and prefix-based queries that would require a full scan in a hash table.

## Key Points

- **Binary heap** - A complete binary tree where every parent satisfies the heap property relative to its children; the shape property (complete tree) guarantees O(log N) height without rebalancing.
- **Min-heap vs. max-heap** - Min-heap keeps the smallest element at the root (parent <= children); max-heap keeps the largest (parent >= children). Python's `heapq` is a min-heap; negate values for max-heap behavior.
- **Insert is bubble up** - Add the element at the end of the array, then swap upward until the heap property holds. O(log N) worst case, but usually fewer swaps in practice.
- **Extract is bubble down** - Remove the root, replace it with the last element, then swap downward with the smaller (min-heap) or larger (max-heap) child. O(log N).
- **Array representation** - Node at index i has left child at 2i+1, right child at 2i+2, parent at (i-1)//2. No pointers, excellent cache locality.
- **Bottom-up heapify is O(N)** - Building a heap by sifting down from the last non-leaf node is faster than N individual insertions because most nodes are near the bottom where sift-down cost is low.
- **`heapq` is the Python standard** - `heappush`, `heappop`, `heapify`, `nsmallest`, `nlargest`, and `merge` cover the common priority queue and top-K patterns.
- **Trie (prefix tree)** - An N-ary tree where edges represent characters and paths spell out stored strings; shared prefixes are stored once, making prefix queries natural.
- **Trie operations are O(K)** - Insert and search depend only on word length K, not on the number of stored words, so performance stays constant as the dictionary grows.
- **Tries vs. hash tables** - Hash tables win at exact-match lookups; tries win at prefix matching, autocomplete, sorted iteration, and avoiding hash collisions.

## Example

```python
import heapq

# --- Heap: task scheduler with priorities ---
class TaskScheduler:
    def __init__(self):
        self._heap: list[tuple[int, int, str]] = []
        self._counter = 0  # tiebreaker for equal priorities

    def add_task(self, task: str, priority: int) -> None:
        heapq.heappush(self._heap, (priority, self._counter, task))
        self._counter += 1

    def next_task(self) -> str:
        _, _, task = heapq.heappop(self._heap)
        return task

scheduler = TaskScheduler()
scheduler.add_task("write tests", 3)
scheduler.add_task("fix production bug", 1)
scheduler.add_task("code review", 2)

print("Task order:")
while scheduler._heap:
    print(f"  {scheduler.next_task()}")
# fix production bug, code review, write tests


# --- Trie: autocomplete system ---
class TrieNode:
    __slots__ = ("children", "is_end")
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end: bool = False

class Autocomplete:
    def __init__(self, words: list[str]):
        self.root = TrieNode()
        for word in words:
            self._insert(word)

    def _insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def suggest(self, prefix: str) -> list[str]:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        results: list[str] = []
        self._collect(node, list(prefix), results)
        return results

    def _collect(self, node: TrieNode, path: list[str], results: list[str]) -> None:
        if node.is_end:
            results.append("".join(path))
        for ch, child in sorted(node.children.items()):
            path.append(ch)
            self._collect(child, path, results)
            path.pop()

ac = Autocomplete(["python", "pytest", "pypi", "java", "javascript"])
print(f"\nAutocomplete 'py': {ac.suggest('py')}")
# ['pypi', 'pytest', 'python']
print(f"Autocomplete 'java': {ac.suggest('java')}")
# ['java', 'javascript']
print(f"Autocomplete 'go': {ac.suggest('go')}")
# []
```

The heap-based task scheduler shows the core priority queue pattern: push tasks with priorities, pop them in priority order. The trie-based autocomplete demonstrates prefix matching -- typing a few characters instantly narrows the suggestions to stored words sharing that prefix, regardless of dictionary size.
