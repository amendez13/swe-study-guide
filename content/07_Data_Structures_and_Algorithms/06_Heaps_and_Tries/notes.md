# Heaps and Tries

Heaps and tries are specialized tree structures that trade general-purpose flexibility for targeted efficiency. A heap gives you constant-time access to the minimum or maximum element and O(log N) insertion and extraction, making it the backbone of priority queues and algorithms like Dijkstra's shortest path and heap sort. A trie stores strings character by character so that shared prefixes are stored only once, enabling O(K) lookups and prefix-based queries that would require a full scan in a hash table.

## Key Points

- **Binary heap** - A complete binary tree where every parent satisfies the heap property relative to its children; the shape property guarantees O(log N) height without rebalancing.
- **Min-heap vs. max-heap** - Min-heap keeps the smallest element at the root (parent <= children); max-heap keeps the largest. Python's `heapq` is a min-heap; negate numbers (or wrap values with a reversed `__lt__`) for max-heap behavior.
- **Array representation** - Node at index i has left child at 2i+1, right child at 2i+2, parent at (i-1)//2. No pointers, excellent cache locality; leaves start at index n//2.
- **Heap insert (sift up)** - Append at the end, then swap upward while smaller than the parent. O(log N) worst case.
- **Extract min (sift down)** - Move the last element to the root, then swap downward with the smaller child (larger for a max-heap). O(log N).
- **Bottom-up heapify** - Sift down from the last non-leaf to the root; O(N) total, faster than N pushes (O(N log N)) because most nodes are near the bottom.
- **Priority queue ADT** - push, pop, peek, len. A heap gives O(log N) push/pop and O(1) peek; push `(priority, seq, item)` for FIFO ties and to avoid comparing payloads.
- **Priority queue with heapq** - `heappush`, `heappop`, `heapify`, `heappushpop`, `heapreplace`, `nsmallest`, `nlargest`, and `merge` operate on a plain list.
- **Top-K with a bounded heap** - K largest uses a size-K min-heap whose root is the bar to beat: O(N log K) time, O(K) space, works on streams.
- **Two heaps (running median)** - Lower half in a max-heap, upper half in a min-heap, sizes within one; the middle is read from the roots in O(1).
- **Decrease-key and lazy deletion** - Heaps cannot find arbitrary items fast; either keep a position map or push a new entry and skip stale ones on pop.
- **Heap sort** - Build a max-heap, then repeatedly swap the root to the end and sift down. O(N log N) worst case, O(1) extra space, not stable.
- **When not to use a heap** - One-off min, full sorting, search/range/ordered iteration, or small integer priorities each have a simpler or better structure.
- **Trie (prefix tree)** - An N-ary tree where edges are characters and root-to-node paths spell prefixes; shared prefixes are stored once.
- **Trie insert and search** - O(K) for a key of length K, independent of dictionary size. The end-of-word marker separates "car is a word" from "car is only a prefix".
- **Prefix collection (autocomplete)** - Walk to the prefix node in O(P), then DFS its subtree in sorted child order; keep a node cursor to advance one keystroke at a time.
- **Dict vs. array children** - Fixed arrays are fast and ordered but cost a slot per letter per node; dicts store only real edges and handle any alphabet. Radix trees compress single-child chains.
- **Trie deletion** - Clear `is_end`, then prune childless non-terminal nodes bottom-up, stopping at the first node another word still needs.
- **Trie vs. hash table** - Hash tables win at exact-match lookups; tries win at prefix queries, autocomplete, longest-prefix match, and sorted iteration.

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

## More practice

Work the original exercises on the **Drills** tab: read each prompt and snippet, commit to an answer, then open the card to check it. For background reading, open CTCI Chapter 4 on the private reader under `#binary-heaps-min-heaps-and-max-heaps` (with `#insert` and `#extract-minimum-element`) and `#tries-prefix-trees`. Trees and graphs from that chapter belong to the Trees and Graphs topics. Do not copy book text or solutions into these study files.
