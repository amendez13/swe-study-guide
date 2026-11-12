# Fast and Slow Pointers — Drills

Original drills for two speeds on a chain: where the pointers meet, where the cycle starts, a repeated value reached by indexes, a guard that reads `next` of `None`, the middle node unlinked from the node in front of it, a digit-square sequence, a fast step of 3, and the choice between two speeds and a set. The lists and the integers are exercise numbers. None of these repeats the even-length middle question or the loop-length count. Blocks that walk a list repeat `ListNode` and `chain` so each one runs alone.

## The step where they meet

The exercise list is `12 → 4 → 7 → 3 → 9 → 5 → 8`, and `8` links back to `3`. The slow pointer moves one step and the fast pointer moves two. On which step do they land on the same node, and which value does that node hold? How long is the stem in front of the cycle?

**Answer:** They meet on step 4, on the node that holds `9`. The stem is `12 → 4 → 7`, three nodes, and the cycle is `3 → 9 → 5 → 8`, four nodes. The rows are (step, slow value, fast value): (1, 4, 7), (2, 7, 9), (3, 3, 8), (4, 9, 9). The meeting value `9` is on the cycle. It is not the entrance. The entrance is `3`, which is a different question. On the straight list of the same seven values, three double-steps leave the fast pointer on the last node, `8`, and the slow pointer on `3`. The next guard sees that `8` has no successor and stops. That row is (4, 3, None). Time is O(n). Extra memory is O(1). Compare the nodes with `is`.

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None) -> None:
        self.val = val
        self.next = nxt


def chain(values: list[int], back: int | None) -> ListNode | None:
    if not values:
        return None
    nodes = [ListNode(value) for value in values]
    for earlier, later in zip(nodes, nodes[1:]):
        earlier.next = later
    if back is not None:
        nodes[-1].next = nodes[back]
    return nodes[0]


def trace(head: ListNode | None) -> list[tuple[int, int | None, int | None]]:
    slow = fast = head
    rows: list[tuple[int, int | None, int | None]] = []
    for step in range(1, 8):
        if fast is None or fast.next is None:
            rows.append((step, None if slow is None else slow.val, None))
            return rows
        slow = slow.next
        fast = fast.next.next
        rows.append((step, None if slow is None else slow.val, None if fast is None else fast.val))
        if slow is fast:
            return rows
    return rows


