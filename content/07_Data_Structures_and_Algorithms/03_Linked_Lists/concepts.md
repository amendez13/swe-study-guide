## Singly linked list: nodes chained by next pointers

A singly linked list is a sequence of nodes where each node holds a value and a reference to the next node. The last node points to `None`. Unlike arrays, there is no contiguous block of memory and no indexing. Inserting or removing at the head is O(1), but reaching the kth element requires walking k pointers, making random access O(k).

This structure matters because it is the foundation for stacks, queues, and many interview problems. Understanding how pointers connect nodes is the prerequisite for every other linked list technique.

```python
class Node:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

# Build: 1 -> 2 -> 3 -> None
head = Node(1, Node(2, Node(3)))
```

```mermaid
graph LR
    A["1"] -->|next| B["2"]
    B -->|next| C["3"]
    C -->|next| D["None"]
```

## Doubly linked list: bidirectional traversal

A doubly linked list adds a `prev` pointer to each node, so you can walk forward or backward. The main advantage is that given a reference to any node, you can remove it in O(1) without needing to find its predecessor first. This is why LRU caches pair a hash map with a doubly linked list.

The cost is extra memory per node and slightly more complex pointer updates on every insert and delete.

```python
class DNode:
    def __init__(self, data, prev=None, next=None):
        self.data = data
        self.prev = prev
        self.next = next
```

```mermaid
graph LR
    N["None"] <-->|prev| A["1"]
    A <-->|next/prev| B["2"]
    B <-->|next/prev| C["3"]
    C -->|next| M["None"]
```

## Head reference vs. wrapper class

The simplest representation of a linked list is a bare `head` variable pointing to the first node. This works, but any operation that changes the head (insert at front, delete the first element) must return the new head or use some other convention to propagate the change.

A wrapper class solves this by holding the head reference inside an object. Callers interact with the list object, and the head can change internally without the caller needing to track it. Most production code and most interview solutions benefit from this pattern.

```python
class LinkedList:
    def __init__(self):
        self.head = None

    def prepend(self, data):
        self.head = Node(data, self.head)

    def __iter__(self):
        cur = self.head
        while cur:
            yield cur.data
            cur = cur.next
```

## Node deletion: pointer surgery around the target

Deleting a node means making the previous node's `next` pointer skip over the target. The key edge case is deleting the head, where there is no previous node and the head reference itself must change. For a doubly linked list, you also update the `next` node's `prev` pointer.

Getting deletion wrong usually means either losing the rest of the list or leaking the node. Drawing the before-and-after pointer diagram on paper is the fastest way to verify correctness.

```python
def delete(self, target_data):
    if self.head and self.head.data == target_data:
        self.head = self.head.next
        return
    cur = self.head
    while cur.next:
        if cur.next.data == target_data:
            cur.next = cur.next.next  # skip the target
            return
        cur = cur.next
```

```mermaid
graph LR
    subgraph Before
        A1["A"] -->|next| B1["B"] -->|next| C1["C"]
    end
    subgraph After
        A2["A"] -->|next| C2["C"]
    end
```

## Inserting at head, tail, and middle

Insertion at the head is O(1): create a new node pointing to the current head, then update the head. Insertion at the tail is O(N) for a singly linked list because you must walk to the end, unless you maintain a tail pointer. Insertion in the middle requires finding the correct position first, then splicing the new node into the chain.

Each position has a different pointer update pattern. Head insertion changes one pointer. Middle insertion changes two. Keeping a tail pointer makes tail insertion O(1) but adds bookkeeping to every deletion.

```python
def insert_after(self, prev_node, data):
    """Insert a new node after prev_node."""
    new_node = Node(data, prev_node.next)
    prev_node.next = new_node

def append(self, data):
    """Insert at the tail. O(N) without a tail pointer."""
    if not self.head:
        self.head = Node(data)
        return
    cur = self.head
    while cur.next:
        cur = cur.next
    cur.next = Node(data)
```

## Runner (two-pointer) technique

