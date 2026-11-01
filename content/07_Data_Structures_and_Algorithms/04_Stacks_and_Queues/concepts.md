## Stack (LIFO)

A stack enforces last-in, first-out ordering. The four core operations -- `push`, `pop`, `peek`, and `is_empty` -- all run in O(1). Stacks model any situation where you need to reverse order or backtrack: undo history, browser back buttons, call stacks, and expression parsing.

The cleanest implementation uses a singly linked list, adding and removing from the head so every operation stays constant time without worrying about capacity.

```python
class StackNode:
    def __init__(self, val, nxt=None):
        self.val = val
        self.nxt = nxt

class Stack:
    def __init__(self):
        self._top = None

    def push(self, val):
        self._top = StackNode(val, self._top)

    def pop(self):
        if self._top is None:
            raise IndexError("pop from empty stack")
        val = self._top.val
        self._top = self._top.nxt
        return val

    def peek(self):
        if self._top is None:
            raise IndexError("peek at empty stack")
        return self._top.val

    def is_empty(self):
        return self._top is None
```

![Stack (LIFO): push(C) onto [B, A], then pop() returns C; linked-list view and O(1) operations](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-1-stack-lifo.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 1.*

## Stack implementation with arrays vs. linked lists

An array-backed stack tracks a top-of-stack index and stores elements in a contiguous buffer. It offers better cache locality than a linked list and avoids per-node allocation overhead, but must resize when it runs out of room (amortized O(1) append, same as Python's `list.append`). A linked-list-backed stack never needs resizing and has true worst-case O(1) for push and pop, but each node carries pointer overhead.

```python
# Array-backed stack (Python list as the backing store)
class ArrayStack:
    def __init__(self):
        self._data = []

    def push(self, val):
        self._data.append(val)       # amortized O(1)

    def pop(self):
        if not self._data:
            raise IndexError("pop from empty stack")
        return self._data.pop()      # O(1)

    def peek(self):
        if not self._data:
            raise IndexError("peek at empty stack")
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0
```

![Stack implementation: array-backed buffer with amortized growth vs. linked nodes relinked at _top, with a comparison table](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-2-array-vs-linked-list.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 2.*

In Python, `list` is the practical choice for stacks. Use the linked-list version when you need guaranteed O(1) without amortization or when you are building the data structure from scratch in an interview.

## Explicit stack for converting recursion to iteration

Any recursive algorithm can be converted to an iterative one by managing an explicit stack that holds the same state the call stack would. This matters when recursion depth is large enough to blow through Python's default 1000-frame limit or when you need finer control over traversal order.

The pattern: replace each recursive call with a push, and replace the function return with a pop. Here is iterative DFS on a graph.

```python
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        print(node)

        # Push neighbors in reverse so leftmost is processed first
        for neighbor in reversed(graph[node]):
            if neighbor not in visited:
                stack.append(neighbor)

    return visited
```

![Explicit stack vs. call stack: the same DFS moment shown as recursive frames and as an explicit list, the call-to-push and return-to-pop rule, and a step-by-step trace](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-3-recursion-to-iteration.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 3.*

The explicit stack version mirrors the recursive DFS exactly: each `stack.append` corresponds to a recursive call, and each `stack.pop` corresponds to returning from one.

## Stack for expression evaluation and bracket matching

Stacks are the natural tool for problems where you need to match something opened earlier: parentheses, HTML tags, postfix operators. The core insight is that the most recently opened item must be closed first -- exactly LIFO order.

```python
def is_balanced(expr: str) -> bool:
    """Return True if every bracket in expr is properly matched."""
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

# Examples
print(is_balanced("({[]})"))   # True
print(is_balanced("([)]"))     # False
print(is_balanced("(("))       # False
```

For postfix (reverse Polish) evaluation, push operands onto the stack; when you hit an operator, pop two operands, apply the operator, and push the result. The final value is the single element left on the stack.

![Bracket matching and postfix evaluation: stack snapshots for ({[]}), the ([)] failure, and 3 4 + 2 * evaluating to 14](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-4-expressions-and-brackets.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 4.*

## Min stack

A min stack augments the standard stack so that retrieving the current minimum is O(1) alongside the usual O(1) push and pop. The trick is to store the running minimum at each level: every time you push, record `min(new_val, current_min)`. When you pop, the previous minimum is already stored in the element below.

```python
class MinStack:
    def __init__(self):
        self._data = []  # each entry is (value, current_min)

    def push(self, val):
        current_min = min(val, self._data[-1][1]) if self._data else val
        self._data.append((val, current_min))

    def pop(self):
        if not self._data:
            raise IndexError("pop from empty stack")
        return self._data.pop()[0]

    def peek(self):
        return self._data[-1][0]

    def get_min(self):
        if not self._data:
            raise IndexError("min of empty stack")
        return self._data[-1][1]

# Usage
ms = MinStack()
for v in [5, 3, 7, 2, 8]:
    ms.push(v)
print(ms.get_min())  # 2
ms.pop()             # removes 8
ms.pop()             # removes 2
print(ms.get_min())  # 3
```

![Min stack: (value, running min) pairs through push 5, 3, 7, 2, 8 and two pops, plus the parallel min-stack variant](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-5-min-stack.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 5.*

An alternative approach uses a parallel stack that only pushes when a new minimum arrives, saving space when values rarely decrease. Both variants preserve O(1) for all operations.

## Queue (FIFO)

A queue enforces first-in, first-out ordering. The four core operations -- `enqueue`, `dequeue`, `peek`, and `is_empty` -- all run in O(1). Queues model any situation where requests must be served in arrival order: task scheduling, message passing, print spooling, and breadth-first search.

A linked-list implementation maintains pointers to both the front (for dequeue) and the back (for enqueue).

```python
class QueueNode:
    def __init__(self, val, nxt=None):
        self.val = val
        self.nxt = nxt

class Queue:
    def __init__(self):
        self._front = None
        self._back = None

    def enqueue(self, val):
        node = QueueNode(val)
        if self._back:
            self._back.nxt = node
        self._back = node
        if self._front is None:
            self._front = node

    def dequeue(self):
        if self._front is None:
            raise IndexError("dequeue from empty queue")
        val = self._front.val
        self._front = self._front.nxt
        if self._front is None:
            self._back = None
        return val

    def peek(self):
        if self._front is None:
            raise IndexError("peek at empty queue")
        return self._front.val

    def is_empty(self):
        return self._front is None
```

![Queue (FIFO): enqueue(D) at the back, dequeue() takes A from the front; linked-list view with _front and _back, and O(1) operations](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-6-queue-fifo.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 6.*

## Queue for BFS traversal

Breadth-first search processes nodes level by level, and a queue is what makes that possible. You dequeue the current node, process it, then enqueue all its unvisited neighbors. Because the queue is FIFO, all nodes at distance *d* are processed before any node at distance *d+1*.

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()       # O(1) with deque
        order.append(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order

# Example tree as adjacency list
tree = {
    1: [2, 3],
    2: [4, 5],
    3: [6],
    4: [], 5: [], 6: [],
}
print(bfs(tree, 1))  # [1, 2, 3, 4, 5, 6]
```

![BFS with a queue: tree colored by level, the queue mid-traversal holding two adjacent levels, and a full trace](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-7-queue-bfs.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 7.*

BFS also gives the shortest path in unweighted graphs because it explores nodes in order of their distance from the start.

## Two-stack queue

A queue can be built from two stacks. One stack (`in_stack`) receives all enqueues. When you need to dequeue and the second stack (`out_stack`) is empty, pour everything from `in_stack` into `out_stack`, which reverses the order so the oldest element is on top. Each element is moved at most once, giving amortized O(1) per operation.

```python
class TwoStackQueue:
    def __init__(self):
        self._in_stack = []
        self._out_stack = []

    def enqueue(self, val):
        self._in_stack.append(val)

    def _transfer(self):
        if not self._out_stack:
            while self._in_stack:
                self._out_stack.append(self._in_stack.pop())

    def dequeue(self):
        self._transfer()
        if not self._out_stack:
            raise IndexError("dequeue from empty queue")
        return self._out_stack.pop()

    def peek(self):
        self._transfer()
        if not self._out_stack:
            raise IndexError("peek at empty queue")
        return self._out_stack[-1]
```

![Two-stack queue: transfer from in_stack to out_stack reverses order; trace of enqueues and dequeues showing when transfers happen](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-8-two-stack-queue.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 8.*

This is a classic interview question. The amortized analysis works because each element is pushed and popped from each stack exactly once -- four total operations spread across its lifetime in the queue.

## Deque (double-ended queue)

A deque supports insertion and removal from both ends in O(1). It generalizes both stacks (use one end) and queues (use opposite ends). Python's `collections.deque` is the standard implementation, backed by a doubly linked list of fixed-size blocks.

```python
from collections import deque

d = deque()
d.append(1)        # add to right:  [1]
d.appendleft(0)    # add to left:   [0, 1]
d.append(2)        # add to right:  [0, 1, 2]
d.popleft()        # remove left:   [1, 2] → returns 0
d.pop()            # remove right:  [1]     → returns 2

# Bounded deque: keeps only the last N items
recent = deque(maxlen=3)
for i in range(5):
    recent.append(i)
print(list(recent))  # [2, 3, 4]
```

![Deque: append/pop at both ends, trace of the card code, maxlen dropping old items, stack vs queue disciplines, and the linked-block internals](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-9-deque.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 9.*

Use `deque` over `list` whenever you need O(1) operations on both ends. A `list.pop(0)` is O(N) because it shifts every element, while `deque.popleft()` is O(1). The `maxlen` parameter makes `deque` useful for sliding window problems and bounded buffers.

## Priority queue

A priority queue dequeues elements by priority rather than insertion order. The typical backing structure is a binary heap, which provides O(log N) insert and O(log N) extract-min (or max). Python's `heapq` module operates on a plain list as a min-heap, and `queue.PriorityQueue` adds thread safety on top.

```python
import heapq

tasks = []
heapq.heappush(tasks, (2, "low priority"))
heapq.heappush(tasks, (0, "urgent"))
heapq.heappush(tasks, (1, "normal"))

while tasks:
    priority, description = heapq.heappop(tasks)
    print(f"[{priority}] {description}")
# [0] urgent
# [1] normal
# [2] low priority
```

![Priority queue: FIFO vs priority serving order, heapq min-heap as tree and list, and costs vs unsorted and sorted lists](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-10-priority-queue.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 10.*

Priority queues appear in Dijkstra's shortest path, Huffman coding, task scheduling, and event-driven simulations. The heap internals are covered in the Heaps topic; the key idea here is that a priority queue is the interface and a heap is the implementation.

## Stack and queue as ADTs: contract first, implementation second

An abstract data type (ADT) is a promise about behavior, not storage. A stack promises "the item you get back is the one added most recently"; a queue promises "the item you get back is the one that has waited longest." Arrays, linked lists, ring buffers, and pairs of stacks are all ways to keep that promise -- interviewers usually want you to name the contract, then pick an implementation and state its costs.

Decide up front what happens on **underflow** (pop/dequeue on empty) and, for fixed-capacity versions, **overflow** (push/enqueue when full). Raising an exception is clearer than returning `None`, because `None` may be a legitimate stored value.

| Need | Python choice | Notes |
|------|---------------|-------|
| Stack | `list` (`append` / `pop`) | Amortized O(1) at the right end |
| Queue or deque | `collections.deque` | O(1) at both ends; `list.pop(0)` is O(N) |
| Queue shared between threads | `queue.Queue` | Locking, blocking `get`/`put`, optional `maxsize` |
| Priority order | `heapq` on a list | O(log N) push/pop; see the Heaps topic |

```python
from collections import deque

stack = []
stack.append("a"); stack.append("b")
print(stack.pop())       # b  (most recent)

q = deque()
q.append("a"); q.append("b")
print(q.popleft())       # a  (oldest)
```

![Stack and Queue ADT contracts with the implementations that satisfy them, underflow and overflow decisions, and the four-step interview answer](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-11-adt-contract.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 11.*

## Circular buffer (ring buffer) queue

A fixed-capacity queue can live in a plain array if the front and back indices wrap around with modulo arithmetic. Nothing ever shifts, so enqueue and dequeue are worst-case O(1) with no allocation -- the reason ring buffers show up in audio pipelines, network drivers, and log tails.

Track `head` (index of the oldest item) and `size`. The next free slot is `(head + size) % capacity`. Keeping an explicit `size` avoids the classic ambiguity where `head == tail` could mean either empty or full.

```python
class RingQueue:
    def __init__(self, capacity):
        self._buf = [None] * capacity
        self._head = 0
        self._size = 0

    def enqueue(self, val):
        if self._size == len(self._buf):
            raise OverflowError("queue full")
        self._buf[(self._head + self._size) % len(self._buf)] = val
        self._size += 1

    def dequeue(self):
        if self._size == 0:
            raise IndexError("dequeue from empty queue")
        val = self._buf[self._head]
        self._buf[self._head] = None          # drop the reference
        self._head = (self._head + 1) % len(self._buf)
        self._size -= 1
        return val

rq = RingQueue(3)
for v in "abc":
    rq.enqueue(v)
print(rq.dequeue())   # a
rq.enqueue("d")       # wraps into slot 0
print([rq.dequeue() for _ in range(3)])  # ['b', 'c', 'd']
```

![Ring buffer: RingQueue(3) snapshots with head and next-free indices, d wrapping into slot 0, the ring view, and full-buffer policies](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-12-ring-buffer.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 12.*

A variant overwrites the oldest item when full instead of raising -- that is exactly what `deque(maxlen=N)` gives you.

## Monotonic stack: next greater element

A monotonic stack keeps its contents sorted (for example, decreasing from bottom to top) by popping anything that would break the order before pushing. Each pop is a moment of discovery: the incoming item is the first one to the right that beats the popped item. Every index is pushed and popped at most once, so the whole scan is O(N) even though there is a loop inside a loop.

Store **indices**, not values, so you can write answers back into an output array and measure distances.

```python
def next_greater(nums):
    """For each position, the next value to the right that is larger, else -1."""
    result = [-1] * len(nums)
    stack = []                       # indices; their values are decreasing
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            result[stack.pop()] = x
        stack.append(i)
    return result

print(next_greater([2, 1, 5, 3, 4]))  # [5, 5, -1, 4, -1]
```

![Monotonic stack: bars with next-greater arrows, the stack trace for [2, 1, 5, 3, 4], the result, and variants](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-13-monotonic-stack.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 13.*

Recognize it when a problem asks for the "nearest larger/smaller to the left/right," spans, or anything bounded by the first taller bar. Flip `<` to `>` for next smaller; scan right-to-left for previous greater.

## Monotonic deque: sliding window maximum

The deque version of the same idea answers "max (or min) of every window of size k" in O(N). Keep indices in a deque whose values decrease from front to back. On each step: drop the front if it has slid out of the window, pop smaller values off the back (they can never be a future max while the newer, larger value is around), push the new index, and read the max from the front.

```python
from collections import deque

def window_max(nums, k):
    dq, out = deque(), []            # indices, values decreasing front→back
    for i, x in enumerate(nums):
        if dq and dq[0] <= i - k:
            dq.popleft()             # out of the window
        while dq and nums[dq[-1]] <= x:
            dq.pop()                 # dominated by x
        dq.append(i)
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

print(window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))  # [3, 3, 5, 5, 6, 7]
```

![Monotonic deque: window of size 3, step i=4 expiring the front and popping dominated values, and the full trace](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-14-monotonic-deque.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 14.*

A heap also works (O(N log k)), but the deque is the expected optimal answer. The pattern needs both ends -- pop from the back to keep order, pop from the front to expire -- which is why a plain stack or queue is not enough.

## Same loop, different frontier: stack vs. queue traversal

Graph and tree traversals share one skeleton: take an item from a **frontier**, process it, add its neighbors. The container you choose for the frontier decides the order. A queue gives BFS (nearest first, shortest paths in unweighted graphs). A stack gives a DFS order (go deep first, smaller frontier on wide graphs). A priority queue gives best-first search (Dijkstra, A*).

```python
from collections import deque

def traverse(graph, start, use_stack):
    frontier = deque([start])
    seen, order = {start}, []
    while frontier:
        node = frontier.pop() if use_stack else frontier.popleft()
        order.append(node)
        for nb in graph[node]:
            if nb not in seen:
                seen.add(nb)
                frontier.append(nb)
    return order

g = {1: [2, 3], 2: [4], 3: [5], 4: [], 5: []}
print(traverse(g, 1, use_stack=False))  # [1, 2, 3, 4, 5]  BFS
print(traverse(g, 1, use_stack=True))   # [1, 3, 5, 2, 4]  DFS-style
```

![Same traversal loop with a queue (BFS order 1 2 3 4 5) and a stack (order 1 3 5 2 4), plus the priority-queue variant](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-15-frontier.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 15.*

Marking nodes as seen when they are **added** (as here) keeps each node in the frontier once; marking them when **popped** is required if you need a true preorder DFS that matches the recursive version.

## Bounded and blocking queues: producers and consumers

In real systems a queue usually sits between code that produces work and code that consumes it. Giving the queue a **capacity** creates backpressure: when consumers fall behind, producers block (or are rejected) instead of growing memory without bound. Python's `queue.Queue(maxsize=N)` is a thread-safe bounded FIFO with blocking `put` and `get`; message brokers (SQS, RabbitMQ, Kafka) apply the same idea across machines.

```python
import queue
import threading

jobs = queue.Queue(maxsize=2)      # put() blocks when 2 items are waiting
results = []

def worker():
    while True:
        item = jobs.get()
        if item is None:           # sentinel: shut down
            break
        results.append(item * item)
        jobs.task_done()

t = threading.Thread(target=worker)
t.start()
for n in range(5):
    jobs.put(n)
jobs.join()                        # wait until every job is processed
jobs.put(None)
t.join()
print(results)  # [0, 1, 4, 9, 16]
```

![Bounded blocking queue: producer, queue.Queue(maxsize=2) and worker; empty, partly full and full states; shutdown sequence; full-queue policies](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues-16-bounded-queue.png)

*Source: [`diagrams/stacks-and-queues.drawio`](/content/07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/diagrams/stacks-and-queues.drawio), page 16.*

Interview talking points: choose a capacity, decide what happens when full (block, drop, or reject), and use a sentinel or a close signal so consumers can exit cleanly.