values = [12, 4, 7, 3, 9, 5, 8]
print(trace(chain(values, 3)))
print(trace(chain(values, None)))
# [(1, 4, 7), (2, 7, 9), (3, 3, 8), (4, 9, 9)]
# [(1, 4, 7), (2, 7, 9), (3, 3, 8), (4, 3, None)]
```

## Walk back to the entrance

The exercise list is `2 → 6 → 1 → 8 → 4 → 7 → 9 → 5`, and `5` links back to `7`. The one-step and two-step pointers have already met. Put one pointer back on the head, leave the other on the meeting node, and move both one step. Which node do they reach, and how many steps does that take? What is the forward distance from the meeting node to the entrance, along the cycle? Then answer the same entrance question for `2 → 6 → 8` linked back to `2`, and for `3 → 8` with `8` linked to itself.

**Answer:** The entrance is `7`, and the reset takes 5 steps. The stem is the five nodes `2, 6, 1, 8, 4`. The cycle is `7 → 9 → 5`, three nodes. The pointers meet at `9`. The forward walk from `9` to `7` is `9 → 5 → 7`, two steps. Five mod three is 2, so the distance along the cycle is 2 and the reset still walks all five stem steps. The cycle pointer stands on `7` while the head pointer is still on `1`. Those are different nodes. The head pointer is not on the cycle yet, so the walk does not stop there. On `2 → 6 → 8` linked back to `2` the head is the entrance, the pointers meet on `2`, and the reset takes 0 steps. On `3 → 8` with `8` linked to itself the entrance is `8`, the cycle length is 1, and the stem is the single node `3`, so the reset takes 1 step. The pointer on the self-loop stays on `8`. A set of node identities returns the same three entrances, `7`, `2`, and `8`. Time is O(n). Extra memory for the reset is O(1).

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None) -> None:
        self.val = val
        self.next = nxt


def chain(values: list[int], back: int | None) -> ListNode | None:
    if not values:
        return None
    nodes = [ListNode(value) for value in values]
    for earlier, later in zip(nodes, nodes[1:]):
        earlier.next = later
    if back is not None:
        nodes[-1].next = nodes[back]
    return nodes[0]


def entrance(head: ListNode | None) -> tuple[int | None, int | None]:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            steps = 0
            walker = head
            while walker is not slow:
                walker = walker.next
                slow = slow.next
                steps += 1
            return (walker.val, steps)
    return (None, None)


def by_identities(head: ListNode | None) -> int | None:
    seen: set[int] = set()
    while head is not None:
        if id(head) in seen:
            return head.val
        seen.add(id(head))
        head = head.next
    return None


def forward(values: list[int], back: int, start_value: int) -> int:
    nodes = [ListNode(value) for value in values]
    for earlier, later in zip(nodes, nodes[1:]):
        earlier.next = later
    nodes[-1].next = nodes[back]
    cursor = next(node for node in nodes if node.val == start_value)
    goal = nodes[back]
    distance = 0
    while cursor is not goal:
        cursor = cursor.next
        distance += 1
    return distance


def show(values: list[int], back: int) -> tuple[int | None, int | None, int | None]:
    head = chain(values, back)
    start, steps = entrance(head)
    return (start, steps, by_identities(head))


print(show([2, 6, 1, 8, 4, 7, 9, 5], 5), forward([2, 6, 1, 8, 4, 7, 9, 5], 5, 9))
print(show([2, 6, 8], 0))
print(show([3, 8], 1))
# (7, 5, 7) 2
# (2, 0, 2)
# (8, 1, 8)
```

## The value that index zero leads into

Each exercise array has length n + 1. Every value is in 1 through n, and exactly one value appears more than once. Return that value. Do not modify the array. Use a constant amount of extra memory. Check the result against a count of the values.

**Answer:** Follow `nums[i]` as the successor of index i. Index 0 is a stem, because every stored value is at least 1. The entrance of the cycle is the repeated value. `[4, 1, 6, 2, 5, 3, 6]` returns 6. `[8, 3, 5, 1, 7, 2, 6, 4, 8]` returns 8, a repeat at both ends. `[1, 1]` returns 1. `[4, 4, 4, 4, 4]` returns 4, a value that appears five times, with 1, 2, and 3 missing. `[6, 5, 4, 3, 2, 1, 5]` returns 5. `[1, 2, 3, 4, 5, 6, 6]` returns 6. The count of values agrees on every row, and the arrays are unchanged. LeetCode 287 is this contract, with n up to 100,000, and it requires constant extra memory. These arrays are smaller and are not that problem's samples. Time for the cycle walk is O(n). Extra memory is O(1). The count used here as a check is O(n) extra memory. The value-range halving on the concept card is the constant-memory check with an extra log factor.

```python
def find_duplicate(nums: list[int]) -> int:
    slow = fast = 0
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = 0
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow


def by_count(nums: list[int]) -> list[int]:
    counts: dict[int, int] = {}
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
    return [value for value, count in counts.items() if count > 1]


def show(nums: list[int]) -> tuple[int, list[int], list[int]]:
    found = find_duplicate(nums)
    return (found, by_count(nums), list(nums))


print(show([4, 1, 6, 2, 5, 3, 6]))
print(show([8, 3, 5, 1, 7, 2, 6, 4, 8]))
print(show([1, 1]))
print(show([4, 4, 4, 4, 4]))
print(show([6, 5, 4, 3, 2, 1, 5]))
print(show([1, 2, 3, 4, 5, 6, 6]))
# (6, [6], [4, 1, 6, 2, 5, 3, 6])
# (8, [8], [8, 3, 5, 1, 7, 2, 6, 4, 8])
# (1, [1], [1, 1])
# (4, [4], [4, 4, 4, 4, 4])
# (5, [5], [6, 5, 4, 3, 2, 1, 5])
# (6, [6], [1, 2, 3, 4, 5, 6, 6])
```

