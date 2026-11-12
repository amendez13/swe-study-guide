# Stacks

A stack returns the item you stored most recently. Matching brackets, an undo, and a value that has to wait for a later event are that order. A monotonic stack keeps indexes in value order and resolves them when a new value beats the top, in linear time because each index is pushed once and popped at most once. The comparison is strict or it is not, and duplicates are where those two answers split. A deque of indexes is the same idea with an expiration at the other end. These notes are the recognition, the comparisons, and the checks. They are not a catalog of published problems.

## Key Points

- **When a stack fits** — most recent unmatched opener, most recent action, or a value that waits. `git stash pop` with no argument applies `stash@{0}`. A call pushes a frame and a return pops it. CPython's default recursion limit is 1000. A queue, a deque, a heap, or a binary search is the other order.
- **Matching nested structures** — Python's indent stack starts with 0 and never pops it. Deeper columns push. A shallower column has to land on a saved column, and each popped column is one `DEDENT`. Column 2 after 0 and 4 is an error. CPython caps the indent stack at 100 and the parenthesis stack at 200. The HTML parser's current node is the element most recently pushed.
- **A monotonic stack** — next strictly greater pops while the top is `<` the new value. Next greater-or-equal pops while the top is `<=`. Smaller flips the test. Previous reads the top that remains. On `[8, 3, 3, 9, 3]` the strict next-greater row is `[9, 9, 9, -1, -1]` and the greater-or-equal row is `[9, 3, 9, -1, -1]`.
- **Each index is pushed once** — one step on `[5, 4, 3, 2, 9]` pops four indexes, and the sum of the pops is 4. The nested loop is linear. A single pop can still take O(n) time. That is the difference between an aggregate bound and a worst-case call.
- **A deque that remembers the window extreme** — indexes, values decreasing toward the back, front expires, back drops values that are `<=` the new one. The front is the oldest index, so one pop expires it. `[6, 2, 8, 4, 7, 3]` with length 3 yields `[8, 8, 8, 7]`. Time O(n), extra memory O(k). A lazy binary heap is O(n log n). A tree that deletes the leaving value is O(n log k), which is the heap bound on the sliding-windows card.
- **A valid bracket expression (LeetCode-style: Valid Parentheses)** — the top must be the closer's partner, and the stack must end empty. `{[()()]}` is valid. `]`, `[[]`, and `(a)` are not. An empty string is valid here. LeetCode 20 starts at length 1 and allows only the six brackets.
- **The next greater value to the right** — `[7, 2, 8, 4, 4, 9]` is `[8, 8, 9, 9, 9, -1]`. The two 4s both wait for 9 because the test is `<`. LeetCode 496 looks up unique values in a second array. LeetCode 503 wraps.
- **Evaluate plus, minus, and parentheses (LeetCode-style: Basic Calculator)** — flush a finished number, and push `(total, sign)` on `(`. `8-(3-1)` is 6. `-(4+5)` is -9. A closer on an empty stack raises. An unclosed opener leaves the saved pair unused: `(` returns 0, and `8-(3` returns 3. Two minuses in a row are outside the LeetCode contract, and `1--2` returns -1. LeetCode 224 allows unary minus, forbids `eval`, and fits in a signed 32-bit integer.
- **Delete adjacent equal pairs (LeetCode-style: Remove All Adjacent Duplicates in String)** — equal to the top pops, otherwise push. `bookkeeper` becomes `bper`. `zzz` leaves `z`. Join once. LeetCode 1047 is lowercase letters, length at least 1.
- **A queue built from two stacks (LeetCode-style: Implement Queue using Stacks)** — pour the inbox onto the outbox only when the outbox is empty. Push 4, 1, 7, then pop, returns 4 after 3 moves. Four popped values cost 4 moves. One of those pops did 3 of the moves. LeetCode 232 never peeks an empty queue. This class raises.
- **The maximum of every window (LeetCode-style: Sliding Window Maximum)** — `[5, 5, 1, 4, 6]` with length 3 is `[5, 5, 6]`. A falling pair reports the left value. A k outside 1 through the length returns no block. LeetCode 239 keeps k inside that range. A lazy binary heap is O(n log n) and can hold more than k indexes. Deleting the leaving value is O(n log k), the same bound as the sliding-windows card.

## Example

```python
def valid_brackets(text: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            return False
    return not stack


def next_greater(values: list[int]) -> list[int]:
    answer = [-1] * len(values)
    stack: list[int] = []
    for i, value in enumerate(values):
        while stack and values[stack[-1]] < value:
            answer[stack.pop()] = value
        stack.append(i)
    return answer


def pop_counts(values: list[int]) -> list[int]:
    counts = []
    stack: list[int] = []
    for i, value in enumerate(values):
        popped = 0
        while stack and values[stack[-1]] < value:
            stack.pop()
            popped += 1
        counts.append(popped)
        stack.append(i)
    return counts


print(valid_brackets("{[()()]}"), valid_brackets("]"))
print(next_greater([7, 2, 8, 4, 4, 9]))
print(pop_counts([5, 4, 3, 2, 9]), sum(pop_counts([5, 4, 3, 2, 9])))
# True False
# [8, 8, 9, 9, 9, -1]
# [0, 0, 0, 0, 4] 4
```

The bracket check fails on an empty pop. The next-greater scan leaves equal values on the stack until a strictly larger value arrives. The pop counts show one step doing four pops, and the sum of the counts staying within the length of the list. The inputs are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the comparison, the cost, and a Python check. None of them is a published problem from a book list.
