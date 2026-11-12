# Linked Lists — Drills

Original drills for rewiring a list: a dummy head, a fixed gap, a map plus a doubly linked list, and a child list flattened by level. Each answer has an approach, a cost, and Python. The lists are exercise numbers, not measured data. None of these repeats the reversal trace, the sublist reversal, the merge, the even-length middle, the loop length, the rotation, the odd-then-even split, the weave, the move-to-front, the adjacent swap, or the sentinel that removes one target value. Blocks that walk a singly linked list repeat `ListNode`, `from_list`, and `to_list` so each one runs alone.

## Delete the node you are holding

You are holding one node of the exercise list `8 -> 3 -> 6 -> 1`. You do not have the head, and you do not have the predecessor. Delete the node that holds `3`. What does the list become? What happens if the node you are holding is the tail `1`, or the only node of a one-node list?

**Answer:** Copy the successor's value into the node you hold, then skip the successor. `8 -> 3 -> 6 -> 1` becomes `8 -> 6 -> 1`. The same move on the node that holds `6` produces `8 -> 3 -> 1`. The tail has no successor to copy, so the function returns false and the list stays `8 -> 3 -> 6 -> 1`. A one-node list fails the same way. The node object you were holding is still in the chain. Its value changed, and the successor node is the one that dropped out. That is legal only when a successor exists. LeetCode 237 promises the values are unique, the list has at least two nodes, and the given node is not the tail. This drill includes the tail and the one-node list, which that problem excludes. Time is O(1). Extra memory is O(1). A real delete of the tail needs the predecessor, which this statement does not give you. The [Node deletion: pointer surgery around the target](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) card is that predecessor walk.

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


def node_at(head: ListNode | None, index: int) -> ListNode:
    current = head
    for _ in range(index):
        current = current.next
    return current


def delete_held(node: ListNode) -> bool:
    if node.next is None:
        return False
    node.val = node.next.val
    node.next = node.next.next
    return True


held = from_list([8, 3, 6, 1])
print(delete_held(node_at(held, 1)), to_list(held))
middle = from_list([8, 3, 6, 1])
print(delete_held(node_at(middle, 2)), to_list(middle))
tail = from_list([8, 3, 6, 1])
print(delete_held(node_at(tail, 3)), to_list(tail))
only = from_list([8])
print(delete_held(only), to_list(only))
# True [8, 6, 1]
# True [8, 3, 1]
# False [8, 3, 6, 1]
# False [8]
```

## Drop every value that repeats

The exercise list `4 -> 4 -> 5 -> 7 -> 7 -> 7 -> 9` is sorted. Remove every value that appears more than once, so a value that appears once stays and a value that repeats is gone entirely. What remains? What do `4 -> 4`, a single `5`, an empty list, and `4 -> 4 -> 5 -> 5` become?

**Answer:** `5 -> 9`. Both `4`s go, and all three `7`s go. `4 -> 4` becomes empty. A single `5` stays. An empty list stays empty. `4 -> 5 -> 5` leaves `4`. `4 -> 4 -> 4` becomes empty. `1 -> 2 -> 3` is unchanged, because nothing repeated. `4 -> 4 -> 5 -> 5` becomes empty. A dummy head matters because the first value may be one of the repeats, as it is for `4 -> 4`. Walk with a predecessor. When the next two nodes share a value, skip the whole run of that value. Otherwise step the predecessor forward. The list has to be sorted, so equal values are adjacent. An unsorted list is a different problem and needs a count. The [Sentinel: remove every match](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) drill deletes every node equal to one chosen target and keeps the other duplicates. This drill deletes a value only because it occurs more than once. Time is O(n). Extra memory is O(1). LeetCode 82 is this rule on a sorted list of length 0 to 300, with values from -100 to 100. Its samples are different numbers. This drill uses the same rule, including the empty list that problem allows.

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


def drop_repeats(head: ListNode | None) -> ListNode | None:
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next is not None:
        curr = prev.next
        if curr.next is not None and curr.val == curr.next.val:
            value = curr.val
            while curr is not None and curr.val == value:
                curr = curr.next
            prev.next = curr
        else:
            prev = prev.next
    return dummy.next


samples = (
    [4, 4, 5, 7, 7, 7, 9],
    [4, 4],
    [5],
    [],
    [4, 5, 5],
    [4, 4, 4],
    [1, 2, 3],
    [4, 4, 5, 5],
)
for values in samples:
    print(to_list(drop_repeats(from_list(values))))
# [5, 9]
# []
# [5]
# []
# [4]
# []
# [1, 2, 3]
# []
```

