# Stacks and Queues — Drills

Original mini-drills for stack and queue skills. Each card is one exercise: read the prompt and snippet, commit to an answer, then check it. Each Answer has a short Python solution that runs on its own. No copyrighted book text.

## Trace it: LIFO vs. FIFO

The same five values go into a stack and a queue. What does each loop print?

```python
from collections import deque

s, q = [], deque()
for v in [1, 2, 3, 4, 5]:
    s.append(v)
    q.append(v)
s.pop(); q.popleft()
s.append(6); q.append(6)
print([s.pop() for _ in range(3)])
print([q.popleft() for _ in range(3)])
```

**Answer:** The stack prints `[6, 4, 3]` and the queue prints `[2, 3, 4]`. The stack's first pop removed 5 (newest), then 6 went on top. The queue's first `popleft` removed 1 (oldest), and 6 joined the back, so the next three out are 2, 3, 4.

```python
from collections import deque

s, q = [], deque()
for v in [1, 2, 3, 4, 5]:
    s.append(v)
    q.append(v)
s.pop(); q.popleft()          # stack drops 5, queue drops 1
s.append(6); q.append(6)
print([s.pop() for _ in range(3)])      # [6, 4, 3]
print([q.popleft() for _ in range(3)])  # [2, 3, 4]
```

## The list.pop(0) trap

This BFS is correct but slow on a graph with a million nodes. Why, and what is the one-line fix?

```python
def bfs(graph, start):
    queue, seen, order = [start], {start}, []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for nb in graph[node]:
            if nb not in seen:
                seen.add(nb)
                queue.append(nb)
    return order
```

**Answer:** `list.pop(0)` shifts every remaining element left, so each dequeue is O(N) and the whole BFS can degrade to O(V²). Use `collections.deque` and `popleft()`, which is O(1), restoring O(V + E).

```python
from collections import deque

def bfs(graph, start):
    queue, seen, order = deque([start]), {start}, []
    while queue:
        node = queue.popleft()            # O(1)
        order.append(node)
        for nb in graph[node]:
            if nb not in seen:
                seen.add(nb)
                queue.append(nb)
    return order

g = {0: [1, 2], 1: [3], 2: [3], 3: []}
print(bfs(g, 0))  # [0, 1, 2, 3]
```

## Empty peek: why returning None is a bug

A teammate writes `peek` to return `None` on an empty stack. A caller stores optional values, some of which are `None`. What goes wrong, and what should `peek` do instead?

```python
class Stack:
    def __init__(self):
        self._data = []
    def push(self, v):
        self._data.append(v)
    def peek(self):
        return self._data[-1] if self._data else None
```

**Answer:** After `push(None)`, `peek()` returns `None` -- indistinguishable from "empty." The caller cannot tell a stored `None` from underflow. Raise an exception on empty (and offer `is_empty()` for callers who want to check first).

```python
class Stack:
    def __init__(self):
        self._data = []
    def push(self, v):
        self._data.append(v)
    def is_empty(self):
        return not self._data
    def peek(self):
        if not self._data:
            raise IndexError("peek at empty stack")
        return self._data[-1]

s = Stack()
s.push(None)
print(s.peek(), s.is_empty())   # None False
s._data.clear()
try:
    s.peek()
except IndexError as e:
    print("error:", e)          # error: peek at empty stack
```

## Postfix evaluation: the operand-order bug

This postfix evaluator gets `"8 3 -"` wrong. What does it return, and what is the fix?

```python
def eval_postfix(tokens):
    stack = []
    for t in tokens.split():
        if t in "+-*/":
            a, b = stack.pop(), stack.pop()
            stack.append({"+": a + b, "-": a - b, "*": a * b, "/": a / b}[t])
        else:
            stack.append(int(t))
    return stack.pop()
```

**Answer:** It returns `-5`. The first pop is the **right** operand (pushed last), so `a` is 3 and `b` is 8. Pop into `right` first, then `left`, and compute `left op right`. Order matters for `-` and `/`; `+` and `*` hide the bug.

