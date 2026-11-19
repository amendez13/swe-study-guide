# Linked Lists

Linked lists store data in nodes connected by pointers rather than in contiguous memory. They trade away random access for efficient insertion and deletion at arbitrary positions, and they form the backbone of stacks, queues, LRU caches, and many classic interview problems. The core skill is fluent pointer manipulation: knowing which references to update, in what order, and what edge cases to guard against.

## Key Points

- **Each node holds data and a pointer** - A singly linked list node points to the next node; a doubly linked list node also points to the previous node, enabling O(1) removal given a reference.
- **Head and tail operations differ in cost** - Inserting or deleting at the head is O(1), but reaching the tail of a singly linked list is O(N) unless you maintain a tail pointer.
- **A wrapper class prevents head-tracking bugs** - Wrapping the head pointer in a LinkedList object gives callers a stable reference even when the head changes.
- **Deletion requires updating the predecessor** - Skip the target node by setting `prev.next = target.next`; always handle the head-deletion edge case separately.
- **The two-pointer technique eliminates counting passes** - A fast pointer (2 steps) and slow pointer (1 step) find the midpoint, detect cycles, and locate the kth-to-last node in a single traversal.
- **Floyd's algorithm detects and locates cycles** - If fast and slow pointers meet, a cycle exists; resetting one pointer to the head and advancing both by one finds the cycle start.
- **Recursive solutions are elegant but stack-limited** - Reversing, merging, and checking palindromes decompose recursively, but O(N) stack depth hits Python's recursion limit on long lists.
- **Arrays usually win unless insertion dominates** - Contiguous memory gives arrays superior cache performance; prefer linked lists only when frequent splicing at arbitrary positions is the bottleneck.
- **A sentinel node removes head special cases** - Put a dummy node before the head so every real node has a predecessor; return `dummy.next` at the end.
- **Iterative reversal is save, flip, advance** - Keep `prev`, `cur`, and a saved `nxt`; it runs in O(1) extra space and is the base for sublist and group reversals.
- **Merging sorted lists is a tail-append loop** - Attach the smaller front node to a sentinel-backed tail, then attach whatever is left in one step.
- **Split, transform, and weave** - Find the middle, cut with `slow.next = None`, reverse or process one half, then walk both halves together.
- **Doubly linked list plus sentinels gives O(1) unlink** - Paired with a hash map, this is the core of an LRU cache.
- **Test the tiny cases first** - Empty, one node, two nodes, odd and even length, and changes at the head or tail catch most pointer bugs.

## Example

```python
class Node:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next


class LinkedList:
    def __init__(self):
        self.head = None

    def prepend(self, data):
        self.head = Node(data, self.head)

    def delete(self, target):
        if self.head and self.head.data == target:
            self.head = self.head.next
            return
        cur = self.head
        while cur and cur.next:
            if cur.next.data == target:
                cur.next = cur.next.next
                return
            cur = cur.next

    def find_middle(self):
        slow = fast = self.head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        return slow.data if slow else None

    def __iter__(self):
        cur = self.head
        while cur:
            yield cur.data
            cur = cur.next


ll = LinkedList()
for val in [5, 4, 3, 2, 1]:
    ll.prepend(val)

print("List:", list(ll))         # [1, 2, 3, 4, 5]
print("Middle:", ll.find_middle())  # 3

ll.delete(3)
print("After deleting 3:", list(ll))  # [1, 2, 4, 5]
```

The example builds a singly linked list, finds the middle node with the two-pointer technique, and deletes a node by pointer surgery. These three operations cover the core mechanics that more complex linked list problems build on.

## More practice

Work the original exercises on the **Drills** tab: read each prompt and snippet, commit to an answer, then open the card to check it. For more linked list practice, open CTCI Chapter 2 on the private reader (`#chapter-2-linked-lists`, with background under `#creating-a-linked-list`, `#deleting-a-node-from-a-singly-linked-list`, `#the-runner-technique`, and `#recursive-problems`); the chapter's interview questions live under `#interview-questions_2`. Work the problems there; do not copy book text or solutions into these study files.