## Add two reversed digit lists

Two exercise numbers are stored with the ones digit at the head: `9 -> 9 -> 2` is 299, and `1 -> 8` is 81. Add them and return the sum in the same reversed form. What do `9 -> 9` plus `1`, `0` plus `0`, two empty lists, and an empty list plus `4 -> 1` return?

**Answer:** `0 -> 8 -> 3`, because 299 + 81 = 380. `9 -> 9` plus `1` is 100, stored as `0 -> 0 -> 1`. The new hundreds digit is a node the inputs did not have. `0` plus `0` is a single `0`. This drill treats an empty list as 0, so two empty lists return `0`, and an empty list plus `4 -> 1` returns `4 -> 1`. `9` plus `9` is `8 -> 1`. Walk both lists while either list remains or a carry remains. The digit is `total % 10` and the carry is `total // 10`, which `divmod` returns as a pair. A dummy collects the digits so the first digit, which might be 0, needs no special case. Time is O(n + m). Extra memory is the output list, one node per digit of the sum. LeetCode 2 requires non-empty lists, a single digit 0 through 9 in each node, and no leading zero except the number 0 itself. Its length is 1 to 100. This drill also accepts an empty list as 0. A node holding 12 would still run through `divmod` and would break the one-digit contract, so the inputs here stay in 0 through 9.

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


def add_reversed(left: ListNode | None, right: ListNode | None) -> ListNode:
    dummy = tail = ListNode(0)
    carry = 0
    while left is not None or right is not None or carry:
        total = carry
        if left is not None:
            total += left.val
            left = left.next
        if right is not None:
            total += right.val
            right = right.next
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
    if dummy.next is None:
        return ListNode(0)
    return dummy.next


pairs = (
    ([9, 9, 2], [1, 8]),
    ([9, 9], [1]),
    ([0], [0]),
    ([], []),
    ([], [4, 1]),
    ([9], [9]),
)
for left, right in pairs:
    print(to_list(add_reversed(from_list(left), from_list(right))))
# [0, 8, 3]
# [0, 0, 1]
# [0]
# [0]
# [4, 1]
# [8, 1]
```

## Partition around a pivot and keep order

Partition the exercise list `5 -> 1 -> 8 -> 3 -> 8 -> 2` around 5. Nodes less than 5 come first. Nodes greater than or equal to 5 follow them. Keep the original relative order inside each side. What does the list become? What do an empty list, `5 -> 5`, and `-1 -> 5 -> -3` around 0 become?

**Answer:** `1 -> 3 -> 2 -> 5 -> 8 -> 8`. The less-than side kept `1, 3, 2`. The other side kept `5, 8, 8`. `5 -> 5` stays `5 -> 5`, because equality belongs on the second side. `1 -> 2` around 5 stays `1 -> 2`. `8 -> 9` around 5 stays `8 -> 9`. An empty list stays empty. `-1 -> 5 -> -3` around 0 becomes `-1 -> -3 -> 5`. Two dummy heads collect the two sides, so neither side needs a special case for its first node. Each input node is detached before it is appended, and the less-than tail is then pointed at the first greater-or-equal node. Stable order is the point of walking once from the head. Swapping toward the ends would put the small values first and scramble their order. Time is O(n). Extra memory is O(1) besides the two dummy nodes. LeetCode 86 is this rule, with length 0 to 200, values from -100 to 100, and a pivot from -200 to 200. Its sample list is different. This drill uses the same `<` versus `>=` split, including the empty list.

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


def partition(head: ListNode | None, pivot: int) -> ListNode | None:
    less_head = less_tail = ListNode(0)
    more_head = more_tail = ListNode(0)
    while head is not None:
        nxt = head.next
        head.next = None
        if head.val < pivot:
            less_tail.next = head
            less_tail = head
        else:
            more_tail.next = head
            more_tail = head
        head = nxt
    less_tail.next = more_head.next
    return less_head.next


cases = (
    ([5, 1, 8, 3, 8, 2], 5),
    ([5, 5], 5),
    ([1, 2], 5),
    ([8, 9], 5),
    ([], 5),
    ([-1, 5, -3], 0),
)
for values, pivot in cases:
    print(to_list(partition(from_list(values), pivot)))
# [1, 3, 2, 5, 8, 8]
# [5, 5]
# [1, 2]
# [8, 9]
# []
# [-1, -3, 5]
```