## The condition that reads past the end

This loop is supposed to report whether a list cycles. It crashes on some lists that do not. Which inputs crash, and which inputs hide the bug?

```text
while fast.next and fast:
    slow = slow.next
    fast = fast.next.next
```

**Answer:** The test reads `fast.next` before it asks whether `fast` exists. When `fast` is `None`, that is an `AttributeError`. An empty list crashes immediately. A straight list of even length sends the fast pointer off the end: length 2 and length 4 crash. A straight list of odd length parks the fast pointer on the last node, `next` is `None`, and the test returns "no cycle" without crashing. That return happens to be the right boolean, and it never executed the guard that is wrong. A self-loop and a longer cycle also return "cycle," because the fast pointer never becomes `None`. The repaired test names `fast` first: `while fast is not None and fast.next is not None`. On these inputs it returns no cycle for the empty list and every straight list, and cycle for the self-loop and the list whose tail links back to the head. Time for the repaired walk is O(n). Extra memory is O(1).

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None) -> None:
        self.val = val
        self.next = nxt


def chain(values: list[int], back: int | None) -> ListNode | None:
    if not values:
        return None
    nodes = [ListNode(value) for value in values]
    for earlier, later in zip(nodes, nodes[1:]):
        earlier.next = later
    if back is not None:
        nodes[-1].next = nodes[back]
    return nodes[0]


def scan(head: ListNode | None, safe: bool) -> str:
    slow = fast = head
    try:
        while (fast is not None and fast.next is not None) if safe else (fast.next and fast):
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return "cycle"
        return "no cycle"
    except AttributeError:
        return "AttributeError"


def show(values: list[int], back: int | None) -> tuple[str, str]:
    return (scan(chain(values, back), False), scan(chain(values, back), True))


print(show([], None))
print(show([8], None))
print(show([8, 3], None))
print(show([8, 3, 5], None))
print(show([8, 3, 5, 1], None))
print(show([8], 0))
print(show([5, 7, 1, 3], 0))
# ('AttributeError', 'no cycle')
# ('no cycle', 'no cycle')
# ('AttributeError', 'no cycle')
# ('no cycle', 'no cycle')
# ('AttributeError', 'no cycle')
# ('cycle', 'cycle')
# ('cycle', 'cycle')
```

## Unlink the middle from the node in front of it

Delete the middle node and return the remaining values. On an even length the middle is the second middle, index n // 2, the same node version A returns. The pointer that unlinks has to stand on the predecessor. What does each exercise list become, including an empty list, a single node, and `4 → 9`?

**Answer:** Keep a predecessor. A dummy node stands in front of the head so the single-node list has a predecessor too. Start the slow pointer on the head and the fast pointer on the head, and move the predecessor with the slow pointer. When the fast pointer cannot take two steps, the slow pointer is the middle and the predecessor's `next` skips it. `[]` stays empty. `[4]` becomes empty. `[4, 9]` becomes `[4]`, because the second middle is `9`. `[8, 3, 5, 1]` becomes `[8, 3, 1]`, deleting `5`. `[8, 3, 5, 1, 9]` becomes `[8, 3, 1, 9]`, deleting the single middle `5`. `[7, 8, 9, 1, 2, 6]` becomes `[7, 8, 9, 2, 6]`, deleting `1`. A slice that drops index n // 2 agrees on every row. LeetCode 2095 deletes that same index. Its length starts at 1 and its values are from 1 to 100,000. The empty list is outside that contract, and this drill defines it. Time is O(n). Extra memory is O(1).

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None) -> None:
        self.val = val
        self.next = nxt


def chain(values: list[int]) -> ListNode | None:
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


def delete_middle(head: ListNode | None) -> list[int]:
    if head is None:
        return []
    dummy = ListNode(0, head)
    prev = dummy
    slow: ListNode | None = head
    fast: ListNode | None = head
    while fast is not None and fast.next is not None:
        prev = slow
        slow = slow.next
        fast = fast.next.next
    prev.next = slow.next
    return to_list(dummy.next)


def by_index(values: list[int]) -> list[int]:
    if not values:
        return []
    index = len(values) // 2
    return values[:index] + values[index + 1 :]


def show(values: list[int]) -> tuple[list[int], list[int]]:
    return (delete_middle(chain(values)), by_index(values))


print(show([]))
print(show([4]))
print(show([4, 9]))
print(show([8, 3, 5, 1]))
print(show([8, 3, 5, 1, 9]))
print(show([7, 8, 9, 1, 2, 6]))
# ([], [])
# ([], [])
# ([4], [4])
# ([8, 3, 1], [8, 3, 1])
# ([8, 3, 1, 9], [8, 3, 1, 9])
# ([7, 8, 9, 2, 6], [7, 8, 9, 2, 6])
```

