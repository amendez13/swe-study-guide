# Stacks and Queues

Stacks and queues are the two fundamental ordered-access data structures. A stack enforces last-in, first-out (LIFO) order; a queue enforces first-in, first-out (FIFO) order. Both provide O(1) core operations and appear constantly in algorithm design -- stacks drive DFS, expression parsing, and undo systems, while queues drive BFS, task scheduling, and message passing. Mastering when to reach for each one is more important than memorizing their implementations.

## Key Points

- **Stack = LIFO, Queue = FIFO** - Stacks process the most recent item first; queues process the oldest item first. This single difference determines which problems each one solves.
- **All core operations are O(1)** - Push, pop, peek, and is_empty for stacks; enqueue, dequeue, peek, and is_empty for queues. If an implementation breaks this, something is wrong.
- **Array vs. linked-list backing** - Array-backed stacks (Python `list`) have better cache locality and amortized O(1) push. Linked-list-backed stacks have true worst-case O(1) without resizing. Choose based on whether you need guaranteed latency or practical speed.
- **Stacks convert recursion to iteration** - Replace recursive calls with explicit pushes and returns with pops. This avoids stack overflow on deep input and gives you control over traversal order.
- **Stacks solve matching and nesting problems** - Balanced parentheses, HTML tag validation, postfix evaluation, and any problem where the most recently opened thing must be closed first.
- **Min stack tracks the minimum in O(1)** - Store the running minimum alongside each element so popping automatically restores the previous minimum. Classic interview pattern.
- **Queues power BFS** - Breadth-first search works because FIFO ordering guarantees nodes at distance d are processed before nodes at distance d+1, yielding shortest paths in unweighted graphs.
- **Two-stack queue is amortized O(1)** - Push to one stack, pour into the other on demand. Each element moves at most once, so the amortized cost per operation is constant.
- **Deque generalizes both** - Python's `collections.deque` supports O(1) insert and remove from both ends, making it suitable for stacks, queues, and sliding-window problems. Always prefer it over `list` when you need `popleft`.
- **Priority queue is ordered by priority, not arrival** - Backed by a heap, it provides O(log N) insert and extract. Used in Dijkstra's algorithm, scheduling, and any scenario where the next item to process depends on a computed priority rather than when it arrived.

## Example

```python
from collections import deque

# ----- Stack: balanced bracket checker -----
def is_balanced(expr: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in expr:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return len(stack) == 0

print(is_balanced("{[()]}"))  # True
print(is_balanced("{[(])}"))  # False

# ----- Queue: BFS level-order traversal -----
tree = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [], "E": [], "F": [],
}

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return result

print(bfs(tree, "A"))  # ['A', 'B', 'C', 'D', 'E', 'F']

# ----- Min stack: O(1) minimum retrieval -----
class MinStack:
    def __init__(self):
        self._data = []  # (value, current_min)

    def push(self, val):
        cur_min = min(val, self._data[-1][1]) if self._data else val
        self._data.append((val, cur_min))

    def pop(self):
        return self._data.pop()[0]

    def get_min(self):
        return self._data[-1][1]

ms = MinStack()
for v in [5, 3, 7, 2, 8]:
    ms.push(v)
print(ms.get_min())  # 2
ms.pop()             # removes 8
ms.pop()             # removes 2
print(ms.get_min())  # 3
```

This example demonstrates the three most interview-relevant patterns: stacks for bracket matching, queues for BFS traversal, and the min-stack augmentation for O(1) minimum tracking.