## Recency after each get and put

A cache holds two keys. Start empty. Run `put(10, 10)`, `put(20, 20)`, `get(10)`, `put(30, 30)`, `get(20)`, `put(10, 11)`, `put(40, 40)`. After each call, what is the key order from oldest to newest, and what did each get return?

**Answer:** The orders are `[10]`, `[10, 20]`, `[20, 10]`, `[10, 30]`, `[10, 30]`, `[30, 10]`, `[10, 40]`. `get(10)` returns 10 and makes 10 newest, so 20 becomes the oldest. `put(30, 30)` evicts 20. `get(20)` returns `None` and does not change the order. `put(10, 11)` overwrites 10 and moves it to the newest end, so 30 stays and nothing is evicted. `put(40, 40)` then evicts 30. A get on an empty cache returns `None`. The [LRU Trace](../../09_System_Design_Interview/05_Caching/) drill uses the letters A, B, C, A, D at capacity 3 and compares FIFO with a TTL. This drill is capacity 2, integer keys, and it includes an overwrite. The [Least-Recently-Used Cache (LeetCode-style: LRU Cache)](../11_Linked_Lists/) card is the class. Time per call is expected O(1). Extra memory is O(capacity). The collision worst case is linear in the number of stored keys. LeetCode 146 returns `-1` on a miss and constrains values to be at least 0. This drill returns `None`.

```python
class DNode:
    def __init__(self, key: int = 0, val: int = 0) -> None:
        self.key = key
        self.val = val
        self.prev: "DNode | None" = None
        self.next: "DNode | None" = None


class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.nodes: dict[int, DNode] = {}
        self.oldest = DNode()
        self.newest = DNode()
        self.oldest.next = self.newest
        self.newest.prev = self.oldest

    def _unlink(self, node: DNode) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _append_newest(self, node: DNode) -> None:
        last = self.newest.prev
        last.next = node
        node.prev = last
        node.next = self.newest
        self.newest.prev = node

    def order(self) -> list[int]:
        keys: list[int] = []
        current = self.oldest.next
        while current is not self.newest:
            keys.append(current.key)
            current = current.next
        return keys

    def get(self, key: int) -> int | None:
        node = self.nodes.get(key)
        if node is None:
            return None
        self._unlink(node)
        self._append_newest(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        node = self.nodes.get(key)
        if node is not None:
            node.val = value
            self._unlink(node)
            self._append_newest(node)
            return
        node = DNode(key, value)
        self.nodes[key] = node
        self._append_newest(node)
        if len(self.nodes) > self.capacity:
            stale = self.oldest.next
            self._unlink(stale)
            del self.nodes[stale.key]


cache = LRUCache(2)
cache.put(10, 10)
print(cache.order())
cache.put(20, 20)
print(cache.order())
print(cache.get(10), cache.order())
cache.put(30, 30)
print(cache.order())
print(cache.get(20), cache.order())
cache.put(10, 11)
print(cache.order())
cache.put(40, 40)
print(cache.order())
print(LRUCache(2).get(10))
# [10]
# [10, 20]
# 10 [20, 10]
# [10, 30]
# None [10, 30]
# [30, 10]
# [10, 40]
# None
```

