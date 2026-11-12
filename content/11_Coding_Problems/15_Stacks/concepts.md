## When a stack fits

A stack is a sequence you change only at one end. The value you take off is the one you put on last. Push, pop, peek, and the empty test are the whole interface, and on that end each of them is O(1).

You reach for a stack when the problem's order is "the most recent unfinished item." Four shapes cover the problems in this topic. A closer has to match the opener that is still open, which is brackets, tags, and indentation. An undo removes the latest action. A value you cannot finish yet has to wait for a later event, which is a parenthesis, the next larger reading, or the front of a queue you are building out of stacks. A reversal falls out of the same end: pouring one stack into another flips the order. The [Stack (LIFO)](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card is the structure and the four operations. This card is how to hear the order in the problem statement. A Python list is the usual stack: `append` pushes and `pop()` with no argument pops. That append is amortized O(1) because of buffer growth, which is the [Stack implementation with arrays vs. linked lists](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card.

`git stash` with no arguments is `git stash push`. It records the working directory and the index, then reverts both to match `HEAD`. The latest stash is `refs/stash`. In the reflog, `stash@{0}` is the most recently created stash and `stash@{1}` is the one before it. `git stash pop` with no argument applies `stash@{0}` and removes it when the apply succeeds. A conflict leaves the stash in the list. `git stash drop` can name an older entry, so the list is newest-first and is also addressable. The default pop is the latest entry. A call stack is the same order inside the interpreter. A call pushes a frame and a return pops it. CPython's default recursion limit is 1000, which `sys.getrecursionlimit()` reports unless the process has changed it. The [Explicit stack for converting recursion to iteration](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card and the [Recursive vs. iterative DFS](../../07_Data_Structures_and_Algorithms/05_Trees/) card are what you do when that call stack is the wrong place to store the frames. The three actions below are exercise labels.

```python
undo = []
for action in ["type-a", "type-b", "delete"]:
    undo.append(action)
print([undo.pop() for _ in range(len(undo))])
# ['delete', 'type-b', 'type-a']
```

The list gives back `delete`, then `type-b`, then `type-a`. Nothing in the loop searched for the earliest action. The end of the list was enough.