## 23 reaches one and 15 does not

Replace a non-negative integer by the sum of the squares of its digits, and repeat. A value that reaches 1 is happy. Report the chain and the value where the one-step and two-step walks meet, for 23, for 15, for 1, and for 7.

**Answer:** 23 goes 23 → 13 → 10 → 1 and the two speeds meet at 1, so 23 is happy. 15 goes 15 → 26 → 40 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4, and the next step returns to 16. The two speeds meet at 42. 42 is on the cycle and it is not 1, so 15 is not happy. A set of seen values notices the repeat at 16, which is the entrance of that cycle, a different node from the meeting value. 1 goes to 1 and the speeds meet at 1, so 1 is happy. 7 goes 7 → 49 → 97 → 130 → 10 → 1 and the speeds meet at 1, so 7 is happy. The unhappy cycle that 15 reaches is 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 and back to 4. LeetCode 202 starts at 1 and includes none of these exercise values as its sample. Reading the digits is O(log n). After the value falls into the finite range, the rest is a bounded number of steps. Extra memory for the two speeds is O(1).

```python
def digit_square_sum(number: int) -> int:
    total = 0
    while number:
        number, digit = divmod(number, 10)
        total += digit * digit
    return total


def chain_and_meeting(number: int) -> tuple[list[int], int, bool]:
    seen: list[int] = []
    current = number
    while current not in seen:
        seen.append(current)
        current = digit_square_sum(current)
    slow = fast = number
    while True:
        slow = digit_square_sum(slow)
        fast = digit_square_sum(digit_square_sum(fast))
        if slow == fast:
            return (seen, slow, slow == 1)


print(chain_and_meeting(23))
print(chain_and_meeting(15))
print(chain_and_meeting(1))
print(chain_and_meeting(7))
print(chain_and_meeting(4))
# ([23, 13, 10, 1], 1, True)
# ([15, 26, 40, 16, 37, 58, 89, 145, 42, 20, 4], 42, False)
# ([1], 1, True)
# ([7, 49, 97, 130, 10, 1], 1, True)
# ([4, 16, 37, 58, 89, 145, 42, 20], 4, False)
```

## Three steps for the fast pointer

On the exercise list `4 → 8 → 9 → 1 → 6`, with `6` linked back to `8`, move the slow pointer one step and the fast pointer three steps. Do they meet? If you then put one pointer on the head and walk both one step at a time, do you reach the entrance? What does the one-step and two-step schedule return on the same list? Then answer both schedules for `5 → 7` linked back to `5`, and for `4 → 8 → 9 → 1` with `1` linked back to `8`.

