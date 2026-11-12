## Fast and slow pointers

A fast and slow pointer pair is two variables that walk the same chain at different speeds, almost always one step and two steps.

A pointer here holds a node, or `None`. The chain is a singly linked list, or a sequence in which each value has exactly one next value. There is no index. The [Runner (two-pointer) technique](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) card is the middle-finding form of this walk, and [Cycle detection with Floyd's algorithm](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) card is the cycle form. This topic is how to recognize the walk in an interview, how to prove the meeting and the reset, and how the same walk applies when the "node" is only a number. Two indexes that move toward each other on an array are [Two pointers: what a second index buys](../09_Two_Pointers/). Two node pointers a fixed k links apart, both moving one step, are [A fixed gap between two node pointers](../11_Linked_Lists/).

Reach for different speeds when the statement says the structure might loop, asks for the node where a loop begins, asks for the middle node of a list that has no length field, or describes a process that feeds a value back into the same rule until it repeats. A cycle, a middle, and a repeated function are the three shapes.

Pollard's rho factoring method is this walk on a sequence of integers. The polynomial usually written now is x → (x² + 1) mod n. Pollard's original polynomial was (x² − 1) mod n. One copy of the sequence advances one step and the other advances two, which is Floyd's schedule. A greatest common divisor of the two copies' difference and n is a factor of n when that divisor is neither 1 nor n. The name rho is the stem-and-cycle shape of the Greek letter. Linux pathname lookup does not use Floyd for a symlink loop. It counts symlink traversals and returns `ELOOP` at `MAXSYMLINKS`, defined as 40 in `include/linux/namei.h`. The kernel's path-lookup documentation says a loop can be detected without a cap, and a cap is the simple guard against both loops and very long chains that are not loops.

The reusable detection template starts both pointers on the head and moves before it compares. The fast pointer takes two hops, so the loop test has to look at the node and at that node's successor before either hop. The numbers in the block are exercise numbers.

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


def first_meeting(head: ListNode | None) -> tuple[bool, int | None, int]:
    slow = fast = head
    steps = 0
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        steps += 1
        if slow is fast:
            return (True, slow.val, steps)
    return (False, None, steps)


straight = chain([8, 1, 4], None)
looping = chain([8, 1, 4, 6, 2, 9, 3], 3)
only = chain([6], 0)
print(first_meeting(None))
print(first_meeting(chain([4], None)))
print(first_meeting(only))
print(first_meeting(straight))
print(first_meeting(looping))
# (False, None, 0)
# (False, None, 0)
# (True, 6, 1)
# (False, None, 1)
# (True, 2, 4)
```

An empty list never enters the loop, so the answer is no cycle in 0 steps. A single node whose `next` is `None` is the same. A single node whose `next` is itself meets on step 1, on that node. The straight list `8 → 1 → 4` takes one double-step, lands the fast pointer on `4`, and then `4.next` is `None`. The exercise list `8 → 1 → 4 → 6 → 2 → 9 → 3`, with `3` linked back to `6`, meets on step 4 at the node that holds `2`. The later card uses that same list to show why the meeting node is not the entrance.

The walk is O(n) time and O(1) extra memory. The fast pointer follows at most twice as many links as there are nodes, whether it meets or falls off the end. A set of node identities answers the same yes-or-no question in expected linear time and O(n) extra memory. The closing card is that choice.

**Trade-offs.** Two speeds use a constant amount of extra memory and a worst-case linear number of link follows, with no hashing. A set of identities is shorter to explain and spends memory proportional to the length. A faster constant step still detects a cycle when both pointers start on the head. The same step can miss a cycle when the pointers start on different nodes. The entrance arithmetic in the later card is proved for one step and two steps, and a fast step of 3 can meet without that reset landing on the entrance. Checking `fast.next` while `fast` is `None` raises `AttributeError`. The safe test names `fast` first.

**Interview.** Say which question you are answering: a boolean, the entrance node, or the middle. Start both pointers on the head, move, then compare with `is`. Name empty, one node, a self-loop, and a straight list before you talk about a long cycle. Offer the set of identities as the version that spends linear memory, then the two speeds as the constant-memory version. If the statement is an array with indexes, this is the wrong pattern until you can say what the next index is.

**Recap.** Two pointers at different speeds answer cycle and middle questions on a chain that has no indexes. The usual speeds are one step and two steps, both starting at the head, and the comparison is node identity after the move. The walk is linear time and constant extra memory. A set of identities is the linear-memory alternative. Pollard's rho factoring method uses the same one-step and two-step schedule on x → (x² + 1) mod n. Linux symlink lookup stops at 40 traversals instead.

## Why the faster pointer meets the slower one

Once both pointers are on a cycle, and the speeds are one step and two steps, the distance from the fast pointer forward to the slow pointer shrinks by 1 on every iteration, so it reaches 0.

The fast pointer gains one node per iteration on the slow pointer. A gap of g nodes, with g at least 1, is gone after g iterations. The fast pointer cannot jump over the slow one, because the relative speed is 1. If the chain has no cycle, the fast pointer reaches a node whose `next` is `None`, and the loop stops. The exercise chain below is `5 → 10 → 11 → 12 → 13 → 14 → 15`, with `15` linked back to `10`. The first iteration puts the slow pointer on `10` and the fast pointer on `11`, both on the cycle. The forward distance from the fast pointer to the slow pointer is then 5, 4, 3, 2, 1, and 0. They meet on `15`.

A slow step of 1 and a fast step of h, with h greater than 1, also meets when both pointers start on the head. After k iterations the slow pointer has taken k steps and the fast pointer has taken h times k. Once both are on the cycle, those counts name the same node exactly when the cycle length divides k times (h − 1). The smallest positive k is the cycle length divided by the greatest common divisor of (h − 1) and the cycle length, and a large enough multiple of that k is past the stem. The divisor can be greater than 1. That does not block the meeting, because both step counts come from the same k. The lead before you reduce it modulo the cycle length is a multiple of (h − 1). Along the cycle, the distance is only guaranteed to be a multiple of that divisor. On the exercise chain with stem 2 and cycle 5, a fast step of 4 has lead 6, and 6 mod 5 is 1, which is not a multiple of 3. The pointers still meet.

A faster step does not always meet when the pointers start on different nodes. On a cycle of two nodes, start the slow pointer on one node and the fast pointer on the other, and move the fast pointer 3 steps at a time. The fast pointer gains 2 steps on the slow pointer, and 2 does not divide the starting gap of 1, so the gap never closes. The pointers swap places and never land together.

Speeds 1 and 2 are the pair to memorize, because the gap shrinks by 1 and 1 divides every cycle length. The block checks shared-start detection on exercise chains: stem lengths 0 through 11, cycle lengths 1 through 11, and straight chains of length 0 through 11, for speed pairs (1, 2), (1, 3), (1, 4), (2, 5), and (3, 7). It also prints that reduced lead, and the two-node start that never meets.

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


def gaps(head: ListNode) -> list[tuple[int, int, int, int]]:
    slow = fast = head
    rows: list[tuple[int, int, int, int]] = []
    for step in range(1, 8):
        slow = slow.next
        fast = fast.next.next
        distance = 0
        cursor = fast
        while cursor is not slow:
            cursor = cursor.next
            distance += 1
        rows.append((step, slow.val, fast.val, distance))
        if slow is fast:
            return rows
    return rows


def detects(head: ListNode | None, slow_step: int, fast_step: int) -> bool:
    slow = fast = head
    for _ in range(200):
        for _ in range(slow_step):
            if slow is None:
                return False
            slow = slow.next
        for _ in range(fast_step):
            if fast is None:
                return False
            fast = fast.next
        if slow is fast:
            return True
    return False


def modular_gap(stem: int, fast_step: int, length: int) -> int:
    return (stem * (fast_step - 1)) % length


def separated_step3() -> str:
    first = ListNode(1)
    second = ListNode(2)
    first.next = second
    second.next = first
    slow: ListNode | None = first
    fast: ListNode | None = second
    for _ in range(8):
        if slow is None or fast is None or fast.next is None or fast.next.next is None:
            return "fell"
        slow = slow.next
        fast = fast.next.next.next
        if slow is fast:
            return "met"
    return "never"


failures = 0
cycle_checks = 0
pairs = ((1, 2), (1, 3), (1, 4), (2, 5), (3, 7))
for stem in range(12):
    for length in range(1, 12):
        head = chain(list(range(stem + length)), stem)
        for slow_step, fast_step in pairs:
            cycle_checks += 1
            if not detects(head, slow_step, fast_step):
                failures += 1
straight_checks = 0
for length in range(12):
    head = chain(list(range(length)), None)
    for slow_step, fast_step in pairs:
        straight_checks += 1
        if detects(head, slow_step, fast_step):
            failures += 1
print(gaps(chain([5, 10, 11, 12, 13, 14, 15], 1)))
print(failures, cycle_checks, straight_checks)
print(modular_gap(2, 4, 5), detects(chain(list(range(7)), 2), 1, 4))
print(separated_step3())
# [(1, 10, 11, 5), (2, 11, 13, 4), (3, 12, 15, 3), (4, 13, 11, 2), (5, 14, 13, 1), (6, 15, 15, 0)]
# 0 660 60
# 1 True
# never
```

The six rows are the iteration, the slow value, the fast value, and the forward distance. The distance falls by 1 until the pointers are on the same node. The sweep reports 0 misses, 660 cycle checks, and 60 straight-chain checks. 12 stem lengths times 11 cycle lengths times 5 speed pairs is 660. 12 straight lengths times 5 pairs is 60. A straight chain includes the empty list. The next line prints 1 and True. 1 is 6 mod 5, the distance along that cycle, and it is not a multiple of 3. True means the pointers still meet. The last line is the two-node start: a fast step of 3 never meets. The sweep is a finite check. The ratio argument above is what covers every stem and every cycle. Detection is not the entrance. The next cards separate those two questions. A fast step of 3 can meet, and the one-step reset still misses when the slow pointer's step count is not a multiple of the cycle length. A drill shows that miss on a 4-cycle, and a 3-cycle where the same reset hits.

**Trade-offs.** Speeds 1 and 2 need one guard, `fast` and `fast.next`, and the relative speed divides every cycle length. A faster step needs a guard on every hop and a fresh proof if you still want the entrance. There is no asymptotic gain from a larger step. Starting the pointers on different nodes can make a faster step miss a cycle that steps 1 and 2 would still find, because the gap is no longer produced by one shared iteration count. The sweep bound of 200 iterations is only a backstop. On these chain lengths a real meeting happens within a few dozen steps.

**Interview.** Say the shrink-by-1 sentence before you write the loop, and say it applies once both pointers are on the cycle. If the interviewer asks about a fast step of 3, say detection still holds when both start at the head, because the cycle length divides a multiple of the speed gap, and say it can fail when the pointers start apart. Give the two-node cycle as the counterexample. Say the entrance reset is proved for steps 1 and 2, and that it misses for a faster step when the slow pointer's step count at the meeting is not a multiple of the cycle length. Then give a straight list, so the fall-off case is in the same answer as the meeting.

**Recap.** With steps 1 and 2, the distance from the fast pointer forward to the slow pointer shrinks by 1 per iteration on the cycle, so the two pointers meet. A straight chain makes the fast pointer reach `None` instead. A larger constant speed still detects a cycle when both pointers start together, and it can miss when they start apart. On the five speed pairs in the block, all 660 looping chains met and all 60 straight chains fell off. The node where they meet is not, by itself, the entrance of the cycle, and the one-step reset that finds the entrance is proved for steps 1 and 2.

## Does This List Loop? (LeetCode-style: Linked List Cycle)

Decide whether a singly linked list contains a cycle. Return true when some node is reachable again by following `next`, and false when the last node points at `None`.

This is the template from the first card. Both pointers start on the head. Each iteration moves the slow pointer one node and the fast pointer two nodes. If they land on the same node, the list cycles. If the fast pointer cannot take two steps, it does not. Compare with `is`. A second node that stores the same number is a different node. On the exercise list `4 → 1 → 4 → 1 → 4`, with no link back, the second iteration puts the two pointers on different nodes that both hold `4`. A value comparison reports a cycle. Identity reports none.

The order of the loop test matters. `while fast.next and fast` reads `next` before it asks whether `fast` exists. On an empty list, and on the even-length straight list `8 → 3`, that read raises `AttributeError`. On the odd-length straight list `8 → 3 → 5` the fast pointer stops on the last node, `next` is `None`, and the buggy test returns without crashing. A cycle also hides the bug, because the fast pointer never becomes `None`. The drill runs the even and odd lengths side by side.

LeetCode 141, Linked List Cycle, allows 0 to 10,000 nodes and values from −100,000 to 100,000. The tail's link is either absent or a valid index. The follow-up asks for O(1) extra memory. The set of identities is the linear-memory answer. Two speeds are the follow-up. This card uses the same empty list the problem allows.

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


def has_cycle(head: ListNode | None) -> bool:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


def values_look_cyclic(head: ListNode | None) -> bool:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if fast is not None and slow.val == fast.val:
            return True
    return False


def unsafe_scan(head: ListNode | None) -> str:
    fast = head
    try:
        while fast.next and fast:
            fast = fast.next.next
        return "returned"
    except AttributeError:
        return "AttributeError"


repeated = chain([4, 1, 4, 1, 4], None)
at_head = chain([5, 7, 1, 3], 0)
print(has_cycle(None), has_cycle(chain([4], None)), has_cycle(chain([6], 0)))
print(has_cycle(chain([8, 1, 4], None)), has_cycle(at_head), has_cycle(chain([4, 1, 9], 2)))
print(has_cycle(repeated), values_look_cyclic(repeated))
print(unsafe_scan(chain([8, 3], None)), unsafe_scan(chain([8, 3, 5], None)), unsafe_scan(None))
# False False True
# False True True
# False True
# AttributeError returned AttributeError
```

The empty list and the single node `4` have no cycle. The node `6` that points at itself does. `8 → 1 → 4` does not. `5 → 7 → 1 → 3` linked back to `5` is a cycle through the head. `4 → 1 → 9` with `9` linked to itself is a cycle at the tail. The five-node list of alternating values has no cycle, and the value comparison still returns true. The unsafe test crashes on `8 → 3` and on the empty list, and it returns on `8 → 3 → 5`.

Time is O(n). Extra memory is O(1). The set of node identities is expected O(n) time and O(n) extra memory, and a hash collision chain makes that walk quadratic. Two speeds have no hash table, so the linear bound is a worst case.

**Trade-offs.** Two speeds meet the constant-memory follow-up and are easy to point at the wrong field, either `next` before the node or `.val` instead of the node. The identity set is the version to write when the interviewer has not asked for constant memory. It stores every node until a repeat, so a long straight list pays for the whole length and then reports no cycle.

**Interview.** Repeat the question as a boolean about node identity. Write the guard as `fast is not None and fast.next is not None`, then the two moves, then `is`. Give the empty list, the self-loop, the straight list, and one list whose values repeat without a cycle. Mention that an odd-length straight list can hide a reversed guard. State O(n) time and O(1) extra memory, and mention the set as the alternative you would write first if memory were free.

**Recap.** A list loops when the one-step pointer and the two-step pointer land on the same node. They start at the head, and the fast pointer's guard names the node before `next`. Equal values on different nodes are not a cycle. LeetCode 141 allows an empty list and asks for constant extra memory as a follow-up. The unsafe order `fast.next and fast` crashes when `fast` is `None`, which an even-length straight list produces and an odd-length straight list can skip.

## The Node Where the Cycle Starts (LeetCode-style: Linked List Cycle II)

The entrance is the first node on the cycle, the node a tail link points back to. Return that node, or `None` when the list does not cycle.

LeetCode 142, Linked List Cycle II, returns the node rather than a boolean. It allows 0 to 10,000 nodes, values from −100,000 to 100,000, and a tail link that is either absent or a valid index. The follow-up asks for constant extra memory. The [Cycle detection with Floyd's algorithm](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) card shows the reset. This card is why the reset lands on the entrance. The length of the cycle is the extra question you can answer from the meeting node. The [How long is the loop?](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) drill counts that length on a different list.

Both pointers start at the head. Let the stem hold μ nodes before the entrance, and let the cycle hold λ nodes. At the first meeting, the slow pointer has taken t steps and the fast pointer has taken 2t. A node before the entrance has only one path from the head, so two different step counts cannot land on it. The meeting is on the cycle, which means t is at least μ. The two walks share those μ stem steps. After that, the slow pointer travels t − μ steps on the cycle and the fast pointer travels 2t − μ steps on the cycle. Those two distances end on one node, so their difference, t, is a whole number of laps: t = mλ for a positive integer m. The equation does not force m to be 1. When the stem is longer than the cycle, the fast pointer finishes one or more laps before the slow pointer arrives, and m is 2 or more. Those extra laps are multiples of λ, so they cancel when the position is reduced modulo λ.

The meeting node's offset along the cycle is (t − μ) mod λ = (mλ − μ) mod λ = (−μ) mod λ. Put one pointer back on the head and leave the other on the meeting node. Move both one step at a time. The head pointer reaches the entrance after exactly μ steps, and it is not on the cycle before that step, so the two pointers cannot meet earlier, even while the cycle pointer passes the entrance. The pointer that stayed on the meeting node is on the cycle the whole time, so μ steps move it (μ mod λ) nodes forward, plus the full laps hidden inside μ. That is the forward distance from offset (−μ) mod λ back to offset 0. Both pointers arrive on the entrance together. The laps that happened before the meeting do not change this walk, because they already cancelled in the offset.

The exercise list `8 → 1 → 4 → 6 → 2 → 9 → 3`, with `3` linked to `6`, has μ = 3 and λ = 4. The pointers meet at `2` after t = 4 steps, and 4 is 1 × 4. The offset of `2` is 1, and (−3) mod 4 = 1. The forward walk `2 → 9 → 3 → 6` is 3 steps, which is 3 mod 4. The reset takes 3 steps and stops on `6`.

The longer exercise list `10 → 20 → 30 → 40 → 50 → 60 → 70 → 80 → 90`, with `90` linked to `60`, has μ = 5 and λ = 4. They meet at `90` after 8 slow steps, and 8 is 2 × 4, so the fast pointer's gain is two laps, not one. The offset of `90` is 3, and (−5) mod 4 = 3. The forward distance from `90` to `60` is 1, which is 5 mod 4, not 5. The reset still walks all 5 stem steps. The cycle pointer uses those 5 steps as one lap plus the one step, and both pointers arrive on `60`. During that walk the cycle pointer stands on `60` while the head pointer is still on the stem. They are not the same node yet. Stopping at the first time the cycle pointer touches the entrance would be early.

When μ is 0 the head is the entrance. On `11 → 4 → 15` linked back to `11`, the pointers meet on `11`, and the reset sees them already equal, so it takes 0 steps. On a tail self-loop, `4 → 1 → 9` with `9` linked to itself, λ is 1 and μ is 2. They meet on `9`. The reset walks 2 steps, and the pointer on the self-loop stays on `9` because one step forward is `9` again. A node that points at itself is the same case with μ = 0: the meeting is that node and the reset takes 0 steps. A straight list, an empty list, and a single node with `next` of `None` return `None`.

After the meeting, both pointers move one step. Moving the fast pointer two steps again is a different ratio, and this count does not apply. The reset lands on the entrance exactly when t is a multiple of λ. Steps 1 and 2 always make t a multiple of λ, including when m is greater than 1. A fast step of 3 only makes 2t a multiple of λ, so t itself may not be. A drill shows a 4-cycle where the pointers meet after 2 slow steps and the reset never meets, and a 3-cycle where they meet after 3 slow steps and the same reset lands on the entrance.

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


def analyze(head: ListNode | None) -> tuple[int | None, int, int | None]:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            length = 1
            cursor = slow.next
            while cursor is not slow:
                length += 1
                cursor = cursor.next
            steps = 0
            walker = head
            while walker is not slow:
                walker = walker.next
                slow = slow.next
                steps += 1
            return (walker.val, length, steps)
    return (None, 0, None)


def by_identities(head: ListNode | None) -> int | None:
    seen: set[int] = set()
    while head is not None:
        if id(head) in seen:
            return head.val
        seen.add(id(head))
        head = head.next
    return None


def show(values: list[int], back: int | None) -> tuple[int | None, int | None, int, int | None]:
    head = chain(values, back)
    start, length, steps = analyze(head)
    return (start, by_identities(head), length, steps)


print(show([8, 1, 4, 6, 2, 9, 3], 3))
print(show([10, 20, 30, 40, 50, 60, 70, 80, 90], 5))
print(show([11, 4, 15], 0))
print(show([4, 1, 9], 2))
print(show([5, 7, 1, 3], 0))
print(show([6], 0))
print(show([8, 1, 4], None))
print(show([], None))
print(show([4], None))
# (6, 6, 4, 3)
# (60, 60, 4, 5)
# (11, 11, 3, 0)
# (9, 9, 1, 2)
# (5, 5, 4, 0)
# (6, 6, 1, 0)
# (None, None, 0, None)
# (None, None, 0, None)
# (None, None, 0, None)
```

Each row is the entrance from the reset, the entrance from a set of node identities, the cycle length, and the number of reset steps. The two entrance methods agree. The short stem takes 3 reset steps and the cycle is 4 long. The stem of 5 into a cycle of 4 takes 5 reset steps, the full stem, even though the forward distance on the cycle is 1. The whole-list cycle and the cycle through `5` take 0 reset steps because the meeting node is the head. The tail self-loop takes 2 reset steps and has length 1. The straight list, the empty list, and the single node `4` have no entrance.

Finding the entrance is O(n) time and O(1) extra memory. The identity set is expected linear time and O(n) extra memory. Counting the length from the meeting node adds λ steps and no extra memory.

**Trade-offs.** The reset is constant memory and it depends on the 2-to-1 ratio. The identity set finds the same node and spends linear memory, and it is the check to keep beside the reset while you are still unsure. Returning the meeting node skips the proof and, on the short list, returns `2` where the entrance is `6`. Walking the fast pointer by two during the reset follows a ratio this argument does not use.

**Interview.** Draw the stem and the cycle and name μ and λ. Say that t, the slow pointer's steps at the meeting, is a multiple of λ because the fast pointer gained t steps and they stand on one node. Then say the reset walks μ steps. On the cycle that distance is μ mod λ, so a stem longer than the cycle still lands on the entrance. Give one example where μ is smaller than λ and one where it is larger. Say the whole-list cycle takes 0 reset steps. Compare nodes with `is`. Offer the length count as the follow-up after the entrance.

**Recap.** After the one-step and two-step pointers meet, send one back to the head and move both one step at a time. They meet at the entrance. The slow pointer's travel at the first meeting is a multiple of the cycle length, for one lap or for several, so the remaining walk from the meeting node equals the stem length modulo the cycle, and walking the whole stem absorbs the extra laps. A stem longer than the cycle, a cycle through the head, and a self-loop at the tail all use that same reset. LeetCode 142 returns the node and allows an empty list. The meeting node itself is a different node whenever the slow pointer has not landed on the entrance. A fast step of 3 keeps the detection and can lose this reset, because its meeting count need not be a multiple of the cycle length.

## Which middle the loop stops on

The middle this topic returns is the node at 0-based index n // 2. On an even length that is the second of the two middle nodes.

Version A is the loop the [Which middle on an even length?](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) drill calls version A. Both pointers start on the head. The slow pointer moves one step and the fast pointer moves two, while the fast pointer has a successor:

```text
slow = fast = head
while fast is not None and fast.next is not None:
    slow = slow.next
    fast = fast.next.next
```

On the exercise list `8 → 3 → 5 → 1` the two middle nodes are `3` and `5`, and version A stops on `5`. On `8 → 3 → 5 → 1 → 9` there is one middle, `5`, and version A stops there. On `4 → 9` it stops on `9`. On a single node it stays on that node. On an empty list it stays on `None`. The drill's list `1 → 2 → 3 → 4` is the same rule: version A stops on `3`, the second middle.

Version B starts the fast pointer one node ahead. On an even length it stops on the first middle, the last node of the first half. On `8 → 3 → 5 → 1` that node is `3`. On an odd length it stops on the same single middle as version A. The [Split, reverse, and weave](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) card cuts at version B, because `slow.next = None` then separates the halves. Top-down merge sort of a singly linked list uses that same cut. The [A List That Reads the Same Both Ways (LeetCode-style: Palindrome Linked List)](../11_Linked_Lists/) card reverses from version A's node, the first node of the second half, and on an even length that is the second middle.

This topic's middle problem and the drill that unlinks the middle both use version A. If a statement says "the middle" of an even list and does not say which one, state the choice. LeetCode 876 states the second middle. The next card is that problem.

Counting the nodes and then walking n // 2 steps returns the same node as version A. That is two passes, still O(n) time and O(1) extra memory. Copying the nodes into a Python list and indexing at n // 2 is O(n) extra memory and makes the index obvious.

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


def version_a(head: ListNode | None) -> int | None:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    return None if slow is None else slow.val


def version_b(head: ListNode | None) -> int | None:
    if head is None:
        return None
    slow: ListNode | None = head
    fast = head.next
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    return None if slow is None else slow.val


def by_count(values: list[int]) -> int | None:
    if not values:
        return None
    return values[len(values) // 2]


def show(values: list[int]) -> tuple[int | None, int | None, int | None]:
    head = chain(values)
    return (version_a(head), version_b(head), by_count(values))


print(show([]))
print(show([4]))
print(show([4, 9]))
print(show([8, 3, 5, 1]))
print(show([8, 3, 5, 1, 9]))
print(show([7, 8, 9, 1, 2, 6]))
# (None, None, None)
# (4, 4, 4)
# (9, 4, 9)
# (5, 3, 5)
# (5, 5, 5)
# (1, 9, 1)
```

Each row is version A, version B, and index n // 2. Version A matches the index on every row. Version B matches it on the empty list, the single node, and the odd lengths. On the two even lists it stops one node earlier, on the first middle. The length-6 list's second middle is `1` and its first middle is `9`.

**Trade-offs.** Version A is one pass and constant extra memory, and it is the second middle on an even length. Version B is the same cost and the first middle, which is the node you want when the next line cuts the list in half. The length count is easier to check against n // 2 and spends a second pass. The array copy spends linear memory. Choosing B when the caller wanted the second middle, or A when the caller wanted a cut before the second half, is a linear algorithm that returns the neighbor of the requested node.

**Interview.** Ask which middle an even length should return, or state version A and the phrase "second middle, index n // 2." Say that an odd length has one middle and both loops land on it. Mention the palindrome card, which reverses from version A, and the split, which cuts at version B. Give the empty list, one node, two nodes, and one even list you can draw.

**Recap.** Version A, the loop `while fast is not None and fast.next is not None`, returns the node at index n // 2. On an even length that is the second middle, the same node the even-length middle drill calls version A and the same node the palindrome card reverses from. Version B starts the fast pointer one node ahead and, on an even length, stops on the first middle, where a split cuts the list. An odd length has one middle, and both versions stop on it.

## The Middle Node (LeetCode-style: Middle of the Linked List)

Return the middle node of a singly linked list. When the length is even, return the second middle node.

That is version A from the previous card, and it is index n // 2. LeetCode 876, Middle of the Linked List, uses this rule. Its length is from 1 to 100, so the list is never empty, and its values are from 1 to 100. This card also defines an empty list as `None`, and it accepts values outside that range. The exercise list `200 → 3 → 5 → 1` has a value above 100. Its second middle is still `5`.

The steps are the loop itself. Start both pointers on the head. Move one and two while the fast pointer can take two steps. The slow pointer is the answer. A one-node list never enters the loop. A two-node list enters once and leaves the slow pointer on the second node. Counting n and walking n // 2 steps is the same answer in a second pass.

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


def middle(head: ListNode | None) -> int | None:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    return None if slow is None else slow.val


def middle_by_count(values: list[int]) -> int | None:
    if not values:
        return None
    return values[len(values) // 2]


def show(values: list[int]) -> tuple[int | None, int | None]:
    return (middle(chain(values)), middle_by_count(values))


print(show([]))
print(show([4]))
print(show([4, 9]))
print(show([8, 3, 5, 1]))
print(show([8, 3, 5, 1, 9]))
print(show([200, 3, 5, 1]))
print(show([7, 8, 9, 1, 2, 6]))
# (None, None)
# (4, 4)
# (9, 9)
# (5, 5)
# (5, 5)
# (5, 5)
# (1, 1)
```

The two columns are the two-speed walk and index n // 2. They match, including the empty list, the single node, the two-node list, both even lengths, the odd length, and the list whose first value is 200. On `8 → 3 → 5 → 1` the returned node is `5`, the second middle. On `4 → 9` it is `9`.

Time is O(n). Extra memory is O(1). The count-then-walk version is the same class of cost. The array copy is O(n) extra memory.

**Trade-offs.** One pass is what you want once the loop condition is settled. Two passes make the index n // 2 visible and cost the same class of time. The array is the version to name when the caller already holds a Python list. Version B returns the first middle on an even length, which fails this problem and is the right node for a split.

**Interview.** Quote the even-length rule in one sentence: second middle, index n // 2, the same node version A returns. LeetCode 876 starts at one node and limits values to 1 through 100. Say you also define empty as `None` if that input is on the table. Walk `4 → 9` and a five-node list out loud. Mention the palindrome use and the split use so the interviewer hears that you know both middles.

**Recap.** The middle node in this problem is the slow pointer after the fast pointer can no longer take two steps. On an even length that is the second middle, index n // 2, consistent with version A and with the palindrome split of the second half. LeetCode 876 requires at least one node and values from 1 to 100. An empty list is outside that contract, and this card returns `None` for it. The walk is linear time and constant extra memory.

## A sequence of next values is a linked list

A rule that sends each value to exactly one next value is a linked list, even when the values are integers and the link is a function instead of a `next` field.

The shape is a stem into a cycle, the rho that Pollard's factoring method is named for. Happy numbers, the next card, use the rule "sum of the squares of the digits." Finding a repeated value in an array uses the indexes themselves as the nodes.

The array problem: there are n + 1 integers, each in 1 through n, and exactly one value appears more than once. Every other value appears once. Return the repeated value. Do not modify the array. LeetCode 287, Find the Duplicate Number, requires constant extra memory. Its n is from 1 to 100,000, `nums.length` is n + 1, and each `nums[i]` is in 1 through n. The repeated value may appear more than twice. This card uses smaller exercise arrays and the same contract.

Treat index i as a node whose successor is `nums[i]`. Every stored value is at least 1, so nothing points at index 0, and 0 is a stem. Follow the links and the path enters a cycle. The entrance of that cycle is the repeated value, because that value is the node with two incoming links. The reset from the entrance card, starting at 0, returns it.

The exercise array `[2, 5, 1, 4, 3, 2]` has length 6, so n is 5 and every value is in 1 through 5. The value 2 appears twice. The walk from 0 is `0 → 2 → 1 → 5 → 2`. The entrance is 2. One step and two steps meet, one pointer goes back to 0, and both move one index at a time until they meet at 2.

The other constant-memory method searches the value range. Let low and high bound the candidate. The midpoint m is a guess. Count how many entries are at most m. If the count is greater than m, the repeated value is in 1 through m. Otherwise it is above m. That count uses the contract that only one value repeats. It is O(n log n) time and O(1) extra memory. A set of seen values is expected linear time and O(n) extra memory, and it is the version to write when the statement allows the memory. The drill uses different arrays.

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


def find_duplicate_by_count(nums: list[int]) -> int:
    low, high = 1, len(nums) - 1
    while low < high:
        mid = (low + high) // 2
        count = sum(value <= mid for value in nums)
        if count > mid:
            high = mid
        else:
            low = mid + 1
    return low


def show(nums: list[int]) -> tuple[int, int, list[int]]:
    found = find_duplicate(nums)
    counted = find_duplicate_by_count(nums)
    return (found, counted, nums)


print(show([2, 5, 1, 4, 3, 2]))
print(show([1, 1]))
print(show([2, 2, 2]))
print(show([2, 1, 2]))
print(show([1, 4, 6, 3, 2, 5, 4]))
# (2, 2, [2, 5, 1, 4, 3, 2])
# (1, 1, [1, 1])
# (2, 2, [2, 2, 2])
# (2, 2, [2, 1, 2])
# (4, 4, [1, 4, 6, 3, 2, 5, 4])
```

Each row is the cycle entrance, the value-range count, and the array after both calls. The array is unchanged. `[2, 5, 1, 4, 3, 2]` returns 2. `[1, 1]` returns 1. `[2, 2, 2]` returns 2, so a value that appears more than twice is still the entrance. `[2, 1, 2]` returns 2. `[1, 4, 6, 3, 2, 5, 4]` returns 4.

The cycle walk is O(n) time and O(1) extra memory. The value-range count is O(n log n) time and O(1) extra memory. Both leave the array as they found it.

**Trade-offs.** The index cycle is linear time and it is Floyd applied to a function, so the entrance proof has to be in hand. The value-range count is slower by a log factor and easier to justify from the pigeonhole count, without talking about a meeting node. A set is the simplest code and it breaks the constant-memory requirement. Sorting a copy also finds the neighbor pair and spends linear memory. Sorting the original array in place would modify it, which the statement forbids.

**Interview.** Say the contract before the loop: length n + 1, values in 1 through n, one repeated value, the array stays intact, constant extra memory. Then say index 0 is a stem because nothing stores 0. The repeated value is the entrance, found by the same reset as a linked list. Mention the count of values at most m as the other constant-memory method, and give its O(n log n) time. Walk `[2, 5, 1, 4, 3, 2]` from index 0 out loud.

**Recap.** A function from a value to the next value is a linked list. On an array of n + 1 entries drawn from 1 through n, index i points at `nums[i]`, index 0 is a stem, and the cycle entrance is the repeated value. One step and two steps, then the reset back to 0, find it in linear time and constant extra memory without modifying the array. Counting how many values are at most m finds the same value in O(n log n) time. LeetCode 287 requires the constant-memory bound. A set of seen values is the linear-memory version.

## Reaching One by Squaring Digits (LeetCode-style: Happy Number)

A non-negative integer is happy when replacing it, repeatedly, by the sum of the squares of its digits reaches 1. The value 1 maps to 1, so the process stays there. Any cycle that contains 1 is that same one-node cycle, because the next value after 1 is 1. A start that never reaches 1 still repeats. The bound later in this card puts every later value into a finite set, and a walk on a finite set must repeat. The first repeated value is the entrance of a cycle, and that cycle does not contain 1.

LeetCode 202, Happy Number, asks for that boolean. Its n runs from 1 through 2³¹ − 1. This card also defines 0, which is outside that range: 0 maps to 0, so it is not happy. A negative integer is outside the problem, and Python's floor division does not peel its decimal digits. The [Modular arithmetic](../01_Math_and_Logic_Puzzles/) card records that `%` on a negative left side stays non-negative. `divmod(-23, 10)` yields quotient −3 and remainder 7, then quotient −1 and remainder 7, then quotient −1 and remainder 9, and that last pair repeats. A loop that continues while the quotient is non-zero never ends. The function below requires n ≥ 0.

The next value is a function of the current value, so the sequence is the linked list from the previous card. Two speeds detect the cycle. Move before you compare. A loop written `while slow != fast` is false at the start, when both variables still hold n, and returning `slow == 1` would call the exercise value 23 unhappy. The meeting test is `slow == fast`, and the number is happy when that shared value is 1. The value 1 is a cycle of length 1, so a happy number does meet there.

The exercise value 23 goes 23 → 13 → 10 → 1. The two speeds meet at 1, so 23 is happy. The exercise value 15 goes 15 → 26 → 40 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4, and the next value is 16, which is already in that chain. A set notices the repeat at 16. The two speeds meet at 42. Both answers are "not happy." Meeting at 42 does not mean 42 is the first repeated value. It means 42 is on the cycle. The cycle that holds these unhappy values is 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4.

A d-digit number is at least 10^(d − 1). The sum of the squares of its digits is at most 81d, because each digit is at most 9 and 9² is 81. For every d ≥ 4, 81d is less than 10^(d − 1), so one step produces a number with fewer digits. The size of that next number is the stronger fact: it is at most 81d, not merely one digit shorter. The exercise value 9999 has 4 digits. The bound is 324, and 9² four times is exactly 324, which is less than 1000. Under the published cap, n has at most 10 digits, so the next value is at most 810. The largest sum of digit squares for a value in 0 through 810 is 211, from 799. The largest sum for a value in 0 through 243 is 163, from 199. Once a value is at most 243, the next value stays in that range. Every start from 0 through 243 reaches one of three cycles: 0 → 0, 1 → 1, or 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4. A non-negative integer is happy exactly when its walk reaches 1 → 1. The exercise value 7 is happy. The exercise value 10^18 is past the published cap. Its digit-square sum is 1, so it is happy in one step.

2³¹ − 1 is 2147483647. Its digit-square sum is 260, then 40, and the two speeds meet away from 1, so it is not happy. A set of the values until the repeat holds 11 integers on that input. Reading the digits of n is O(log n) work and yields a value of at most 81 times the digit count. Under the cap that value is at most 810, and one more step is at most 211. The meeting then happens inside a fixed finite set, a bounded number of steps on small integers, so the whole check is O(log n) time. A drop of one digit per step, with each step scanning the digits that remain, would be O((log n)^2). The 81d cap is what makes the later steps constant. Two speeds store a constant number of integers, O(1) extra memory. The seen set stores the original n plus each distinct later value. On this cap that list is short. The looser label O(log n) extra memory is what the digit count alone suggests, before the 81d cap.

```python
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


def happy_if_already_equal(number: int) -> bool:
    slow = fast = number
    while slow != fast:
        slow = digit_square_sum(slow)
        fast = digit_square_sum(digit_square_sum(fast))
    return slow == 1


def chain_until_repeat(number: int) -> list[int]:
    seen: list[int] = []
    while number not in seen:
        seen.append(number)
        number = digit_square_sum(number)
    return seen


def quotients(number: int, limit: int) -> list[tuple[int, int, int]]:
    rows: list[tuple[int, int, int]] = []
    for _ in range(limit):
        if number == 0:
            break
        nxt, digit = divmod(number, 10)
        rows.append((number, digit, nxt))
        number = nxt
    return rows


def cycle_keys(limit: int) -> list[tuple[int, ...]]:
    found: set[tuple[int, ...]] = set()
    for start in range(limit + 1):
        seen: list[int] = []
        where: dict[int, int] = {}
        value = start
        while value not in where:
            where[value] = len(seen)
            seen.append(value)
            value = digit_square_sum(value)
        body = seen[where[value] :]
        pivot = body.index(min(body))
        found.add(tuple(body[pivot:] + body[:pivot]))
    return sorted(found)


capped = 2**31 - 1
print(is_happy(23), is_happy(15), is_happy(1), is_happy(7), is_happy(0))
print(is_happy(10**18), digit_square_sum(10**18))
print(happy_if_already_equal(23), is_happy(23))
print(chain_until_repeat(23))
print(chain_until_repeat(15))
print(chain_until_repeat(4))
print(digit_square_sum(9999), digit_square_sum(capped), digit_square_sum(260))
print(max(digit_square_sum(value) for value in range(244)))
print([81 * digits < 10 ** (digits - 1) for digits in range(1, 7)])
print(len(chain_until_repeat(capped)), is_happy(capped))
print(quotients(23, 4))
print(quotients(-23, 4))
print(cycle_keys(243))
# True False True True False
# True 1
# False True
# [23, 13, 10, 1]
# [15, 26, 40, 16, 37, 58, 89, 145, 42, 20, 4]
# [4, 16, 37, 58, 89, 145, 42, 20]
# 324 260 40
# 163
# [False, False, False, True, True, True]
# 11 False
# [(23, 3, 2), (2, 2, 0)]
# [(-23, 7, -3), (-3, 7, -1), (-1, 9, -1), (-1, 9, -1)]
# [(0,), (1,), (4, 16, 37, 58, 89, 145, 42, 20)]
```

23, 1, and 7 are happy. 15 and 0 are not. 10^18 steps to 1 and is happy, past the published cap. The comparison that never moves calls 23 unhappy, and the version that moves first calls it happy. The chain for 15 stops just before 16 repeats. The chain for 4 is the unhappy cycle. 9999 steps to 324. 2147483647 steps to 260 and then 40, the seen chain holds 11 values, and the number is not happy. The strict drop 81d < 10^(d − 1) starts at 4 digits. A non-negative peel of 23 yields digits 3 and 2. The negative peel goes remainder 7 with quotient −3, remainder 7 with quotient −1, then remainder 9 with quotient −1, and stays there. The last row is the only three cycles inside 0 through 243.

**Trade-offs.** Two speeds are O(log n) time and a constant number of integers. The seen set is the same time class and a short list of integers, and it is easier to explain. The sentence that carries the complexity is that one digit pass costs O(log n) and leaves a value of at most 81 times the digit count, at most 810 under the published cap, so the rest of the walk stays in a fixed range. Saying only that the digit count gets smaller leaves an O((log n)^2) reading on the table. Spending the interview on a tighter bound than the 81d sentence is how the solution stays unwritten.

**Interview.** Define happy with the rule and the value 1, then say the sequence must repeat because one step leaves at most 81 times the digit count and the later values stay in a finite range. Write the digit peel for a non-negative integer, move both speeds, and return whether they meet at 1. Give 23 and an unhappy value whose meeting point is on the cycle and is not 1. Mention 0 only if you have extended the contract. Say O(log n) time and O(1) extra memory, and mention the set. If they ask why it terminates, give the 81d sentence, the example 9999 → 324, and the three cycles inside 0 through 243.

**Recap.** A happy number reaches 1 by replacing the value with the sum of the squares of its digits. The sequence is a linked list, so two speeds detect the cycle, and the number is happy when they meet at 1. LeetCode 202 starts at 1 and stops at 2³¹ − 1. A number with 4 or more digits steps to at most 81 times its digit count. Under the published cap that next value is at most 810, and one more step is at most 211, inside 0 through 243. The only cycles in that range are 0 → 0, 1 → 1, and the cycle through 4, so the sequence must repeat, and it is happy exactly when the cycle is 1. That is an O(log n) check. Two speeds use a constant number of integers. A negative quotient under Python's `divmod` is not a digit peel.

## Two speeds, or a set of seen values

The choice follows what the statement asks you to return, and how much extra memory it allows.

A yes-or-no cycle question with constant extra memory is two speeds. The time is O(n) in the worst case, because the walk follows links and does not hash. A set of node identities is expected linear time, O(n) extra memory, and quadratic time if every hash collides. The entrance is the same two speeds plus the reset, still O(1) extra memory. The set finds the entrance by recording each node until one repeats, and on the exercise list `8 → 1 → 4 → 6 → 2 → 9 → 3` linked back to `6` that record holds all 7 nodes.

A caller who wants every value up to the repeat needs the set. Two speeds do not keep the path. The middle of a linked list, under constant extra memory, is version A. If the caller already has a Python list, index n // 2 is the same node and the copy has already been paid for. A happy number under constant extra memory is two speeds on the digit function. For the exercise value 23 the seen set holds 4 integers, 23, 13, 10, and 1, so the set is also a short answer. The duplicate in 1 through n, when linear memory is allowed, is a set of values. On `[2, 5, 1, 4, 3, 2]` that set holds 5 integers. The index cycle is what you switch to when the statement requires constant extra memory and forbids modifying the array.

The edge list that checks a cycle answer is empty, one node, a self-loop, a cycle through the head, a self-loop at the tail, and a straight list whose values repeat. The edge list that checks a middle is empty, one node, two nodes, an even length, and an odd length.

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


looping = chain([8, 1, 4, 6, 2, 9, 3], 3)
print(("cycle-bool", "two-speeds", 2, len(values_until_repeat(looping))))
print(("values-before-repeat", "set", len(values_until_repeat(looping))))
print(("happy-23", "two-speeds", 2, len(happy_values(23))))
print(("duplicate-memory-ok", "set", len({2, 5, 1, 4, 3, 2})))
# ('cycle-bool', 'two-speeds', 2, 7)
# ('values-before-repeat', 'set', 7)
# ('happy-23', 'two-speeds', 2, 4)
# ('duplicate-memory-ok', 'set', 5)
```

The first row is a boolean cycle question: two references against a set that stores 7 nodes. The second row is the question that asks for those values, which is the set. The third row is 23: two integers against a chain of 4. The fourth row is the duplicate array with memory allowed: the set of its values has size 5.

**Trade-offs.** Two speeds meet a constant-memory bound and return a boolean, an entrance, or a middle, not the list of visited values. The set returns that list and spends linear memory, and its worst case depends on hashing. The value-range count for the duplicate is constant memory and O(n log n) time. Copying a linked list into an array makes the middle an index and spends linear memory.

**Interview.** Start from the sentence the interviewer asked. Boolean cycle, tight memory: two speeds. Entrance as well: the reset, still two references. The values along the way: a set. Middle of a linked list: version A, and say the second middle. Happy number: two speeds, with the set as the short alternative. Duplicate, constant memory, array unchanged: the index cycle or the count. Then name the edges that match the question you picked.

**Recap.** Two speeds are the constant-memory tool for a cycle, an entrance, a middle, and a repeated function. A set of seen nodes or values is the tool when the answer is the path, or when linear memory is allowed and the code should stay obvious. On the seven-node exercise cycle the set stores 7 nodes and the two speeds store 2 references. The duplicate and the happy number are the same choice applied to a function.