**Trade-offs.** A stack is O(1) at one end and the wrong shape as soon as you need the other end. The oldest item is a queue, on the [Queue (FIFO)](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card. Both ends are a deque. The smallest of a set that is not ordered by arrival is a heap, on the [Priority queue](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card. A sorted array you can cut in half is [Binary search over a search space](../14_Binary_Search/). The stack uses memory proportional to the number of unfinished items. That is the nesting depth, the undo length, or the window, and it is the cost you name out loud.

**Interview.** Repeat the order you heard: most recent unmatched opener, most recent action, or a value that has to wait. Name the end you will use, and say what an empty pop should do. Raising is the contract on the [Stack and queue as ADTs: contract first, implementation second](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card, because `None` can be a stored value. If the problem also wants the minimum in constant time, that is the [Min stack](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card, which stores the running minimum beside the value.

**Recap.** A stack returns the most recent unfinished item, in constant time at one end. Matching, undo, deferred work, and reversal are the four reasons to pick it. A queue, a deque, a heap, or a binary search is the tool when the order is something else. Say what an empty pop does before you write the loop.

## Matching nested structures

Matching nested structures means every closer pairs with the opener that is still open, and the openers that remain at the end are a failure.

The Python language reference generates `INDENT` and `DEDENT` tokens from a stack of column numbers. Before the first line, a single 0 is pushed, and that 0 is never popped. Each later column is larger than the column under it, so the saved columns increase from the bottom of the stack toward the top. A line whose column equals the top changes nothing. A deeper line pushes that column and emits one `INDENT`. A shallower line has to land on a column that is already on the stack. Every column deeper than the new one is popped, and each pop is one `DEDENT`. At the end of the file, one `DEDENT` is emitted for every column still above 0. A shallower column that matches none of the saved columns is an indentation error. Tabs expand to the next multiple of 8 in that public rule. CPython's lexer, in `Parser/lexer/state.h` on main as of 12 Nov 2026, stores those levels in `layout.stack`, an array of 100 `indentation_level` values (`MAXINDENT`). Each level holds a column and an alternate column. Bracket characters wait on `parenstack`, an array of 200 (`MAXLEVEL`), and `level` counts the open `()[]{}` so a newline inside brackets does not change the indent. The columns below are exercise numbers, measured the way a logical line's indent is measured.

```python
def indent_events(columns: list[int]) -> list[list[str]]:
    stack = [0]
    rows: list[list[str]] = []
    for col in columns:
        if col == stack[-1]:
            rows.append(["same"])
        elif col > stack[-1]:
            stack.append(col)
            rows.append(["indent"])
        else:
            removed = 0
            while len(stack) > 1 and stack[-1] > col:
                stack.pop()
                removed += 1
            if stack[-1] != col:
                rows.append(["error"])
                return rows
            rows.append(["dedent"] * removed)
    end: list[str] = []
    while len(stack) > 1:
        stack.pop()
        end.append("dedent")
    rows.append(end)
    return rows


print(indent_events([0, 4, 8, 4, 0]))
print(indent_events([0, 4, 8, 0]))
print(indent_events([0, 4, 2]))
print(indent_events([0, 4]))
# [['same'], ['indent'], ['indent'], ['dedent'], ['dedent'], []]
# [['same'], ['indent'], ['indent'], ['dedent', 'dedent'], []]
# [['same'], ['indent'], ['error']]
# [['same'], ['indent'], ['dedent']]
```

`[0, 4, 8, 4, 0]` indents twice and dedents once on the way back to 4 and once on the way back to 0. `[0, 4, 8, 0]` dedents twice on the single line that returns to column 0. Column 2, after columns 0 and 4, matches neither saved column, so the line is an error and the function stops. A file that ends at column 4 still owes one `DEDENT`. The HTML parser keeps a stack of open elements. In the living standard, section 13.2.4.2, as fetched on 12 Nov 2026, that stack starts empty and grows downward: the first element pushed is the topmost, and the current node is the bottommost, which is the element most recently added. Popping the current node finishes that element. The same section also has rules for tags that were never closed, so an HTML parser does more than the bracket check on the next card. The [Stack for expression evaluation and bracket matching](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card is that bracket check on a different string.

**Trade-offs.** The stack's height is the nesting depth, so the time is linear in the text and the extra memory is the deepest nest. A counter works for one pair of brackets and loses the type when `()[]{}` are mixed: a `)` can close a `[` and the counter still looks balanced. Re-scanning the whole prefix at every character is quadratic. The indent rule needs the column, not only the depth, because a dedent has to land on a column that was actually opened.

**Interview.** Say which opener the closer has to match, and say what is left at the end. For indentation, say that 0 stays on the stack and that a dedent has to hit a saved column. For tags, say that a real HTML parser also finishes elements that the author never closed. Then offer the linear scan.

**Recap.** Nested matching pushes an opener and pairs a closer with the opener still on top. Python's indent stack starts at 0, stays strictly deeper as it grows, and emits one `DEDENT` per column it pops. A column that hits none of the saved levels is an indentation error. A single counter is enough only when there is one pair of brackets.

## A monotonic stack

A monotonic stack stores indexes whose values stay in order, increasing or decreasing from the bottom toward the top. Before a new index is pushed, every index that would break that order is popped. The new value is the answer for each popped index.

The order is the invariant. For the next strictly greater value, scanning left to right, the values decrease from bottom to top. The top is the nearest index that is still waiting, and it is the smallest waiting value, so a new value that fails to beat the top also fails to beat everything under it. Those buried indexes stay. A new value that beats the top pops it, and keeps popping while the new top is also smaller. Each pop has found its next strictly greater value, because everything between the popped index and the new index was smaller and was already popped. An index that is still on the stack at the end has no greater value to its right. The [Monotonic stack: next greater element](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card, the [Monotonic stack](../../07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/) card, and [A monotonic stack](../07_Hard_Problems/) card are this scan. The indent columns on the previous card are the same shape: each pushed column is strictly deeper than the one under it, and a shallower line pops every column that can no longer be the current indent.

The comparison is the whole bug with duplicates. These eight tests are the templates. "Next" pops from a stack of indexes that are still waiting, and the new value is their answer. "Previous" pops the indexes that can no longer be anyone's answer, and the index that remains on top is the answer for the new value.

- Next strictly greater: pop while the top's value is `<` the new value. An equal stays, so a later greater value can still answer it.
- Next greater or equal: pop while the top's value is `<=` the new value. The equal value is the answer, and the earlier index is gone.
- Next strictly smaller: pop while the top's value is `>` the new value.
- Next smaller or equal: pop while the top's value is `>=` the new value.
- Previous strictly greater: pop while the top's value is `<=` the new value, then read the new top.
- Previous greater or equal: pop while the top's value is `<` the new value, then read the new top.
- Previous strictly smaller: pop while the top's value is `>=` the new value, then read the new top. The [Nearest shorter bar](../../07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/) drill is this test on bar heights.
- Previous smaller or equal: pop while the top's value is `>` the new value, then read the new top.

Using `<=` for a strictly-greater question writes the equal value into the answer and never looks further right. The readings below are exercise numbers.

```python
def next_right(values: list[int], greater: bool, strict: bool) -> list[int]:
    answer = [-1] * len(values)
    stack: list[int] = []
    for i, value in enumerate(values):
        if greater:
            while stack and (values[stack[-1]] < value if strict else values[stack[-1]] <= value):
                answer[stack.pop()] = value
        else:
            while stack and (values[stack[-1]] > value if strict else values[stack[-1]] >= value):
                answer[stack.pop()] = value
        stack.append(i)
    return answer


def previous_left(values: list[int], greater: bool, strict: bool) -> list[int]:
    answer = [-1] * len(values)
    stack: list[int] = []
    for i, value in enumerate(values):
        if greater:
            while stack and (values[stack[-1]] <= value if strict else values[stack[-1]] < value):
                stack.pop()
        else:
            while stack and (values[stack[-1]] >= value if strict else values[stack[-1]] > value):
                stack.pop()
        answer[i] = values[stack[-1]] if stack else -1
        stack.append(i)
    return answer


readings = [8, 3, 3, 9, 3]
print(next_right(readings, True, True))
print(next_right(readings, True, False))
print(next_right(readings, False, True))
print(next_right(readings, False, False))
print(previous_left(readings, True, True))
print(previous_left(readings, True, False))
print(previous_left(readings, False, True))
print(previous_left(readings, False, False))
# [9, 9, 9, -1, -1]
# [9, 3, 9, -1, -1]
# [3, -1, -1, 3, -1]
# [3, 3, 3, 3, -1]
# [-1, 8, 8, -1, 9]
# [-1, 8, 3, -1, 9]
# [-1, -1, -1, 3, -1]
# [-1, -1, 3, 3, 3]
```

On `[8, 3, 3, 9, 3]`, the next strictly greater row is `[9, 9, 9, -1, -1]`. Both 3s wait until 9, because `3 < 3` is false and the first 3 stays on the stack. The next greater-or-equal row is `[9, 3, 9, -1, -1]`. The second 3 answers the first 3, and that first 3 never sees the 9. The next strictly smaller row is `[3, -1, -1, 3, -1]`: 8's next smaller is the first 3, and the second 3 is not smaller than the first. The next smaller-or-equal row is `[3, 3, 3, 3, -1]`. The previous strictly greater row is `[-1, 8, 8, -1, 9]`. The second 3's previous strictly greater is 8, because the first 3 is equal and was popped. The previous greater-or-equal row is `[-1, 8, 3, -1, 9]`. The second 3 stops on the first 3. The previous strictly smaller row is `[-1, -1, -1, 3, -1]`. The 9 is the first value with a strictly smaller value to its left, and that value is 3. The previous smaller-or-equal row is `[-1, -1, 3, 3, 3]`. Store the index. The value alone cannot tell you which copy you answered, and it cannot tell you a distance.

Each index is pushed once. Each index is popped at most once. One step can pop many indexes, so that step is O(n) on a decreasing run followed by a larger value, and the sum of the pops is at most n. The scan is O(n) time and O(n) extra memory. The argument is the next card. A pair of nested loops that walks to the right from every index is O(n²) and is the check on a short list.

**Trade-offs.** The stack is linear only while the pop is a discard you can defend: the popped index has found its answer, or it can never be a later index's answer. A problem that asks for every greater value, rather than the next one, does not get to throw the middle values away. Strict and non-strict answers differ exactly on ties. Writing the wrong one still runs in linear time and fails the duplicate case.

**Interview.** Say the direction, then the comparison, then what a tie should do. Walk one duplicate by hand before you pick `<` or `<=`. Say that you store indexes. Give the aggregate bound in one sentence: every index is pushed once and popped at most once.

**Recap.** A monotonic stack keeps indexes in value order and pops the ones the new value resolves. Next strictly greater pops while the top is `<` the new value, and next greater-or-equal pops while the top is `<=`. Smaller flips the inequality. Previous reads the top that remains after the same kind of pop. Ties are the case that separates those tests, and the whole scan is linear because each index moves once.

## Each index is pushed once

Aggregate analysis charges every push and every pop to the index that moved, then adds those charges up. A loop inside the scan can still be linear when each index is pushed once and popped at most once.

One step of a monotonic scan can pop the whole stack. On a strictly decreasing run followed by a larger value, that step does Θ(n) pops. The next steps have an empty stack. Across the whole scan the pops cannot outnumber the pushes, and there is one push per index, so the total is at most 2n stack operations. That is O(n), even though the worst single step is O(n). The [Amortized time](../../07_Data_Structures_and_Algorithms/01_Algorithmic_Complexity/) card spreads a rare buffer copy across the appends that filled the buffer. The charge here is different and tighter: each index pays for its own push and its own pop, and no index pays twice. The same sentence covers three patterns in this topic. The monotonic scan pops an index when its answer arrives. Adjacent-pair removal pops a character when its twin arrives. A character that survives is never popped. The two-stack queue moves a value from the inbox to the outbox at most once, so a pop that pours n values is O(n) that once, and n operations are O(n) altogether. The readings below are exercise numbers.

```python
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


spike = [5, 4, 3, 2, 9]
print(pop_counts(spike), sum(pop_counts(spike)))
# [0, 0, 0, 0, 4] 4
```

The first four values only push. The 9 pops all four in one step. The sum of the counts is 4, which is n - 1 on a list of 5, and the last index stays on the stack. A narrative that says "the inner loop is n, so the algorithm is n²" charges that one burst as if it happened on every index. It happened once.

**Trade-offs.** The aggregate bound is a statement about the whole scan. It does not make the expensive step cheap for a latency budget that cares about one operation. A queue pop that pours n values still takes O(n) time on that call. Amortized O(1) means n calls take O(n) time. Worst-case O(1) means every call does a constant amount of work, which is what a ring buffer gives you and what this pour does not. Rebuilding a string on every cancelled pair is the version that really is quadratic, because each rebuild copies characters that will be copied again.

**Interview.** When you have a loop inside the scan, say how many times an index can enter the stack and how many times it can leave. If both numbers are one, the total is linear. Separate that from the worst single call when the interviewer asks about latency. Name the quadratic version you are replacing, which is the nested scan or the repeated string copy.

**Recap.** A nested loop is linear when each index is pushed once and popped at most once. One step may pop a whole decreasing run, and that cost is paid by those indexes, not paid again on the next step. The same charge covers a monotonic scan, adjacent-pair removal, and a pour from one stack into another. Amortized O(1) still allows a single call to take O(n) time.

## A deque that remembers the window extreme

A monotonic deque stores indexes of one window so that the front index is the maximum, or the minimum, and both ends can drop an index in O(1).

A fixed sum slides by adding the value that enters and subtracting the value that leaves. Subtracting the leaving value does not tell you the new maximum when that value was the maximum. The [When a sliding window is the wrong tool](../13_Sliding_Windows/) card is that failure. The structure that repairs it needs both ends, so a plain stack is one end short. The [Deque (double-ended queue)](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card is `collections.deque`, with O(1) `popleft`. The [Monotonic deque: sliding window maximum](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card is this pattern. `pandas.Series.rolling(k).max()` is the library call for a k-long maximum. This card does not claim that pandas uses a deque. It is the linear way to answer the same question from indexes.

Keep indexes, and keep their values decreasing from the front toward the back when you want maxima. On each new index, do three things. Drop the front if its index has left the window, which is `index <= i - k`. The front is the oldest index, so at most one index expires on a step, and one pop is enough. Pop the back while its value is smaller than the new value, or equal to it: a smaller value behind a newer larger one can never be the maximum, and an older tie leaves the window first. Push the new index. Once `i >= k - 1`, the front's value is the maximum of the window that ends at `i`. Emitting earlier reports a window that is still short. Storing the value and not the index leaves you unable to tell whether the front has left the window. Popping the front on every slide, because "something left," drops a maximum that is still inside the window when the value that actually left was already dominated and already gone. The readings below are exercise numbers.

```python
from collections import deque


def window_max(values: list[int], k: int) -> list[int]:
    if k <= 0 or k > len(values):
        return []
    window: deque[int] = deque()
    out = []
    for i, value in enumerate(values):
        if window and window[0] <= i - k:
            window.popleft()
        while window and values[window[-1]] <= value:
            window.pop()
        window.append(i)
        if i >= k - 1:
            out.append(values[window[0]])
    return out


print(window_max([6, 2, 8, 4, 7, 3], 3))
print(window_max([5, 5, 1], 2))
# [8, 8, 8, 7]
# [5, 5]
```

On `[6, 2, 8, 4, 7, 3]` with `k` of 3, the 8 pops both the 6 and the 2, and the first full window's maximum is 8. The 4 and then the 7 sit behind that 8. At the last index the 8's index has fallen out, the front becomes 7, and the maximum is 7. The windows are `[6, 2, 8]`, `[2, 8, 4]`, `[8, 4, 7]`, and `[4, 7, 3]`. A `<=` test and a `<` test report the same maximums. `<=` drops the older tie, which cannot outlive the newer equal value. `<` keeps the older tie until the window expires it, and the front is still a maximum. `[5, 5]` with `k` of 2 is 5 either way. Each index is pushed once and popped at most once, from the front or from the back, so the scan is O(n) time. The deque holds only indexes inside the current window, so the extra memory is O(k).

**Trade-offs.** A heap of the live window is also correct, and the cost depends on whether the heap can delete the value that just left. A balanced tree of the k values in the window can delete that value, which is O(n log k) time and O(k) memory. A plain binary heap cannot delete an arbitrary index. The usual lazy version pushes every index and pops an expired index only when it reaches the root. That heap can hold every index seen so far, so the time is O(n log n) and the extra memory is O(n). The deque stays inside the window. Rescanning each window is O(n · k). The deque is the linear answer, and it is the wrong tool for a sum, which only needs the add-and-subtract slide.

**Interview.** Say why a running total cannot produce the new maximum. Name both ends: the front expires, the back drops dominated indexes. Say that you store indexes, and that you emit only after the first full window. Give O(n) time and O(k) memory. If the interviewer asks for a heap, say which one: a window-sized tree is O(n log k), and a lazy binary heap is O(n log n).

**Recap.** The maximum of every window of length k lives at the front of a deque of indexes whose values decrease toward the back. Expire the front when its index leaves, drop smaller and equal values from the back, then push. The scan is linear because each index is pushed once and popped at most once, and the deque stays inside the window. A lazy binary heap answers the same question in O(n log n). A tree that deletes the leaving value answers it in O(n log k).

## A valid bracket expression (LeetCode-style: Valid Parentheses)

A bracket string is valid when every closer matches the opener still on top and the stack is empty at the end.

Push `(`, `[`, and `{`. On a closer, the stack has to be non-empty and the top has to be the partner. Then pop. Any other character fails this checker. An empty string has nothing unmatched, so it is valid here. The strings below are exercise strings.

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


print(valid_brackets("{[()()]}"))
print(valid_brackets("{[(])}"))
print(valid_brackets("[[]"))
print(valid_brackets("]"))
print(valid_brackets(""))
print(valid_brackets("(a)"))
# True
# False
# False
# False
# True
# False
```

`{[()()]}` pushes `{`, `[`, `(`, pops on `)`, pushes `(`, pops on `)`, pops on `]`, pops on `}`. The stack ends empty. `{[(])}` pops nothing on the `]`, because the top is `(`. `[[]` leaves one `[`. `]` pops an empty stack. `(a)` fails on `a`. An odd length is enough to reject a string that contains only brackets, because they pair up, and it is not enough to decide the question: `][` has even length and is invalid. This function does not use that shortcut. It looks at the top.

LeetCode 20, Valid Parentheses, is this question for a string of length 1 through 10⁴ whose only characters are `()[]{}`. The empty string and a letter are outside that contract. This function returns true for the empty string and false for any other character.

The scan is O(n) time. The stack holds at most n openers, so the extra memory is O(n). A counter of net opens loses the type, as the matching card said.

**Trade-offs.** Checking the top is one comparison. Building a tree of the pairs is the same information with more machinery. Ignoring the empty-stack test and popping anyway raises `IndexError` in Python, which is a crash on `]`, or it reads whatever sentinel you forgot to place. Treating a non-empty stack at the end as success accepts `[[]`.

**Interview.** Name the partner map, the empty test, and the final empty test as three separate checks. Walk `]`, a leftover opener, and one crossed pair. Say that an odd length is a shortcut only for a brackets-only alphabet, and that you still have to run the stack for the even cases. Mention LeetCode 20's alphabet and its minimum length if you are matching that contract.

**Recap.** Valid brackets push each opener and require the top to be the closer's partner. The stack has to end empty. An empty pop, a crossed pair, and a leftover opener are the three failures. The scan is linear, and a letter or an empty string is outside LeetCode 20's contract.

## The next greater value to the right

For each value, find the first value to its right that is strictly larger. If there is none, the answer is -1.

This is the next-strictly-greater row of the monotonic card, on one array. Scan left to right with a stack of indexes whose values decrease from bottom to top. Pop while the top's value is `<` the new value, write the new value into those answers, then push the index. Indexes that remain have no strictly greater value to their right, and they keep the -1 they started with. The readings below are exercise numbers.

```python
def next_greater(values: list[int]) -> list[int]:
    answer = [-1] * len(values)
    stack: list[int] = []
    for i, value in enumerate(values):
        while stack and values[stack[-1]] < value:
            answer[stack.pop()] = value
        stack.append(i)
    return answer


print(next_greater([7, 2, 8, 4, 4, 9]))
print(next_greater([]), next_greater([7]), next_greater([4, 4, 4]))
print(next_greater([2, 5, 8]), next_greater([9, 7, 5]))
# [8, 8, 9, 9, 9, -1]
# [] [-1] [-1, -1, -1]
# [5, 8, -1] [-1, -1, -1]
```

On `[7, 2, 8, 4, 4, 9]`, the 8 pops the 2 and then the 7. Both answers are 8. The two 4s do not pop each other, because the test is `<` and `4 < 4` is false. The 9 pops both 4s and then the 8. The answer is `[8, 8, 9, 9, 9, -1]`. A `<=` test would pop the first 4 when the second 4 arrives and write 4, which is not strictly greater, and that first 4 would never see the 9. An empty list has no row. One value has no value to its right. Three equal values stay -1. A strictly increasing list answers with the next neighbor. A strictly decreasing list stays -1.

Each index is pushed once and popped at most once, so the time is O(n) and the extra memory is O(n) for the stack and the answer. The nested scan to the right is O(n²).

LeetCode 496, Next Greater Element I, asks for this answer only for the values in a second array, `nums1`, looked up inside `nums2`. Both arrays hold unique values, `nums1` is a subset of `nums2`, the lengths run from 1 through 1000 with `nums1` no longer than `nums2`, and the values run from 0 through 10⁴. LeetCode 503, Next Greater Element II, walks one array as a circle, so a value may be answered by something to its left. This function is one array, duplicates allowed, no wrap, and -1 when the right side has nothing larger.

**Trade-offs.** Scanning from the right and keeping a stack of candidates answers the same question: the candidates increase as you move toward the side you have not consumed, and the nearest greater candidate is the one you keep. Either direction is linear. The left-to-right scan above writes the answer at the moment it is discovered, which is the pop. Storing values instead of indexes forces a search when the caller wanted the distance, which is a different problem and a different drill.

**Interview.** Say "strictly larger" back, and write `<` only after you have said what a tie does. Walk the two equal 4s. State the aggregate bound. If the interviewer makes the array circular, say that each index is still pushed once, and that you stop after a full extra lap so a value does not answer itself.

**Recap.** The next strictly greater value to the right is a decreasing stack of indexes. Pop while the top is smaller than the new value, and leave equals in place so a later greater value can still answer them. Empty, a single value, ties, a rising run, and a falling run are the edges. LeetCode 496 asks the question for a unique subset of a second array, and LeetCode 503 wraps the array.

## Evaluate plus, minus, and parentheses (LeetCode-style: Basic Calculator)

This evaluator reads a valid expression of non-negative integers, `+`, `-`, parentheses, and spaces, and returns the integer value. A minus may be unary. The function does not call `eval`.

A number is built digit by digit, so `12` is twelve and not the sum of 1 and 2. The running total and a sign remember the operation that is waiting. On `+` or `-`, flush the number you have just finished, then set the sign for the next number. On `(`, push that total and that sign, and start a fresh total at 0 with a positive sign. The expression inside the parentheses is then the same problem, one level down. On `)`, flush the number inside, pop the saved total and sign, and replace the total with `saved + saved_sign * inner`. A sign that appears when no digit is waiting, at the start or just after `(`, is the sign of the next number. That is the unary minus. The saved sign is what makes `8-(3-1)` subtract the inner result rather than add it.

In 1961, in "Making a Translator for ALGOL 60," the second part of the Mathematisch Centrum report on the X1 translator, Dijkstra gave each delimiter a priority number. Identifiers go straight to the output. An operator goes onto a translator stack only after every stacked operator of greater or equal priority has been sent to the output. The machine he targeted evaluates with an accumulator stack: a new value takes the next free accumulator, and an operation combines the two most recently filled accumulators. The `>=` test is why two operators of equal priority come out left to right. The function below is the small case of that idea. Plus and minus do not outrank each other, parentheses save the total, and the digits of one integer stay together. The [Stack for expression evaluation and bracket matching](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card includes the postfix form, where the operator arrives after its operands. The strings below are exercise expressions.

```python
def evaluate(expression: str) -> int:
    total = 0
    sign = 1
    number = 0
    saw_digit = False
    stack: list[tuple[int, int]] = []
    for ch in expression:
        if ch.isdigit():
            number = number * 10 + int(ch)
            saw_digit = True
        elif ch in "+-":
            if saw_digit:
                total += sign * number
                number = 0
                saw_digit = False
            sign = -1 if ch == "-" else 1
        elif ch == "(":
            stack.append((total, sign))
            total = 0
            sign = 1
            number = 0
            saw_digit = False
        elif ch == ")":
            total += sign * number
            number = 0
            saw_digit = False
            prev, prev_sign = stack.pop()
            total = prev + prev_sign * total
            sign = 1
        elif ch != " ":
            raise ValueError(ch)
    return total + sign * number


print(evaluate("12 + 3"), evaluate("8-(3-1)"), evaluate("-(4+5)"))
print(evaluate(" 10 - 2 "), evaluate(""), evaluate("42"), evaluate("2-(3-(4))"))
try:
    evaluate(")")
except IndexError:
    print("closer")
print(evaluate("("))
# 15 6 -9
# 8 0 42 3
# closer
# 0
```

`12 + 3` flushes 12 on the plus and adds 3 at the end, which is 15. `8-(3-1)` pushes `(8, -1)` at the parenthesis. The inner `3-1` finishes as 2. The pop computes `8 + (-1) * 2`, which is 6. `-(4+5)` pushes `(0, -1)` and the pop multiplies 9 by that saved sign, which is -9. Spaces are skipped. An empty string returns 0. `42` is one integer. `2-(3-(4))` is 3. A closer with nothing saved raises `IndexError`. An opener that is never closed, the string `(`, returns 0: the saved pair stays on the stack and is never applied. The function assumes the parentheses match.

Each character is handled once, and the stack grows with the nesting, so the time is O(n) and the extra memory is O(n). Python's `int` is unbounded. A fixed-width accumulator wraps, which this function does not do.

LeetCode 224, Basic Calculator, is this expression. The length is 1 through 3 · 10⁵. The characters are digits, `+`, `-`, `(`, `)`, and space. The expression is valid. Unary `+` is outside that contract, and unary `-` is inside it, including `-(2 + 3)`. There are no two consecutive operators. Every intermediate result fits in a signed 32-bit integer, and `eval` is forbidden. This function also accepts the empty string, uses Python integers, and does not wrap. LeetCode 227 is the same idea with `*` and `/`, no parentheses, and division that truncates toward zero. That operator set is a drill, not this function.

**Trade-offs.** `eval` is shorter and it executes whatever the string contains. A recursive descent parser makes the grammar obvious and uses the call stack as the parenthesis stack, which runs into the recursion limit on a nest of depth 1000. The explicit stack above is the same state, with a depth you can see. A postfix conversion is a second pass. This scanner does the arithmetic as it goes, which is enough when the only operators are plus and minus.

**Interview.** Say you will not call `eval`. Show a two-digit number, a minus in front of a parenthesis, and a nested pair. Say where the sign is stored when you see `(`. Say that an unmatched closer raises, and that the contract you are accepting is a valid expression. If the interviewer adds multiplication, switch structures: a stack of signed terms, with `*` and `/` applied to the latest term before the next `+` or `-`.

**Recap.** Plus and minus share one running total and one sign. A parenthesis pushes that pair and starts a fresh total, and the closer combines the inner total with the saved sign. Digits accumulate, spaces disappear, and a leading minus is a sign with no number flushed yet. The scan is linear. `eval` is the wrong tool, and an unmatched closer is an empty pop.

## Delete adjacent equal pairs (LeetCode-style: Remove All Adjacent Duplicates In String)

Repeatedly delete two adjacent equal characters until no such pair remains. The finished string does not depend on which pair you delete first.

Use the stack as the string built so far. If the new character equals the top, pop. The pair is gone, and the character underneath is now adjacent to whatever comes next. Otherwise push. Join once at the end. Joining on every pop copies the whole prefix every time a pair dies, which is quadratic on a string of alternating pairs. The letters below are exercise letters.

```python
def collapse_pairs(text: str) -> str:
    stack: list[str] = []
    for ch in text:
        if stack and stack[-1] == ch:
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)


print(
    collapse_pairs("bookkeeper"),
    repr(collapse_pairs("abccba")),
    collapse_pairs("zzz"),
    repr(collapse_pairs("")),
)
# bper '' z ''
```

`bookkeeper` cancels `oo`, then `kk`, then `ee`. What remains is `bper`. `abccba` cancels from the middle outward and finishes empty. `zzz` cancels one pair and leaves a single `z`, because the rule removes two characters, not a whole run. An empty string stays empty. Each character is pushed once and popped at most once, so the time is O(n) and the extra memory is O(n).

LeetCode 1047, Remove All Adjacent Duplicates In String, is this problem for lowercase English letters, length 1 through 10⁵. The result is unique. This function also accepts the empty string and any characters. Removing k copies in a row, rather than a pair, is LeetCode 1209 and needs a count beside each character.

**Trade-offs.** A stack of characters is the output, so the extra memory is the size of the answer in the worst case, a string with no pair. Doing the deletions in a loop on a Python string allocates a new string every time. Recursion on the cancelled string adds a call per pair and no clarity. The stack is the direct statement of "the neighbors after this cancellation."

**Interview.** Say that cancelling a pair can create a new pair with the character that was buried, and that the new top is that character. Walk `abccba` or `bookkeeper` for one cancellation that exposes a new pair. Say you join once. Mention that a run of three leaves one.

**Recap.** The stack is the string so far. An equal top pops, and anything else pushes. Later pairs see the characters that survived, so one pass finishes the job. The time is linear because each character is pushed once and popped at most once. Join at the end.

## A queue built from two stacks (LeetCode-style: Implement Queue using Stacks)

A queue returns the oldest value. Two stacks can do that if one of them is allowed to hold the values in reverse, and if you reverse them only when the outgoing stack is empty.

`inbox` receives every push. `outbox` is where pop and peek read. When `outbox` is empty, pour `inbox` onto it: each pop from `inbox` pushes onto `outbox`, which reverses the order, so the oldest value is on top. When `outbox` still has values, leave it alone. Pouring again would reverse the values that are already in the right order. Each value moves from `inbox` to `outbox` at most once, so a sequence of n pushes and n pops does O(n) transfers altogether. One pop can perform all n of those transfers, so that call is O(n). The amortized cost of a pop or a peek is O(1). A push is one append, amortized O(1) for the list's own growth, and it does not pour. The [Two-stack queue](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card is this structure. The trace below uses exercise values. The end of each list is the top of that stack.

```python
class TwoStackQueue:
    def __init__(self) -> None:
        self.inbox: list[int] = []
        self.outbox: list[int] = []
        self.moves = 0

    def push(self, value: int) -> None:
        self.inbox.append(value)

    def _pour(self) -> None:
        if self.outbox:
            return
        while self.inbox:
            self.outbox.append(self.inbox.pop())
            self.moves += 1

    def pop(self) -> int:
        self._pour()
        if not self.outbox:
            raise IndexError("pop from empty queue")
        return self.outbox.pop()

    def peek(self) -> int:
        self._pour()
        if not self.outbox:
            raise IndexError("peek at empty queue")
        return self.outbox[-1]

    def empty(self) -> bool:
        return not self.inbox and not self.outbox


q = TwoStackQueue()
q.push(4)
q.push(1)
q.push(7)
print(q.pop(), q.moves, q.inbox, q.outbox)
q.push(2)
print(q.peek(), q.moves)
print(q.pop(), q.pop(), q.pop(), q.moves, q.empty())
try:
    TwoStackQueue().peek()
except IndexError:
    print("empty")
# 4 3 [] [7, 1]
# 1 3
# 1 7 2 4 True
# empty
```

Push 4, 1, and 7. The first pop finds an empty outbox and pours. Three moves put `[7, 1, 4]` in the outbox, and the pop returns 4. The outbox is then `[7, 1]`, with 1 on top. Peek returns 1 and does not pour, so the move count stays 3. The next two pops return 1 and then 7. The outbox is empty and the inbox holds 2, so the last pop pours once more and returns 2. Four values, four moves. A peek on a fresh queue raises `IndexError`. Pop on an empty queue raises the same way.

LeetCode 232, Implement Queue using Stacks, asks for `push`, `pop`, `peek`, and `empty`, using only stack operations. The values in that contract run from 1 through 9, there are at most 100 calls, and every `pop` and `peek` is called on a non-empty queue. The follow-up asks for amortized O(1) per operation. This class raises on an empty pop or peek, and it accepts any integer.

**Trade-offs.** A `collections.deque` gives worst-case O(1) at both ends, which is the structure you use in Python when you are allowed a queue. Two stacks are the answer when the only primitive is a stack, or when the interviewer has asked for the amortized argument. Pouring while the outbox still has values puts newer values on top of older ones. The next pop is then not the oldest, even though each value still moves only once. A single stack cannot return the oldest value without a second stack or a recursion of the same depth.

**Interview.** Draw both stacks and mark which end is the top. Say the guard out loud: pour only when the outbox is empty. Walk a pop that pours, then a peek that must not pour. Give both bounds: one pop can be O(n), and n operations are O(n) because each value is transferred once. Say what an empty pop does. LeetCode 232 never calls it.

**Recap.** Pushes land on the inbox. Pops and peeks read the outbox, and they pour the inbox only when the outbox is empty. The pour reverses the inbox, so the oldest value comes off first. Each value is transferred at most once, which makes the operations amortized O(1) and leaves a single pour at O(n). Pouring while the outbox still has values breaks the order.

## The maximum of every window (LeetCode-style: Sliding Window Maximum)

Return the maximum of every contiguous block of length k, in order.

This is the deque card, walked on one array. The front index is the maximum of the window that ends at the current index. Expire it when `index <= i - k`. Drop the back while its value is `<=` the new value. Push the new index. Append the front's value once the window has k elements. A k that is outside 1 through the length, including an empty list, returns no blocks. The readings below are exercise numbers.

```python
from collections import deque


def window_maximums(values: list[int], k: int) -> list[int]:
    if k <= 0 or k > len(values):
        return []
    window: deque[int] = deque()
    out = []
    for i, value in enumerate(values):
        if window and window[0] <= i - k:
            window.popleft()
        while window and values[window[-1]] <= value:
            window.pop()
        window.append(i)
        if i >= k - 1:
            out.append(values[window[0]])
    return out


print(window_maximums([5, 5, 1, 4, 6], 3))
print(window_maximums([2, -3, 2], 2))
print(window_maximums([4, 4, 4], 2), window_maximums([9, 7, 5, 3], 2), window_maximums([2, 5, 8], 2))
print(window_maximums([4], 1), window_maximums([], 2), window_maximums([1, 2, 3], 4))
# [5, 5, 6]
# [2, 2]
# [4, 4] [9, 7, 5] [5, 8]
# [4] [] []
```

On `[5, 5, 1, 4, 6]` with k of 3, the second 5 replaces the first because the test is `<=`, and the first window's maximum is that 5. The 1 sits behind it. The 4 replaces the 1 and does not replace the 5, so the next window is still 5. The 6 arrives after that 5 has left the window, pops the 4, and the last window is 6. The blocks are `[5, 5, 1]`, `[5, 1, 4]`, and `[1, 4, 6]`. `[2, -3, 2]` shows a negative that never becomes the maximum. Three equal values stay at that value. A falling run reports the leftmost of each pair, because that value expires when the window moves. A rising run reports the rightmost. One value with k of 1 is that value. An empty list, and a k longer than the list, produce no block.

The time is O(n). The deque holds at most k indexes, so the extra memory is O(k). Checking the max of each block from scratch is O(n · k).

LeetCode 239, Sliding Window Maximum, is this list. The length is 1 through 10⁵, each value is from -10⁴ through 10⁴, and k is from 1 through the length. This function also returns an empty list when k is outside that range.

A plain binary heap can answer the same blocks if you store the value with its index and ignore a root whose index has left the window. Expired indexes stay in the heap until they reach the root, so the heap can hold n indexes. Each push and pop is then O(log n), and the total is O(n log n). A balanced tree that actually deletes the value leaving the window stays at k values and runs in O(n log k). The [Monotonic deque: sliding window maximum](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card quotes that window-sized bound. The deque drops an expired index as soon as it reaches the front, and it never stores an index outside the window.

**Trade-offs.** The deque is the linear solution and it takes a minute to get the two ends right. The lazy heap is easier to remember and costs an extra log n. A sorted multiset of the live window is O(n log k) and O(k) memory, and it is still not linear. Storing values in the deque, so you can avoid indexes, fails when the maximum stays in the window and the value that left was already removed from the back.

**Interview.** Restate k, and ask what to return when k is larger than the array. Walk one step where the old maximum expires and one step where a new value kills the back of the deque. Say O(n) and O(k). If you offer the heap, say whether it deletes the leaving index. Lazy deletion is O(n log n) and can use more than k slots. Deleting the leaving value is O(n log k).

**Recap.** Every window maximum is the front of a deque of indexes. Drop the front when it leaves the window, drop the back while it is less than or equal to the new value, and read the front only after k values have arrived. The scan is linear and the deque stays within the window. A lazy binary heap does the same job in O(n log n), and a k outside 1 through the length yields no block.