**Answer:** A fast step of 3 still detects a cycle when both pointers start on the head. Each printed row is the step-3 meeting value, the slow step count, and the reset value, then the same three fields for steps 1 and 2. On `4 → 8 → 9 → 1 → 6` linked back to `8`, the stem has 1 node and the cycle has 4. The pointers meet on `9` after 2 slow steps. The entrance is `8`. 2 is not a multiple of 4, so walking both pointers one step from the head and from `9` repeats a pair of nodes and never lands them on one node. Steps 1 and 2 meet on `6` after 4 slow steps, 4 is a multiple of 4, and the reset stops on `8`. On `5 → 7` linked back to `5` the cycle length is 2 and the stem is empty. Steps 1 and 3 meet on `7` after 1 slow step, and 1 is not a multiple of 2, so the reset misses. Steps 1 and 2 meet on `5` after 2 slow steps and the reset takes 0 steps. On `4 → 8 → 9 → 1` linked back to `8` the cycle length is 3. Twice a step count is a multiple of 3 only when the step count itself is. Both schedules meet on `1` after 3 slow steps, and the reset stops on `8`, the entrance. The reset lands on the entrance exactly when the slow step count at the meeting is a multiple of the cycle length. Steps 1 and 2 always produce that multiple. A fast step of 3 produces it on the 3-cycle and misses it on the 4-cycle and the 2-cycle. Time to detect is still linear in the length. Extra memory is O(1).

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None) -> None:
        self.val = val
        self.next = nxt


def chain(values: list[int], back: int) -> ListNode:
    nodes = [ListNode(value) for value in values]
    for earlier, later in zip(nodes, nodes[1:]):
        earlier.next = later
    nodes[-1].next = nodes[back]
    return nodes[0]


def meet(head: ListNode, fast_step: int) -> tuple[ListNode, int]:
    slow = fast = head
    steps = 0
    while True:
        slow = slow.next
        for _ in range(fast_step):
            fast = fast.next
        steps += 1
        if slow is fast:
            return slow, steps


def reset_from(head: ListNode, meeting: ListNode) -> int | None:
    walker: ListNode | None = head
    other: ListNode | None = meeting
    seen: set[tuple[int, int]] = set()
    while walker is not None and other is not None:
        if walker is other:
            return walker.val
        mark = (id(walker), id(other))
        if mark in seen:
            return None
        seen.add(mark)
        walker = walker.next
        other = other.next
    return None


def show(values: list[int], back: int) -> tuple[int, int, int | None, int, int, int | None]:
    head = chain(values, back)
    met3, steps3 = meet(head, 3)
    met2, steps2 = meet(head, 2)
    return (met3.val, steps3, reset_from(head, met3), met2.val, steps2, reset_from(head, met2))