The runner technique uses two pointers that move through the list at different speeds. The canonical use is finding the middle node: the slow pointer advances one step while the fast pointer advances two. When the fast pointer reaches the end, the slow pointer is at the midpoint.

This same idea generalizes to detecting cycles, finding the kth-to-last element, and interleaving list halves. Two-pointer solutions avoid the need for a first pass to count list length.

```python
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow  # middle node

# Example: 1 -> 2 -> 3 -> 4 -> 5
# slow visits: 1, 2, 3
# fast visits: 1, 3, 5
# returns node with data=3
```

```mermaid
graph LR
    A["1"] --> B["2"] --> C["3"] --> D["4"] --> E["5"] --> F["None"]

    S["slow"] -.->|"step 1"| A
    S -.->|"step 2"| B
    S -.->|"step 3"| C

    FA["fast"] -.->|"step 1"| A
    FA -.->|"step 2"| C
    FA -.->|"step 3"| E
```

## Cycle detection with Floyd's algorithm

Floyd's cycle detection uses the same fast/slow pointer setup. If the list contains a cycle, the fast pointer will eventually lap the slow pointer and they will meet. If there is no cycle, the fast pointer reaches `None`.

To find where the cycle starts, reset one pointer to the head after the meeting point. Then advance both pointers one step at a time. They will meet again at the cycle entrance. This works because of the mathematical relationship between the distances each pointer has traveled.

```python
def detect_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            # Cycle found. Find the start.
            slow = head
            while slow is not fast:
                slow = slow.next
                fast = fast.next
            return slow  # cycle start node
    return None  # no cycle
```

```mermaid
graph LR
    A["1"] --> B["2"] --> C["3"] --> D["4"] --> E["5"]
    E -->|"next (cycle)"| C

    S["slow"] -.-> C
    F["fast"] -.-> C
    note["They meet inside the cycle"]
```

## Recursive list processing

Many linked list operations have clean recursive formulations. Reversing a list, merging two sorted lists, and checking palindromes all decompose naturally: process the rest of the list, then handle the current node. The base case is usually `None` or a single node.

The tradeoff is stack space. Each recursive call adds a frame, so processing a list of N nodes uses O(N) stack space. Python's default recursion limit (around 1000) makes this a real constraint for long lists. For production code, iterative solutions are usually safer; for interviews, recursive solutions are often cleaner to reason about.

```python
def reverse(head):
    """Reverse a singly linked list recursively."""
    if head is None or head.next is None:
        return head
    new_head = reverse(head.next)
    head.next.next = head
    head.next = None
    return new_head
```

## Arrays vs. linked lists: choosing the right structure

Arrays give you O(1) random access and excellent cache locality because elements sit in contiguous memory. Linked lists give you O(1) insertion and deletion at known positions without shifting elements. Neither is universally better.

Use arrays when you need fast indexed access, binary search, or when the data fits naturally into a fixed-size block. Use linked lists when the dominant operations are insertions and deletions at arbitrary positions, when you cannot predict size in advance, or when you need to splice sequences together without copying. In practice, arrays (and dynamic arrays like Python lists) win most of the time because CPU caches strongly favor contiguous memory access.

| Operation            | Array  | Linked List |
|----------------------|--------|-------------|
| Access by index      | O(1)   | O(N)        |
| Insert/delete at head| O(N)   | O(1)        |
| Insert/delete at end | O(1)*  | O(1)**      |
| Search (unsorted)    | O(N)   | O(N)        |
| Cache performance    | High   | Low         |

\* Amortized for dynamic arrays. \** With a tail pointer.

## Sentinel (dummy) head node

A sentinel is a throwaway node placed in front of the real head. Because every real node now has a predecessor, deleting or inserting at the front follows the same code path as anywhere else, and the special "is this the head?" branch disappears. When you are done, the real head is `dummy.next`.

Reach for a sentinel whenever the head might change: removing matching values, merging, partitioning, or building a new list node by node. It costs one extra allocation and removes a whole class of off-by-one bugs.

