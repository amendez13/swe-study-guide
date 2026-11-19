# Linked Lists

The node, the sentinel, and the reversal loop live on the Data Structures linked-list topic. This topic is the interview choice: save the next link before you overwrite it, put a dummy in front when the head can change, keep a fixed gap for the kth-last node, and pair a hash map with a doubly linked list when one structure cannot do every operation. These notes are those choices. They are not a catalog of published problems.

## Key Points

- **Pointer rewiring** — a node is a value plus `next`, and sometimes `prev` or `child`. Save `next` before you overwrite it, or the rest of the chain is unreachable. There is no `values[i]`. Reaching the kth node is a walk. Inserting after a node you hold is a few assignments. Deleting that node needs `prev`, unless you copy the successor, which the tail does not have. The Linux `list_head` rewires neighbors it already has. The mechanics cards use the field name `data`. These snippets use `val`.
- **Dummy head** — every real node, including the first, has a predecessor. The returned head is `dummy.next`. Assigning a local `head` leaves the caller on the old node. Empty in and a removal of the only node both fall out of that return.
- **Reverse a linked list** — save, point backward, advance. Iteration is O(1) extra memory. Recursion must set the old `next` to `None` or the two nodes cycle, and it spends a frame per node. LeetCode 206 allows 5000 nodes. The default recursion limit is 1000. A direct call returns on 999 nodes and raises `RecursionError` on 1000. One extra caller raises on 999.
- **Remove the kth last node** — the leader starts k nodes ahead and stops on the last node, so the trailer sits on the predecessor. On `[8, 3, 5, 1, 9]`, k = 2 leaves the trailer on `5`. k equal to the length leaves the trailer on the dummy and removes the head. Counting the length and walking `length - k` is the second pass. This gap does not change speed. The runner card does. LeetCode 19 promises `1 <= n <= length` and a non-empty list. This card also defines k outside that range.
- **Intersection of two lists** — switch lists at the end, or align the lengths, or store node identities. Equal values are not a shared node: the two `9`s ahead of a shared `6` are different objects. Both heads can be the shared node, and the loop returns it immediately. Replacing `None` with the other head before the loop sees it does not terminate. LeetCode 160 forbids cycles, allows repeated values, and requires the lists to stay as they were.
- **Least recently used cache** — the map finds the node and the sentinels order it. Get and an overwrite move the node and do not evict. A new key over capacity unlinks the oldest node and deletes its key. Writing only one direction leaves `prev` and `next` in disagreement. The miss is `None`. LeetCode 146 returns `-1`, which is free because its values are at least 0. Java's access-ordered `LinkedHashMap`, `OrderedDict.move_to_end`, and CPython's `functools.lru_cache` are this pairing.
- **Palindrome linked list** — find the middle, reverse the second half, compare, reverse it back. Version A on an even length is the second middle. The array copy is O(n) extra memory. LeetCode 234 starts at one node, limits values to digits 0 through 9, and does not require a restore.
- **Flatten child lists** — append each child chain at the tail, then scan into it, so one level finishes before the next. `50` is the `next` of `40`, so it is the same level. LeetCode 430 splices the child between a node and its `next`, which is depth-first, and it also maintains `prev`. The three-node shape disagrees: level order is `10, 20, 30`, and the splice is `10, 30, 20`.
- **Rewire, copy, gap, or map** — a Python list is the linear-memory baseline. A dummy stays in place when the head can change. The gap and the length count are both linear: 5 leader steps against 8 on the length pass. Identity, not value, decides a shared node. Empty, one node, and removing the head check the return value.

## Example

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None) -> None:
        self.val = val
        self.next = nxt


def from_list(values: list[int]) -> ListNode | None:
    head: ListNode | None = None
    for value in reversed(values):
        head = ListNode(value, head)
    return head


def to_list(head: ListNode | None) -> list[int]:
    values: list[int] = []
    while head is not None:
        values.append(head.val)
        head = head.next
    return values


def reverse_iter(head: ListNode | None) -> ListNode | None:
    prev = None
    curr = head
    while curr is not None:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev


def remove_kth(head: ListNode | None, k: int) -> ListNode | None:
    if k < 1:
        return head
    dummy = ListNode(0, head)
    lead = dummy
    for _ in range(k):
        if lead.next is None:
            return head
        lead = lead.next
    trail = dummy
    while lead.next is not None:
        lead = lead.next
        trail = trail.next
    trail.next = trail.next.next
    return dummy.next


class ChildNode:
    def __init__(self, val: int, nxt: "ChildNode | None" = None, child: "ChildNode | None" = None) -> None:
        self.val = val
        self.next = nxt
        self.child = child


def flatten_level(head: ChildNode | None) -> ChildNode | None:
    if head is None:
        return None
    tail = head
    while tail.next is not None:
        tail = tail.next
    curr = head
    while curr is not None:
        if curr.child is not None:
            tail.next = curr.child
            while tail.next is not None:
                tail = tail.next
            curr.child = None
        curr = curr.next
    return head


def child_values(head: ChildNode | None) -> list[int]:
    values: list[int] = []
    while head is not None:
        values.append(head.val)
        head = head.next
    return values


tiny = ChildNode(10, ChildNode(20), ChildNode(30))
print(to_list(reverse_iter(from_list([4, 1, 7]))), to_list(reverse_iter(from_list([]))))
print(to_list(remove_kth(from_list([8, 3, 5, 1, 9]), 2)), to_list(remove_kth(from_list([8]), 1)))
print(child_values(flatten_level(tiny)))
# [7, 1, 4] []
# [8, 3, 5, 9] []
# [10, 20, 30]
```

The reverse saves `next` before it points backward. The removal keeps a leader two nodes ahead and unlinks `1`. The child on `10` is appended after `20`, which is level order. The lists are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the rewiring, the cost, and a Python check. None of them is a published problem from a book list.