```python
def eval_postfix(tokens):
    ops = {
        "+": lambda l, r: l + r,
        "-": lambda l, r: l - r,
        "*": lambda l, r: l * r,
        "/": lambda l, r: int(l / r),   # truncate toward zero
    }
    stack = []
    for t in tokens.split():
        if t in ops:
            right = stack.pop()
            left = stack.pop()
            stack.append(ops[t](left, right))
        else:
            stack.append(int(t))
    if len(stack) != 1:
        raise ValueError("malformed expression")
    return stack[0]

print(eval_postfix("8 3 -"))          # 5
print(eval_postfix("3 4 + 2 *"))      # 14
print(eval_postfix("7 2 /"))          # 3
```

## Collapse adjacent duplicate pairs

Repeatedly delete any two equal adjacent characters until none remain. `"abbaca"` → `"ca"` (remove `bb`, then the new neighbors `aa`). Do it in one left-to-right pass.

**Answer:** Use the stack as "the answer so far." For each character, if it equals the top, pop (the pair cancels); otherwise push. Cancellations that expose new neighbors are handled automatically because the new top is the previous survivor. O(N) time, O(N) space.

```python
def collapse_pairs(s):
    stack = []
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)

print(collapse_pairs("abbaca"))   # ca
print(repr(collapse_pairs("aabbcc")))  # ''
print(repr(collapse_pairs("abba")))  # ''
```

## Simplify a Unix path

Normalize an absolute path: `"."` means stay, `".."` means go up one level (never above root), and repeated slashes collapse. `"/home//alex/./docs/../notes/"` → `"/home/alex/notes"`.

**Answer:** Split on `/` and treat the directory chain as a stack: skip empty parts and `.`, pop on `..` if not already at root, otherwise push. Join with `/` and prefix a single slash. O(N).

```python
def simplify(path):
    stack = []
    for part in path.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return "/" + "/".join(stack)

print(simplify("/home//alex/./docs/../notes/"))  # /home/alex/notes
print(simplify("/../.."))                         # /
print(simplify("/a/b/../../c"))                   # /c
```

## Decode nested repeats

Expand strings like `"2[ab3[c]]"` → `"abcccabccc"`. Counts can have several digits; brackets nest.

**Answer:** On `[`, push the current partial string and the pending count, then start fresh. On `]`, pop them and set `current = previous + count * current`. Digits accumulate into the count; letters append to `current`. Each character is handled once, plus the cost of building the output.

```python
def decode(s):
    stack, current, count = [], "", 0
    for ch in s:
        if ch.isdigit():
            count = count * 10 + int(ch)
        elif ch == "[":
            stack.append((current, count))
            current, count = "", 0
        elif ch == "]":
            prev, k = stack.pop()
            current = prev + current * k
        else:
            current += ch
    return current

print(decode("2[ab3[c]]"))   # abcccabccc
print(decode("10[x]"))       # xxxxxxxxxx
print(decode("a2[b]c"))      # abbc
```

## Next greater element

For each value, find the next value to its right that is strictly larger, or `-1`. `[4, 1, 2, 6, 3]` → `[6, 2, 6, -1, -1]`. The double loop is O(N²); do it in O(N).

**Answer:** Monotonic stack of indices whose values decrease bottom→top. When a new value is larger than the top's value, it is that index's answer: pop and record, repeat, then push the new index. Each index is pushed and popped once, so O(N).

```python
def next_greater(nums):
    res = [-1] * len(nums)
    stack = []                                # indices, decreasing values
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            res[stack.pop()] = x
        stack.append(i)
    return res

print(next_greater([4, 1, 2, 6, 3]))   # [6, 2, 6, -1, -1]
print(next_greater([5, 4, 3]))         # [-1, -1, -1]
```

## Largest rectangle in a histogram

Bars have width 1 and heights `[2, 1, 5, 6, 2, 3]`. What is the area of the largest axis-aligned rectangle that fits under the bars, and how do you find it in O(N)?