## The evicted key is still in the map

This put unlinks the oldest node when the cache is over capacity and leaves that key in the map. Capacity is 2. The calls are `put(5, 50)`, `put(6, 60)`, `put(1, 10)`. What are the list order and the map keys before any get? What does an immediate `get(5)` return, and what is the order afterward? What happens if `get(6)` runs first, and only then `get(5)`? What does the repaired put do?

**Answer:** Before the get, the list order is `[6, 1]` and the map keys are `1, 5, 6`. The node for 5 was unlinked and then left in the map. An immediate `get(5)` returns 50. The detached node's `prev` and `next` still name the two nodes the unlink joined, so unlinking again changes nothing on that edge and the append puts 5 at the newest end. The order becomes `[6, 1, 5]`, which is three keys in a cache of capacity 2. `get(6)` first moves 6 to the newest end, and the order is `[1, 6]`. Those stale links no longer describe a live edge. The following `get(5)` returns 50, the order becomes `[6, 5]`, and key 1 is gone from the list while it remains in the map. The repaired put deletes the key in the same step as the unlink. Its order stays `[6, 1]`, `get(5)` returns `None`, and the map keys are `1, 6`. The [Least-Recently-Used Cache (LeetCode-style: LRU Cache)](../11_Linked_Lists/) card deletes the key. Time is expected O(1) either way. The broken cache is the one that is wrong, not the one that is slower. Extra memory is O(capacity) when the delete runs, and it grows past capacity when the delete is skipped.

```python
class DNode:
    def __init__(self, key: int = 0, val: int = 0) -> None:
        self.key = key
        self.val = val
        self.prev: "DNode | None" = None
        self.next: "DNode | None" = None


class LRUCache:
    def __init__(self, capacity: int, forget_key: bool) -> None:
        self.capacity = capacity
        self.forget_key = forget_key
        self.nodes: dict[int, DNode] = {}
        self.oldest = DNode()
        self.newest = DNode()
        self.oldest.next = self.newest
        self.newest.prev = self.oldest

    def _unlink(self, node: DNode) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _append_newest(self, node: DNode) -> None:
        last = self.newest.prev
        last.next = node
        node.prev = last
        node.next = self.newest
        self.newest.prev = node

    def order(self) -> list[int]:
        keys: list[int] = []
        current = self.oldest.next
        while current is not self.newest:
            keys.append(current.key)
            current = current.next
        return keys

    def get(self, key: int) -> int | None:
        node = self.nodes.get(key)
        if node is None:
            return None
        self._unlink(node)
        self._append_newest(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        node = self.nodes.get(key)
        if node is not None:
            node.val = value
            self._unlink(node)
            self._append_newest(node)
            return
        node = DNode(key, value)
        self.nodes[key] = node
        self._append_newest(node)
        if len(self.nodes) > self.capacity:
            stale = self.oldest.next
            self._unlink(stale)
            if not self.forget_key:
                del self.nodes[stale.key]


def fill(forget_key: bool) -> LRUCache:
    cache = LRUCache(2, forget_key)
    cache.put(5, 50)
    cache.put(6, 60)
    cache.put(1, 10)
    return cache


broken = fill(True)
print(broken.order(), sorted(broken.nodes))
print(broken.get(5), broken.order())
moved = fill(True)
print(moved.get(6), moved.order())
print(moved.get(5), moved.order(), sorted(moved.nodes))
repaired = fill(False)
print(repaired.order(), repaired.get(5), sorted(repaired.nodes))
# [6, 1] [1, 5, 6]
# 50 [6, 1, 5]
# 60 [1, 6]
# 50 [6, 5] [1, 5, 6]
# [6, 1] None [1, 6]
```

## Equal values are not a shared node

