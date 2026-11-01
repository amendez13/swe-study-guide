# Linked Lists — Drills

Original mini-drills for linked list pointer skills. Each card is one exercise: read the prompt and snippet, commit to an answer, then check it. Each Answer has a short Python solution that runs on its own (it defines the small `Node`, `build`, and `to_list` helpers it needs). No copyrighted book text.

## Pointer order: what gets lost?

This version of `insert_after` swaps the two assignments. Starting from `1 -> 2 -> 3`, what does the list look like after `insert_after(head, 9)`?

```python
def insert_after(prev_node, data):
    new_node = Node(data)
    prev_node.next = new_node
    new_node.next = prev_node.next
```

**Answer:** `1 -> 9 -> 9 -> 9 ...` forever. After the first assignment, `prev_node.next` already points at the new node, so the second line makes the new node point at itself, and `2 -> 3` is unreachable. Always wire the new node to the rest of the list first, then point the predecessor at it.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def insert_after(prev_node, data):
    prev_node.next = Node(data, prev_node.next)  # new node grabs the rest first

head = Node(1, Node(2, Node(3)))
insert_after(head, 9)
cur, out = head, []
while cur:
    out.append(cur.data)
    cur = cur.next
print(out)  # [1, 9, 2, 3]
```

## Head deletion: why didn't it change?

The caller runs `delete_first(head)` on `1 -> 2 -> 3` and then prints the list starting from `head`. What prints, and how do you fix it without a wrapper class?

```python
def delete_first(head):
    if head:
        head = head.next
```

**Answer:** It still prints `1 -> 2 -> 3`. Reassigning the parameter `head` only changes the local name; the caller's variable still points at node 1. Return the new head and make the caller reassign it (or use a wrapper class or a sentinel).

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def delete_first(head):
    return head.next if head else None

head = Node(1, Node(2, Node(3)))
head = delete_first(head)  # caller must reassign
print(head.data, head.next.data, head.next.next)  # 2 3 None
```

## Sentinel: remove every match

Remove every node whose value equals `target`, including runs at the head (`7 -> 7 -> 3 -> 7 -> 5`, target 7 gives `3 -> 5`). Write it with no special head branch. What is the time and space cost?

**Answer:** Put a dummy node before the head and only advance `prev` when you keep a node. Unlinking a match leaves `prev` where it is, so back-to-back matches are handled too. O(N) time, O(1) extra space.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def build(xs):
    head = None
    for x in reversed(xs):
        head = Node(x, head)
    return head

def to_list(h):
    out = []
    while h:
        out.append(h.data)
        h = h.next
    return out

def remove_all(head, target):
    dummy = prev = Node(None, head)
    while prev.next:
        if prev.next.data == target:
            prev.next = prev.next.next
        else:
            prev = prev.next
    return dummy.next

print(to_list(remove_all(build([7, 7, 3, 7, 5]), 7)))  # [3, 5]
print(to_list(remove_all(build([7, 7]), 7)))           # []
```

## Trace the three-pointer reversal

Run the loop on `1 -> 2 -> 3`. What are `prev` and `cur` (by value) at the end of each iteration, and what is returned?

```python
def reverse_iter(head):
    prev, cur = None, head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
    return prev
```

**Answer:** After iteration 1: `prev=1, cur=2` (and `1 -> None`). After 2: `prev=2, cur=3` (`2 -> 1`). After 3: `prev=3, cur=None` (`3 -> 2 -> 1`). It returns node 3, the new head. One pass, O(N) time, O(1) space.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def reverse_iter(head):
    prev, cur = None, head
    while cur:
        nxt = cur.next
        cur.next = prev
        print("prev", cur.data, "cur", nxt.data if nxt else None)
        prev, cur = cur, nxt
    return prev

new_head = reverse_iter(Node(1, Node(2, Node(3))))
print("head", new_head.data)  # head 3
```

## Reverse only positions left..right

Reverse the nodes from position `left` to `right` (1-based) in one pass, leaving the rest in place. For `1 -> 2 -> 3 -> 4 -> 5` with `left=2, right=4`, the result is `1 -> 4 -> 3 -> 2 -> 5`. Which node do you need to remember before the reversed block?