**Answer:** Area 10 (heights 5 and 6, width 2, height 5). Keep a stack of indices with increasing heights. When a shorter bar arrives, each popped bar has found its right boundary (the current index) and its left boundary is the new stack top, so its widest rectangle is `height * (i - left - 1)`. A sentinel height 0 at the end flushes the stack. Each bar is pushed and popped once.

```python
def largest_rectangle(heights):
    stack, best = [], 0                      # indices, increasing heights
    for i, h in enumerate(heights + [0]):    # sentinel flushes the stack
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best

print(largest_rectangle([2, 1, 5, 6, 2, 3]))  # 10
print(largest_rectangle([3, 3, 3]))           # 9
```

## Sliding window maximum

Return the maximum of every window of size `k`. For `[9, 2, 4, 1, 7, 3]` and `k = 3` the answer is `[9, 4, 7, 7]`. Beat the O(N·k) rescan.

**Answer:** Monotonic deque of indices with decreasing values. Each step: pop the front if it left the window, pop the back while its value is ≤ the new value (it can never win again), append the new index, and once the first full window is reached, the front is the max. O(N) total.

```python
from collections import deque

def window_max(nums, k):
    dq, out = deque(), []
    for i, x in enumerate(nums):
        if dq and dq[0] <= i - k:
            dq.popleft()
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

print(window_max([9, 2, 4, 1, 7, 3], 3))   # [9, 4, 7, 7]
print(window_max([1, 2, 3], 1))            # [1, 2, 3]
```

## Ring buffer: is it empty or full?

This ring queue tracks only `head` and `tail`. After enqueuing three items into a capacity-3 buffer, `head == tail == 0`. What does `is_empty()` report, and how do you fix the design?

```python
class Ring:
    def __init__(self, cap):
        self.buf, self.head, self.tail = [None] * cap, 0, 0
    def enqueue(self, v):
        self.buf[self.tail] = v
        self.tail = (self.tail + 1) % len(self.buf)
    def is_empty(self):
        return self.head == self.tail
```

**Answer:** It reports `True` even though the buffer is full -- `head == tail` means both "empty" and "full." Fix it by keeping an explicit `size` (or by always leaving one slot unused). With `size`, full is `size == cap`, empty is `size == 0`, and enqueue raises on full.

```python
class Ring:
    def __init__(self, cap):
        self.buf, self.head, self.size = [None] * cap, 0, 0
    def is_empty(self):
        return self.size == 0
    def is_full(self):
        return self.size == len(self.buf)
    def enqueue(self, v):
        if self.is_full():
            raise OverflowError("full")
        self.buf[(self.head + self.size) % len(self.buf)] = v
        self.size += 1
    def dequeue(self):
        if self.is_empty():
            raise IndexError("empty")
        v, self.buf[self.head] = self.buf[self.head], None
        self.head = (self.head + 1) % len(self.buf)
        self.size -= 1
        return v

r = Ring(3)
for v in "xyz":
    r.enqueue(v)
print(r.is_empty(), r.is_full())   # False True
print(r.dequeue(), r.dequeue())    # x y
```

## Keep only the last N log lines

A service wants the most recent 3 log lines in memory at all times, discarding older ones automatically. Write an O(1)-per-line version two ways: with the standard library and with a hand-rolled overwrite-oldest ring.

**Answer:** `deque(maxlen=3)` drops from the left whenever you append past capacity. The hand-rolled version writes at `next_slot`, advances it modulo capacity, and caps `size` at capacity; reading starts at the oldest slot, which is `next_slot` once the buffer is full.

```python
from collections import deque

lines = ["boot", "load", "ready", "req 1", "req 2"]

tail = deque(maxlen=3)
for line in lines:
    tail.append(line)
print(list(tail))    # ['ready', 'req 1', 'req 2']

class LastN:
    def __init__(self, n):
        self.buf, self.next_slot, self.size = [None] * n, 0, 0
    def add(self, item):
        self.buf[self.next_slot] = item
        self.next_slot = (self.next_slot + 1) % len(self.buf)
        self.size = min(self.size + 1, len(self.buf))
    def items(self):
        start = (self.next_slot - self.size) % len(self.buf)
        return [self.buf[(start + i) % len(self.buf)] for i in range(self.size)]

ln = LastN(3)
for line in lines:
    ln.add(line)
print(ln.items())    # ['ready', 'req 1', 'req 2']
```