```python
def remove_value(head, target):
    dummy = Node(None, head)
    prev = dummy
    while prev.next:
        if prev.next.data == target:
            prev.next = prev.next.next  # same code even for the old head
        else:
            prev = prev.next
    return dummy.next
```

```mermaid
graph LR
    D["dummy"] -->|next| A["7"] --> B["3"] --> C["7"] --> N["None"]
```

## Iterative in-place reversal

Reversing iteratively walks the list once with three references: `prev` (the already-reversed part), `cur` (the node being flipped), and `nxt` (a saved pointer to the rest). The order matters: save `cur.next` first, then point `cur` backward, then advance both. If you overwrite `cur.next` before saving it, the rest of the list is lost.

This runs in O(N) time and O(1) extra space, so it is the version to use when the list can be long. It is also a building block: reversing a sublist, reversing the second half, and reversing in groups all reuse the same three-pointer loop.

```python
def reverse_iter(head):
    prev, cur = None, head
    while cur:
        nxt = cur.next   # 1. save the rest
        cur.next = prev  # 2. flip this pointer
        prev = cur       # 3. grow the reversed part
        cur = nxt        # 4. move on
    return prev  # new head
```

## Merging two sorted lists

Two sorted lists merge into one sorted list by repeatedly attaching the smaller front node to a growing tail. A sentinel gives the tail a starting point, so there is no special case for choosing the first node. When one list runs out, attach the rest of the other in one step, since it is already sorted.

The merge reuses existing nodes, so it is O(A + B) time and O(1) extra space. It is the merge step of merge sort on linked lists, which is the usual way to sort a list in O(N log N) without random access.

```python
def merge_sorted(a, b):
    dummy = tail = Node(None)
    while a and b:
        if a.data <= b.data:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b  # attach the leftover run
    return dummy.next
```

## Split, reverse, and weave

Many medium list problems are three small steps chained together: find the middle with fast/slow pointers, cut the list into two halves, transform one half (often reverse it), then walk both halves together. Thinking in these steps keeps each loop short and testable on its own.

The cut is the step people forget. After finding the middle, set the end of the first half's `next` to `None`, or the two halves stay joined and later loops run forever or revisit nodes.

```python
def split_half(head):
    """Return (first, second). First gets the extra node on odd lengths."""
    slow, fast = head, head.next
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    second = slow.next
    slow.next = None  # the cut
    return head, second
```

## Doubly linked list with sentinels: O(1) unlink

A doubly linked list with two sentinels, `head` and `tail`, never has `None` neighbours for a real node. Unlinking any node is always the same two assignments, and inserting after the head is always four. Together with a hash map from key to node, this gives O(1) "move to front" and "drop the oldest", which is how an LRU cache is built.

The usual bug is updating pointers in the wrong order and losing a reference. Unlink first, then relink, and update both directions every time.

```python
class DList:
    def __init__(self):
        self.head, self.tail = DNode(None), DNode(None)
        self.head.next, self.tail.prev = self.tail, self.head

    def unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def push_front(self, node):
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node
```

```mermaid
graph LR
    H["head (sentinel)"] <--> A["A"] <--> B["B"] <--> T["tail (sentinel)"]
```

## Edge cases and test helpers

Most linked list bugs show up on the same short inputs: an empty list, one node, two nodes, an odd versus even length, and the operation touching the first or last node. Run every solution against these before trying a long example.

Two small helpers make that cheap: one builds a list from a Python list, and one turns a list back into a Python list so you can compare with `==`. Python has no built-in linked list; `collections.deque` is a doubly linked block list and is the right choice in real code when you only need fast ends.

```python
def build(values):
    head = None
    for v in reversed(values):
        head = Node(v, head)
    return head

def to_list(head):
    out = []
    while head:
        out.append(head.data)
        head = head.next
    return out

for case in ([], [1], [1, 2], [1, 2, 3]):
    assert to_list(reverse_iter(build(case))) == case[::-1]
```