**Answer:** Remember the node just before position `left` (a sentinel covers `left=1`). Then repeatedly take the node after the block's original first node and move it to the front of the block. That is `right - left` moves, O(N) time, O(1) space.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def build(xs):
    head = None
    for x in reversed(xs):
        head = Node(x, head)
    return head

def to_list(h):
    out = []
    while h:
        out.append(h.data)
        h = h.next
    return out

def reverse_between(head, left, right):
    dummy = Node(None, head)
    before = dummy
    for _ in range(left - 1):
        before = before.next
    first = before.next  # ends up as the block's last node
    for _ in range(right - left):
        moved = first.next
        first.next = moved.next
        moved.next = before.next
        before.next = moved
    return dummy.next

print(to_list(reverse_between(build([1, 2, 3, 4, 5]), 2, 4)))  # [1, 4, 3, 2, 5]
print(to_list(reverse_between(build([1, 2, 3]), 1, 3)))        # [3, 2, 1]
```

## Merge two sorted lists

Merge `1 -> 4 -> 6` and `2 -> 3 -> 7 -> 8` into one sorted list by relinking nodes, not by creating new ones. What happens to `7 -> 8` once the first list runs out, and what is the extra space?

**Answer:** Result `1 -> 2 -> 3 -> 4 -> 6 -> 7 -> 8`. When the first list is exhausted, the remaining `7 -> 8` is already sorted, so one assignment attaches it. O(A + B) time, O(1) extra space.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def build(xs):
    head = None
    for x in reversed(xs):
        head = Node(x, head)
    return head

def to_list(h):
    out = []
    while h:
        out.append(h.data)
        h = h.next
    return out

def merge_sorted(a, b):
    dummy = tail = Node(None)
    while a and b:
        if a.data <= b.data:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next

print(to_list(merge_sorted(build([1, 4, 6]), build([2, 3, 7, 8]))))
# [1, 2, 3, 4, 6, 7, 8]
```

## Which middle on an even length?

For `1 -> 2 -> 3 -> 4`, which node does each loop stop on? Which version would you use to split a list into two halves?

```python
# Version A
slow = fast = head
while fast and fast.next:
    slow, fast = slow.next, fast.next.next

# Version B
slow, fast = head, head.next
while fast and fast.next:
    slow, fast = slow.next, fast.next.next
```

**Answer:** Version A stops on 3 (the second middle). Version B stops on 2 (the first middle). For splitting, use B: `slow` is the last node of the first half, so `slow.next = None` cuts cleanly into `1 -> 2` and `3 -> 4`. On odd lengths both stop on the true middle.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def build(xs):
    head = None
    for x in reversed(xs):
        head = Node(x, head)
    return head