List A is `3 -> 8 -> 5` and list B is `3 -> 8 -> 5`, built from different nodes. A second pair shares a tail: A is `3 -> 8 -> 5`, B is `8 -> 5`, and the final `5` is one node object. A search that remembers values, and a search that remembers node identity, each return a tag. Which tags come back? What do two empty lists return?

**Answer:** On the separate lists the value search returns `("a3", "b3")`, the first value that appears on both, and the identity search returns `None`. On the joined lists the value search returns `("a8", "b8")`. Those two `8`s are different nodes. The shared node is the final `5`, tag `shared`, which is what the identity search returns. Two empty lists, and a real list paired with an empty list, return `None` for both searches. The value map answers "some value occurs in both," which the statement did not ask. It is expected O(n + m) time and O(n) extra memory, and O(n * m) time when every key collides. The identity walk in this drill is the two-pointer switch, not a set: worst-case O(n + m) time, O(1) extra memory, and no hash. [The Node Two Lists Share (LeetCode-style: Intersection of Two Linked Lists)](../11_Linked_Lists/) is that walk. LeetCode 160 allows values to repeat inside 1 to 100,000, so equal values on different nodes are inside that problem too.

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None, tag: str = "") -> None:
        self.val = val
        self.next = nxt
        self.tag = tag


def by_value(left: ListNode | None, right: ListNode | None) -> tuple[str, str] | None:
    seen: dict[int, str] = {}
    while right is not None:
        seen.setdefault(right.val, right.tag)
        right = right.next
    while left is not None:
        if left.val in seen:
            return (left.tag, seen[left.val])
        left = left.next
    return None


def by_identity(left: ListNode | None, right: ListNode | None) -> str | None:
    first, second = left, right
    while first is not second:
        first = first.next if first is not None else right
        second = second.next if second is not None else left
    return None if first is None else first.tag


separate_a = ListNode(3, ListNode(8, ListNode(5, tag="a5"), tag="a8"), tag="a3")
separate_b = ListNode(3, ListNode(8, ListNode(5, tag="b5"), tag="b8"), tag="b3")
shared = ListNode(5, tag="shared")
joined_a = ListNode(3, ListNode(8, shared, tag="a8"), tag="a3")
joined_b = ListNode(8, shared, tag="b8")
print(by_value(separate_a, separate_b), by_identity(separate_a, separate_b))
print(by_value(joined_a, joined_b), by_identity(joined_a, joined_b))
print(by_value(None, None), by_identity(None, None), by_value(joined_a, None), by_identity(joined_a, None))
# ('a3', 'b3') None
# ('a8', 'b8') shared
# None None None None
```

## Reverse in groups of three

Reverse the exercise list `6 -> 1 -> 4 -> 9 -> 2 -> 8 -> 3` in groups of 3. A tail shorter than 3 stays in its original order. What does the list become? What do a group size of 1, a group size equal to the length, a group size longer than the list, an empty list, and a one-node list return?

**Answer:** `4 -> 1 -> 6 -> 8 -> 2 -> 9 -> 3`. The first group `6, 1, 4` reverses, the second group `9, 2, 8` reverses, and the final `3` is shorter than 3 so it stays. Group size 1 leaves the list unchanged. Group size 7, the whole length, reverses it to `3, 8, 2, 9, 4, 1, 6`. Group size 8 is longer than the list, so the only group is short and the list stays as it is. An empty list and a one-node list stay as they are. Group size 0 is not a group. This drill leaves the list unchanged. `6 -> 1 -> 4 -> 9` with group size 3 becomes `4 -> 1 -> 6 -> 9`, a full group plus a one-node tail. Count k nodes past the previous group. If the count falls off the list, return what you have. Otherwise reverse that group in place and repeat. Values are not rewritten. Only `next` changes. The [Swap adjacent pairs](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) drill is group size 2. The [Reverse only positions left..right](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) drill is one range, not every group. Time is O(n). Extra memory is O(1). LeetCode 25 requires `1 <= k <= n <= 5000`, values from 0 to 1000, forbids changing values, and asks in the follow-up for O(1) extra memory. This drill also defines k larger than the length, k < 1, and the empty list.

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


def reverse_groups(head: ListNode | None, k: int) -> ListNode | None:
    if k < 1:
        return head
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        kth: ListNode | None = group_prev
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next
        group_next = kth.next
        prev, curr = group_next, group_prev.next
        while curr is not group_next:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt
        new_tail = group_prev.next
        group_prev.next = prev
        group_prev = new_tail


values = [6, 1, 4, 9, 2, 8, 3]
print(to_list(reverse_groups(from_list(values), 3)))
print(to_list(reverse_groups(from_list(values), 1)))
print(to_list(reverse_groups(from_list(values), 7)))
print(to_list(reverse_groups(from_list(values), 8)))
print(to_list(reverse_groups(from_list([]), 3)), to_list(reverse_groups(from_list([6]), 3)))
print(to_list(reverse_groups(from_list(values), 0)), to_list(reverse_groups(from_list([6, 1, 4, 9]), 3)))
# [4, 1, 6, 8, 2, 9, 3]
# [6, 1, 4, 9, 2, 8, 3]
# [3, 8, 2, 9, 4, 1, 6]
# [6, 1, 4, 9, 2, 8, 3]
# [] [6]
# [6, 1, 4, 9, 2, 8, 3] [4, 1, 6, 9]
```