## Swap the frontier: what order now?

Traverse this graph from `A`, marking nodes seen when they are added. What order comes out with a queue, and what order with a stack?

```python
graph = {"A": ["B", "C"], "B": ["D"], "C": ["E", "F"], "D": [], "E": [], "F": []}
```

**Answer:** Queue (BFS): `A B C D E F` -- level by level. Stack: `A C F E B D` -- it always expands the most recently added node, so it dives into `C`'s branch (last neighbor pushed) before returning to `B`. Push neighbors in reverse if you want left-first DFS order.

```python
from collections import deque

graph = {"A": ["B", "C"], "B": ["D"], "C": ["E", "F"], "D": [], "E": [], "F": []}

def order(start, use_stack):
    frontier, seen, out = deque([start]), {start}, []
    while frontier:
        node = frontier.pop() if use_stack else frontier.popleft()
        out.append(node)
        for nb in graph[node]:
            if nb not in seen:
                seen.add(nb)
                frontier.append(nb)
    return " ".join(out)

print(order("A", use_stack=False))  # A B C D E F
print(order("A", use_stack=True))   # A C F E B D
```

## BFS one level at a time

Return a tree's values grouped by depth: for the tree below, `[[1], [2, 3], [4, 5, 6]]`. How do you know where one level ends without storing depths?

```python
tree = {1: [2, 3], 2: [4, 5], 3: [6], 4: [], 5: [], 6: []}
```

**Answer:** At the start of each round, the queue holds exactly one level. Snapshot `len(queue)`, dequeue that many nodes into the current level, and enqueue their children for the next round. O(N) time; the queue holds at most one level plus the next.

```python
from collections import deque

tree = {1: [2, 3], 2: [4, 5], 3: [6], 4: [], 5: [], 6: []}

def levels(root):
    out, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):         # exactly the current level
            node = q.popleft()
            level.append(node)
            q.extend(tree[node])
        out.append(level)
    return out

print(levels(1))   # [[1], [2, 3], [4, 5, 6]]
```

## In-order traversal without recursion

Print a binary search tree's values in sorted order using an explicit stack (no recursion), for a tree built from `[5, 3, 8, 1, 4, 9]`.

**Answer:** Walk left as far as possible, pushing each node. When you cannot go left, pop a node, visit it, then move to its right child and repeat. The stack holds the "ancestors still waiting to be visited," which is exactly what the recursive call stack would hold. O(N) time, O(h) space.

```python
class TreeNode:
    def __init__(self, val):
        self.val, self.left, self.right = val, None, None

def insert(root, val):
    if root is None:
        return TreeNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    return root

def inorder(root):
    out, stack, cur = [], [], root
    while stack or cur:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        out.append(cur.val)
        cur = cur.right
    return out

root = None
for v in [5, 3, 8, 1, 4, 9]:
    root = insert(root, v)
print(inorder(root))   # [1, 3, 4, 5, 8, 9]
```

## Count requests in the last 3 seconds

`ping(t)` is called with non-decreasing timestamps in milliseconds and returns how many pings happened in `[t - 3000, t]`. For pings at 1, 100, 3001, 3002 the returns are 1, 2, 3, 3.

**Answer:** Keep timestamps in a queue. On each ping, append `t`, then pop from the front while the oldest is older than `t - 3000`. The queue length is the answer. Each timestamp enters and leaves once, so amortized O(1) per call; memory is bounded by the busiest 3-second window.

```python
from collections import deque

class RecentCounter:
    def __init__(self, window_ms=3000):
        self.window, self.q = window_ms, deque()
    def ping(self, t):
        self.q.append(t)
        while self.q[0] < t - self.window:
            self.q.popleft()
        return len(self.q)

rc = RecentCounter()
print([rc.ping(t) for t in [1, 100, 3001, 3002]])  # [1, 2, 3, 3]
```