print(show([4, 8, 9, 1, 6], 1))
print(show([5, 7], 0))
print(show([4, 8, 9, 1], 1))
# (9, 2, None, 6, 4, 8)
# (7, 1, None, 5, 2, 5)
# (1, 3, 8, 1, 3, 8)
```

## Which memory the question allows

For each question, name the structure you would use, and the extra memory it stores on the exercise input.

1. Does `12 → 4 → 7 → 3 → 9 → 5 → 8`, with `8` linked to `3`, contain a cycle? Extra memory must stay a constant number of references.
2. Return every value on that list up to and including the nodes stored before a repeat.
3. Is 7 happy, with extra memory a constant number of integers?
4. Find the repeated value in `[4, 1, 6, 2, 5, 3, 6]`. Linear memory is allowed, and the simpler code is preferred.

**Answer:** Question 1 is two speeds, 2 references. A set of identities would store all 7 nodes to answer a boolean. Question 2 is that set, because two speeds do not keep the path. It stores 7 values, `12, 4, 7, 3, 9, 5, 8`, and the next node is the `3` already stored. Question 3 is two speeds on the digit-square function, 2 integers. The seen set for 7 holds 6 integers, `7, 49, 97, 130, 10, 1`, so it is legal only if the constant bound is relaxed. Question 4 is a set of values. The array's distinct values are 6 integers, and the repeated one is 6. The index cycle is what you switch to when constant memory becomes a requirement. The set's expected time is linear and its collision worst case is quadratic. Two speeds are worst-case linear because they follow links.

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None) -> None:
        self.val = val
        self.next = nxt


def chain(values: list[int], back: int | None) -> ListNode | None:
    nodes = [ListNode(value) for value in values]
    for earlier, later in zip(nodes, nodes[1:]):
        earlier.next = later
    if back is not None:
        nodes[-1].next = nodes[back]
    return nodes[0]


def values_until_repeat(head: ListNode | None) -> list[int]:
    seen: set[int] = set()
    values: list[int] = []
    while head is not None and id(head) not in seen:
        seen.add(id(head))
        values.append(head.val)
        head = head.next
    return values


def digit_square_sum(number: int) -> int:
    total = 0
    while number:
        number, digit = divmod(number, 10)
        total += digit * digit
    return total


def happy_values(number: int) -> list[int]:
    seen: list[int] = []
    while number not in seen:
        seen.append(number)
        number = digit_square_sum(number)
    return seen


looping = chain([12, 4, 7, 3, 9, 5, 8], 3)
stored = values_until_repeat(looping)
happy = happy_values(7)
duplicate = [4, 1, 6, 2, 5, 3, 6]
print(("cycle-bool", "two-speeds", 2, len(stored)))
print(("values-before-repeat", "set", stored))
print(("happy-7", "two-speeds", 2, happy))
print(("duplicate-memory-ok", "set", len(set(duplicate)), 6))
# ('cycle-bool', 'two-speeds', 2, 7)
# ('values-before-repeat', 'set', [12, 4, 7, 3, 9, 5, 8])
# ('happy-7', 'two-speeds', 2, [7, 49, 97, 130, 10, 1])
# ('duplicate-memory-ok', 'set', 6, 6)
```

## The same value on two nodes

The exercise list `9 → 2 → 9 → 2 → 9` has no link from the last node. A check that compares `.val` reports a cycle. A check that compares nodes does not. What does each check return on that list, on a single node that holds `2` and points at itself, and on `3 → 5 → 7` linked back to `3`?

**Answer:** On `9 → 2 → 9 → 2 → 9` the second iteration puts the slow pointer on the middle `9` and the fast pointer on the last `9`. The values match and the nodes do not. Identity returns false. The value check returns true. On the self-loop, both checks return true, because the pointers land on the same node and that node's value matches itself. On `3 → 5 → 7` linked back to `3`, both checks return true, because the pointers meet on a node and that node's value matches itself. A value match is evidence of a cycle only when you already know the values are unique. The safe comparison is `is`. LeetCode 141 allows values to repeat inside −100,000 to 100,000, so a value comparison is the wrong test on that problem too. Time is O(n). Extra memory is O(1).

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None) -> None:
        self.val = val
        self.next = nxt


def chain(values: list[int], back: int | None) -> ListNode | None:
    if not values:
        return None
    nodes = [ListNode(value) for value in values]
    for earlier, later in zip(nodes, nodes[1:]):
        earlier.next = later
    if back is not None:
        nodes[-1].next = nodes[back]
    return nodes[0]


def by_identity(head: ListNode | None) -> bool:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


def by_value(head: ListNode | None) -> bool:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if fast is not None and slow.val == fast.val:
            return True
    return False


def show(values: list[int], back: int | None) -> tuple[bool, bool]:
    head = chain(values, back)
    return (by_identity(head), by_value(head))


print(show([9, 2, 9, 2, 9], None))
print(show([2], 0))
print(show([3, 5, 7], 0))
# (False, True)
# (True, True)
# (True, True)
```
