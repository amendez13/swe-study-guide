# Fast and Slow Pointers

Two pointers on one chain, moving at different speeds, answer the questions a linked list cannot answer with an index: whether it loops, where the loop starts, and which node is the middle. The same walk applies when the next node is a function of the current value. The node, the runner, and the short form of Floyd's cycle check live on the Data Structures linked-list topic. These notes are the meeting, the reset, the middle you meant, and the choice against a set.

## Key Points

- **Fast and slow pointers** — two variables, usually one step and two steps, on a chain with no indexes. Compare nodes with `is` after the move. The guard names the fast pointer before `next`. Pollard's rho factoring method uses this schedule on x → (x² + 1) mod n. Linux symlink lookup stops at `MAXSYMLINKS`, 40, instead of running Floyd.
- **Why the faster pointer meets the slower one** — on a cycle, steps 1 and 2 shrink the forward distance from the fast pointer to the slow pointer by 1 each iteration. A straight chain makes the fast pointer reach `None`. Any faster constant step still detects a cycle when both pointers start together, because the cycle length divides a multiple of the speed gap. The same step can miss when the pointers start apart. The entrance reset is proved for steps 1 and 2.
- **Does This List Loop? (LeetCode-style: Linked List Cycle)** — the one-step and two-step pointers meet if and only if some node repeats. Equal values are a different question. LeetCode 141 allows an empty list. The constant-memory follow-up is this walk. `fast.next and fast` crashes when `fast` is `None`.
- **The Node Where the Cycle Starts (LeetCode-style: Linked List Cycle II)** — after they meet, send one pointer to the head and move both one step. They arrive at the entrance together. The slow pointer's travel at the meeting is a multiple of the cycle length, including when that multiple is several laps because the stem is longer than the cycle. The reset walks the whole stem. A cycle through the head takes 0 reset steps. A fast step of 3 can meet with a step count that is not a multiple of the cycle length, and then this reset misses. LeetCode 142 returns the node.
- **Which middle the loop stops on** — version A, `while fast is not None and fast.next is not None`, returns index n // 2. On an even length that is the second middle. Version B stops on the first middle, where a split cuts. Odd lengths have one middle.
- **The Middle Node (LeetCode-style: Middle of the Linked List)** — version A. LeetCode 876 starts at one node, limits values to 1 through 100, and asks for the second middle. An empty list is outside that contract and returns `None` here.
- **A sequence of next values is a linked list** — index i pointing at `nums[i]`, with values in 1 through n and length n + 1, makes index 0 a stem. The cycle entrance is the repeated value. LeetCode 287 requires constant extra memory and an unmodified array. Counting values at most m is the O(n log n) alternative.
- **Reaching One by Squaring Digits (LeetCode-style: Happy Number)** — replace n by the sum of the squares of its digits. Happy means the two speeds meet at 1. One digit pass costs O(log n) and leaves at most 81 times the digit count. Under the published cap the next value is at most 810, one more step is at most 211, and from there the walk stays inside 0 through 243, whose only cycles are 0 → 0, 1 → 1, and the cycle through 4. LeetCode 202 starts at 1 and stops at 2³¹ − 1. Python's `divmod` on a negative left side does not peel decimal digits.
- **Two speeds, or a set of seen values** — two speeds when extra memory is constant and the answer is a boolean, an entrance, a middle, or a meeting value. A set when the answer is the path, or when linear memory is allowed. On a seven-node cycle the set stores 7 nodes and the two speeds store 2 references.

## Example

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None) -> None:
        self.val = val
        self.next = nxt


def chain(values: list[int], back: int | None = None) -> ListNode | None:
    if not values:
        return None
    nodes = [ListNode(value) for value in values]
    for earlier, later in zip(nodes, nodes[1:]):
        earlier.next = later
    if back is not None:
        nodes[-1].next = nodes[back]
    return nodes[0]


def cycle_start(head: ListNode | None) -> int | None:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            walker = head
            while walker is not slow:
                walker = walker.next
                slow = slow.next
            return walker.val
    return None


def middle(head: ListNode | None) -> int | None:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    return None if slow is None else slow.val


def digit_square_sum(number: int) -> int:
    total = 0
    while number:
        number, digit = divmod(number, 10)
        total += digit * digit
    return total


def is_happy(number: int) -> bool:
    slow = fast = number
    while True:
        slow = digit_square_sum(slow)
        fast = digit_square_sum(digit_square_sum(fast))
        if slow == fast:
            return slow == 1


looping = chain([8, 1, 4, 6, 2, 9, 3], 3)
print(cycle_start(looping), cycle_start(chain([8, 1, 4])), cycle_start(None))
print(middle(chain([8, 3, 5, 1])), middle(chain([8, 3, 5, 1, 9])), middle(None))
print(is_happy(23), is_happy(15), is_happy(1))
# 6 None None
# 5 5 None
# True False True
```

The cycle entrance of the seven-node exercise list is `6`. The straight list and the empty list have none. The even list's second middle is `5`, and the odd list's only middle is `5`. 23 reaches 1. 15 does not. The lists and the integers are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the speed, the cost, and a Python check. The lists and the integers there are exercise inputs.