def middle_a(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow.data

def middle_b(head):
    slow, fast = head, head.next
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow.data

print(middle_a(build([1, 2, 3, 4])), middle_b(build([1, 2, 3, 4])))      # 3 2
print(middle_a(build([1, 2, 3, 4, 5])), middle_b(build([1, 2, 3, 4, 5])))  # 3 3
```

## How long is the loop?

Fast and slow pointers have already met inside a cycle. How do you count the number of nodes in the cycle, and what does it cost?

**Answer:** Keep one pointer at the meeting node and walk the other around until it comes back, counting steps. Every node on the cycle is visited once, so it is O(C) extra time and O(1) space, on top of the O(N) detection.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def cycle_length(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            length, cur = 1, slow.next
            while cur is not slow:
                length += 1
                cur = cur.next
            return length
    return 0  # no cycle

nodes = [Node(i) for i in range(6)]
for a, b in zip(nodes, nodes[1:]):
    a.next = b
nodes[-1].next = nodes[2]  # 0 1 [2 3 4 5] loops back to 2
print(cycle_length(nodes[0]))  # 4
```

## Rotate right by k

Rotate `1 -> 2 -> 3 -> 4 -> 5` right by `k=2` to get `4 -> 5 -> 1 -> 2 -> 3`. What should happen when `k` is larger than the length, say `k=7`?

**Answer:** Only `k % n` matters, so `k=7` on 5 nodes is the same as `k=2`. Find the length and the tail in one pass, close the list into a ring, then walk `n - k % n` steps from the tail and cut there. O(N) time, O(1) space.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def build(xs):
    head = None
    for x in reversed(xs):
        head = Node(x, head)
    return head

def to_list(h):
    out = []
    while h:
        out.append(h.data)
        h = h.next
    return out

def rotate_right(head, k):
    if not head or not head.next:
        return head
    n, tail = 1, head
    while tail.next:
        tail, n = tail.next, n + 1
    k %= n
    if k == 0:
        return head
    tail.next = head  # make a ring
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None  # cut the ring
    return new_head

print(to_list(rotate_right(build([1, 2, 3, 4, 5]), 2)))  # [4, 5, 1, 2, 3]
print(to_list(rotate_right(build([1, 2, 3, 4, 5]), 7)))  # [4, 5, 1, 2, 3]
```

## Odd positions first, then even

Regroup a list so nodes at positions 1, 3, 5, ... come first, followed by positions 2, 4, 6, ..., keeping relative order within each group. `10 -> 20 -> 30 -> 40 -> 50` becomes `10 -> 30 -> 50 -> 20 -> 40`. Can you do it with O(1) extra space?

**Answer:** Yes. Keep two running tails, `odd` and `even`, and remember the head of the even chain. Each step links `odd` past one even node and `even` past one odd node. At the end, attach the even chain after the last odd node. O(N) time, O(1) space.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def build(xs):
    head = None
    for x in reversed(xs):
        head = Node(x, head)
    return head

def to_list(h):
    out = []
    while h:
        out.append(h.data)
        h = h.next
    return out

def odd_even(head):
    if not head:
        return head
    odd, even = head, head.next
    even_head = even
    while even and even.next:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = even_head
    return head

print(to_list(odd_even(build([10, 20, 30, 40, 50]))))  # [10, 30, 50, 20, 40]
```

## Weave the ends together

Reorder `1 -> 2 -> 3 -> 4 -> 5` into `1 -> 5 -> 2 -> 4 -> 3` (first, last, second, second-to-last, ...) in place. Which three steps do you chain?

**Answer:** Split at the first middle, reverse the second half, then alternate one node from each half. The cut after splitting is essential, or the weave loops forever. O(N) time, O(1) space.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def build(xs):
    head = None
    for x in reversed(xs):
        head = Node(x, head)
    return head

def to_list(h):
    out = []
    while h:
        out.append(h.data)
        h = h.next
    return out

def weave_ends(head):
    if not head or not head.next:
        return head
    slow, fast = head, head.next
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    second, slow.next = slow.next, None  # split and cut
    prev = None
    while second:  # reverse second half
        nxt = second.next
        second.next = prev
        prev, second = second, nxt
    first, second = head, prev
    while second:  # weave
        a_next, b_next = first.next, second.next
        first.next, second.next = second, a_next
        first, second = a_next, b_next
    return head

print(to_list(weave_ends(build([1, 2, 3, 4, 5]))))  # [1, 5, 2, 4, 3]
print(to_list(weave_ends(build([1, 2, 3, 4]))))     # [1, 4, 2, 3]
```

## Move to front in a doubly linked list

You keep recently used items in a doubly linked list with `head` and `tail` sentinels, most recent first. Write `touch(node)` that moves an existing node to the front in O(1). Why do the sentinels matter?

**Answer:** Unlink the node from its neighbours, then insert it right after `head`. With sentinels, every real node always has a non-`None` `prev` and `next`, so there are no special cases for the first or last real node. Add a dict from key to node and you have the core of an LRU cache.

```python
class DNode:
    def __init__(self, data):
        self.data, self.prev, self.next = data, None, None

class Recent:
    def __init__(self):
        self.head, self.tail = DNode(None), DNode(None)
        self.head.next, self.tail.prev = self.tail, self.head

    def _unlink(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def push_front(self, node):
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node

    def touch(self, node):
        self._unlink(node)
        self.push_front(node)

    def items(self):
        cur, out = self.head.next, []
        while cur is not self.tail:
            out.append(cur.data)
            cur = cur.next
        return out

r = Recent()
nodes = {k: DNode(k) for k in "abc"}
for k in "abc":
    r.push_front(nodes[k])
print(r.items())  # ['c', 'b', 'a']
r.touch(nodes["a"])
print(r.items())  # ['a', 'c', 'b']
```

## Recursion depth on a long list

This recursive length works on short lists. What happens on a list of 5,000 nodes in CPython with default settings, and what is the fix?

```python
def length(node):
    return 0 if node is None else 1 + length(node.next)
```

**Answer:** It raises `RecursionError`. Each node adds a stack frame and the default limit is about 1,000. Raising the limit only moves the problem; the fix is an iterative loop, which is O(N) time and O(1) space.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def length_rec(node):
    return 0 if node is None else 1 + length_rec(node.next)

def length_iter(node):
    n = 0
    while node:
        n, node = n + 1, node.next
    return n

head = None
for i in range(5000):
    head = Node(i, head)

try:
    length_rec(head)
except RecursionError:
    print("RecursionError")
print(length_iter(head))  # 5000
```

## Print backwards without reversing

Print the values of `1 -> 2 -> 3` in reverse order without changing any pointers. Give a recursive version and an iterative one. What extra space does each use?

**Answer:** Recursion prints after the recursive call returns, so the deepest node prints first; that uses O(N) call stack. The iterative version pushes values onto a list used as a stack, which is also O(N) space. Without O(N) space you would have to reverse the list, print, and reverse it back.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def print_reverse_rec(node):
    if node is None:
        return
    print_reverse_rec(node.next)
    print(node.data, end=" ")

def print_reverse_iter(node):
    stack = []
    while node:
        stack.append(node.data)
        node = node.next
    while stack:
        print(stack.pop(), end=" ")

head = Node(1, Node(2, Node(3)))
print_reverse_rec(head)
print()  # 3 2 1
print_reverse_iter(head)
print()  # 3 2 1
```

## Swap adjacent pairs

Swap every two adjacent nodes by relinking them (not by swapping values): `1 -> 2 -> 3 -> 4 -> 5` becomes `2 -> 1 -> 4 -> 3 -> 5`. How many pointers change per pair?

**Answer:** Three per pair: the node before the pair, the first node, and the second node. A sentinel gives the first pair a "before" node. The odd last node stays put. O(N) time, O(1) space.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

def build(xs):
    head = None
    for x in reversed(xs):
        head = Node(x, head)
    return head

def to_list(h):
    out = []
    while h:
        out.append(h.data)
        h = h.next
    return out

def swap_pairs(head):
    dummy = before = Node(None, head)
    while before.next and before.next.next:
        a, b = before.next, before.next.next
        before.next, a.next, b.next = b, b.next, a
        before = a
    return dummy.next

print(to_list(swap_pairs(build([1, 2, 3, 4, 5]))))  # [2, 1, 4, 3, 5]
```

## Appending N items: cost with and without a tail

Building a list by calling an `append` that walks to the end each time, what is the total cost of N appends? What changes with a tail pointer?

```python
def append(head, data):
    if head is None:
        return Node(data)
    cur = head
    while cur.next:
        cur = cur.next
    cur.next = Node(data)
    return head
```

**Answer:** The k-th append walks k - 1 nodes, so the total is 0 + 1 + ... + (N - 1) = N(N - 1)/2, which is O(N²). Keeping a tail pointer makes each append O(1) and the whole build O(N). Alternatively, prepend and reverse once at the end.

```python
class Node:
    def __init__(self, data, next=None):
        self.data, self.next = data, next

class TailList:
    def __init__(self):
        self.head = self.tail = None

    def append(self, data):
        node = Node(data)
        if self.tail:
            self.tail.next = node
        else:
            self.head = node
        self.tail = node

def walk_steps(n):
    return sum(range(n))  # steps for n walk-to-end appends

lst = TailList()
for i in range(5):
    lst.append(i)
print(lst.head.data, lst.tail.data)  # 0 4
print(walk_steps(1000))              # 499500 steps vs 1000 with a tail
```