## The gap that stops one node late

This removal advances a leader k steps, then keeps moving while the leader itself is not `None`. The repaired loop moves while the leader's `next` is not `None`. On the exercise list `8 -> 3 -> 5 -> 1 -> 9`, what does each version return for k = 2, k = 5, and k = 1? What does k = 6 do?

**Answer:** For k = 2 the late stop removes the tail and leaves `8, 3, 5, 1`. The repaired loop removes `1` and leaves `8, 3, 5, 9`. For k = 5, the length, the late stop removes `3` and leaves `8, 5, 1, 9`. The repaired loop removes the head and leaves `3, 5, 1, 9`. For k = 1 the late stop walks the trailer onto the tail and then reads `next` of `None`, which raises `AttributeError`. The repaired loop removes the tail and leaves `8, 3, 5, 1`. k = 6 is longer than the list, so both versions return the list before the joint walk starts. An empty list with k = 1 stays empty. The leader has to stop on the last node, which is the test `lead.next`. Stopping on `None` is one node further. The [Remove the Kth Last Node (LeetCode-style: Remove Nth Node From End of List)](../11_Linked_Lists/) card uses the repaired test. LeetCode 19 promises `1 <= n <= length` and a length of at least 1, so k = 6 is outside that problem. Both versions are O(n) time and O(1) extra memory. The late stop is linear and wrong.

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


def remove_kth(head: ListNode | None, k: int, stop_on_none: bool) -> ListNode | None:
    if k < 1:
        return head
    dummy = ListNode(0, head)
    lead = dummy
    for _ in range(k):
        if lead.next is None:
            return head
        lead = lead.next
    trail = dummy
    while (lead is not None) if stop_on_none else (lead.next is not None):
        lead = lead.next
        trail = trail.next
    trail.next = trail.next.next
    return dummy.next


def attempt(values: list[int], k: int, stop_on_none: bool) -> list[int] | str:
    try:
        return to_list(remove_kth(from_list(values), k, stop_on_none))
    except AttributeError:
        return "AttributeError"


base = [8, 3, 5, 1, 9]
for k in (2, 5, 1, 6):
    print(attempt(base, k, True), attempt(base, k, False))
print(attempt([], 1, True), attempt([], 1, False))
# [8, 3, 5, 1] [8, 3, 5, 9]
# [8, 5, 1, 9] [3, 5, 1, 9]
# AttributeError [8, 3, 5, 1]
# [8, 3, 5, 1, 9] [8, 3, 5, 1, 9]
# [] []
```
