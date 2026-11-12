# Stacks — Drills

Original drills for distances, spans, deletions, a four-operator expression, collisions, a two-stack trace, and two comparisons that look legal and answer the wrong question. Each answer has an approach, a cost, and Python. The lists and the strings are exercise inputs. None of these repeats the pair collapse, the next-greater value, the window maximum, the Unix path, the nested decode, the histogram rectangle, or the postfix evaluation already in the pattern catalog.

## Days until a warmer reading

The exercise readings are `[12, 14, 13, 13, 16, 11]`. For each day, how many days until a strictly warmer reading, or 0 if none? Also answer an empty list, `[8]`, `[3, 3, 3]`, `[6, 4, 1]`, and `[2, 3, 5, 8]`.

**Answer:** The distances are 1, 3, 2, 1, 0, and 0. The 12 waits one day for 14. The 14 waits three days for 16. Each 13 waits for that same 16, two days and then one day. A stack of indexes whose readings decrease from bottom to top does this in one pass. Pop while the top is strictly cooler than the new reading, and the distance is the difference of the indexes. Equals stay on the stack, because a tie is not warmer, and a later warmer day can still answer the earlier tie. Each index is pushed once and popped at most once, so the time is O(n) and the extra memory is O(n). An empty list has no days. One reading, a run of ties, and a falling run are all 0s. A rising run waits one day, except the last reading. LeetCode 739, Daily Temperatures, is this distance for temperatures from 30 through 100, length 1 through 10⁵, with 0 when no warmer day exists. This function allows an empty list and any integers.

```python
def days_until_warmer(readings: list[int]) -> list[int]:
    answer = [0] * len(readings)
    stack: list[int] = []
    for i, reading in enumerate(readings):
        while stack and readings[stack[-1]] < reading:
            prev = stack.pop()
            answer[prev] = i - prev
        stack.append(i)
    return answer


print(days_until_warmer([12, 14, 13, 13, 16, 11]))
print(days_until_warmer([]), days_until_warmer([8]), days_until_warmer([3, 3, 3]))
print(days_until_warmer([6, 4, 1]), days_until_warmer([2, 3, 5, 8]))
# [1, 3, 2, 1, 0, 0]
# [] [0] [0, 0, 0]
# [0, 0, 0] [1, 1, 1, 0]
```

## How far a price still covers

The exercise prices are `[9, 4, 9, 9, 11]`. The span of a day is how many consecutive prices, ending today and going backward, are less than or equal to today's price. Report every span. Also answer an empty list, `[5]`, `[2, 2, 2]`, `[8, 6, 3]`, and `[3, 5, 8]`.

**Answer:** The spans are 1, 1, 3, 4, and 5. The first 9 covers only itself. The 4 is below that 9, so it covers only itself. The next 9 is greater than or equal to both prices before it, so its span is 3. The following 9 covers four days, and 11 covers all five. Pop while the top's price is `<=` today's price. Those days are inside the span, and the nearer equal-or-smaller price hides them from any later day that today also covers. The span is the distance back to the index that remains, or `i + 1` when the stack is empty. A strict `<` would leave an equal price on the stack and report a span of 1 for the second of two equal prices. Each index is pushed once and popped at most once, so the time is O(n) and the extra memory is O(n). An empty list has no spans. One price spans 1. Three equal prices span 1, 2, and 3. A falling run spans 1 every day. A rising run spans 1, 2, and 3. LeetCode 901, Online Stock Span, asks for this span one price at a time. Each price is from 1 through 10⁵, and there are at most 10⁴ calls. This function takes the whole list, including an empty one.

```python
def stock_spans(prices: list[int]) -> list[int]:
    answer = []
    stack: list[int] = []
    for i, price in enumerate(prices):
        while stack and prices[stack[-1]] <= price:
            stack.pop()
        answer.append(i - stack[-1] if stack else i + 1)
        stack.append(i)
    return answer


print(stock_spans([9, 4, 9, 9, 11]))
print(stock_spans([]), stock_spans([5]), stock_spans([2, 2, 2]))
print(stock_spans([8, 6, 3]), stock_spans([3, 5, 8]))
# [1, 1, 3, 4, 5]
# [] [1] [1, 2, 3]
# [1, 1, 1] [1, 2, 3]
```

## Fewest parentheses to delete

The exercise string is `a)b(c)d)e(`. Delete as few parentheses as possible so the remaining parentheses are valid, and keep every other character. Also answer an empty string, `abc`, `((`, `))`, and `())(`.

**Answer:** One minimum result is `ab(c)de`. The `)` after `a` has no opener. The `(` at the end has no closer. Removing those two leaves a single matched pair. Push the index of each `(`. On a `)`, pop if an index is waiting, and otherwise mark that `)` for deletion. Indexes still on the stack at the end are `(` that never closed, and they are deleted too. The number of deletions is the number of unmatched parentheses, which is the minimum. Which matched pair you delete is a choice this scan does not take: it keeps every pair that found its partner. The time is O(n) and the extra memory is O(n) for the indexes. An empty string and a string with no parentheses stay as they are. `((` and `))` delete everything. `())(` keeps the first pair and finishes as `()`. LeetCode 1249, Minimum Remove to Make Valid Parentheses, asks for any valid string after a minimum number of parenthesis deletions. The length is 1 through 10⁵, and each character is `(`, `)`, or a lowercase letter. Several outputs can be accepted when more than one parenthesis could be the one removed. This function also accepts the empty string.

```python
def min_remove(text: str) -> str:
    stack: list[int] = []
    drop: set[int] = set()
    for i, ch in enumerate(text):
        if ch == "(":
            stack.append(i)
        elif ch == ")":
            if stack:
                stack.pop()
            else:
                drop.add(i)
    drop.update(stack)
    return "".join(ch for i, ch in enumerate(text) if i not in drop)


print(min_remove("a)b(c)d)e("))
print(repr(min_remove("")), min_remove("abc"), repr(min_remove("((")), repr(min_remove("))")))
print(min_remove("())("))
# ab(c)de
# '' abc '' ''
# ()
```

## Multiply and divide with no parentheses

The exercise expression is `14-3*2+8/3`. Integers are non-negative, the operators are `+`, `-`, `*`, and `/`, and division truncates toward zero. There are no parentheses. What is the value? Also answer `7*2+3`, `8/3`, an empty string, `6-8`, and `2147483647*2147483647/100`, which divides the square of the largest integer in the stated range by 100.

**Answer:** The value is 10. Multiplication and division happen before the surrounding addition: `3*2` is 6 and `8/3` truncates to 2, so the expression is `14 - 6 + 2`. Keep a stack of terms that still have to be added. A `+` or `-` pushes the next number with that sign. A `*` or `/` pops the latest term, combines it with the new number, and pushes the combination back. A sentinel operator at the end flushes the last number. Division truncates toward zero. `//` floors, so `-5 // 2` is -3 while the toward-zero quotient is -2. `int(prev / number)` uses a float. A product of two values near 2³¹ no longer fits in the exact integer range of that float, so the quotient can round. The function divides with integers: the sign of the previous term is restored after `abs(prev) // number`. The numbers in this contract are non-negative, and a subtraction can still leave a negative term for a later multiply or divide. Each character is handled once, so the time is O(n). The stack holds one term per `+` or `-`, so the extra memory is O(n). An empty string returns 0. `7*2+3` is 17. `8/3` is 2. `6-8` is -2. At the top of the stated range, `2147483647*2147483647/100` is 46116860141324206. Float division of that product returns 46116860141324208. A divisor of 0 is outside the contract. LeetCode 227, Basic Calculator II, is this expression for length 1 through 3 · 10⁵, non-negative integers up to 2³¹ - 1, a result that fits in a 32-bit integer, and division that truncates toward zero. `eval` is forbidden there, and it is not used here. The parenthesis form, with no multiplication, is the calculator card in this topic.

```python
def calculate(expression: str) -> int:
    if not expression.strip():
        return 0
    stack: list[int] = []
    number = 0
    sign = "+"
    for ch in expression + "+":
        if ch.isdigit():
            number = number * 10 + int(ch)
            continue
        if ch == " ":
            continue
        if sign == "+":
            stack.append(number)
        elif sign == "-":
            stack.append(-number)
        elif sign == "*":
            stack.append(stack.pop() * number)
        elif sign == "/":
            prev = stack.pop()
            quotient = abs(prev) // number
            stack.append(-quotient if prev < 0 else quotient)
        sign = ch
        number = 0
    return sum(stack)


print(calculate("14-3*2+8/3"))
print(calculate("7*2+3"), calculate("8/3"), calculate(""), calculate("6-8"))
print(calculate("2147483647*2147483647/100"))
# 10
# 17 2 0 -2
# 46116860141324206
```

## Asteroids that meet head-on

A positive asteroid moves right and a negative asteroid moves left. They move at the same speed, so two asteroids meet only when a right-mover has a left-mover somewhere to its right and nothing between them survives. The smaller one explodes. Equal sizes both explode. The exercise row is `[4, -2, 3, -3, -1]`. What remains? Also answer `[-2, -1, 5]`, `[5, 1, -2]`, an empty row, `[3]`, and `[3, -3]`.

**Answer:** `[4]` remains. The -2 meets the 4 and explodes. The 3 and the -3 are the same size and both explode. The -1 then meets the 4 and explodes. A stack holds the asteroids that are still in the row. A left-mover with a right-mover on top collides: pop while the top is smaller, stop and drop the left-mover when the top is larger, and pop the top and drop the left-mover when the sizes are equal. Anything that is still alive is pushed. Left-movers that never meet a right-mover stay, in order, which is why `[-2, -1, 5]` is unchanged. `[5, 1, -2]` loses the 1 and then the -2, and the 5 remains. Each asteroid is pushed once and popped at most once, so the time is O(n) and the extra memory is O(n). An empty row and a single asteroid stay as they are. `[3, -3]` finishes empty. LeetCode 735, Asteroid Collision, is this rule for length 2 through 10⁴, nonzero sizes from -1000 through 1000. This function allows an empty row and one asteroid.

```python
def collide(asteroids: list[int]) -> list[int]:
    stack: list[int] = []
    for size in asteroids:
        alive = True
        while alive and stack and size < 0 < stack[-1]:
            if stack[-1] < -size:
                stack.pop()
                continue
            if stack[-1] == -size:
                stack.pop()
            alive = False
        if alive:
            stack.append(size)
    return stack


print(collide([4, -2, 3, -3, -1]))
print(collide([-2, -1, 5]), collide([5, 1, -2]))
print(collide([]), collide([3]), collide([3, -3]))
# [4]
# [-2, -1, 5] [5]
# [] [3] []
```

## Drop digits and keep the smallest

The exercise numeral is `42035`. Remove 2 digits so the remaining numeral is as small as possible, without leading zeros. Also answer `1002` removing 1, `9` removing 1, `20` removing 2, and `112` removing 1.

**Answer:** Removing 2 digits from `42035` leaves `35`. The 4 and the 2 are larger than the digits that follow them, and `035` loses its leading zero. A stack of digits stays non-decreasing. While removals remain and the top digit is strictly greater than the new digit, pop the top. After the scan, any unused removals delete the end of the stack, which is the largest place still available. Then strip leading zeros, and return `0` when nothing is left. The comparison is strict. `112` removing 1 must stay `11`. Popping an equal digit would turn that numeral into `12`. `1002` removing 1 drops the leading 1 as soon as the first 0 arrives, and the result is `2`. `9` removing 1 is `0`. `20` removing 2 is `0`. Each digit is pushed once and popped at most once, so the time is O(n) and the extra memory is O(n). LeetCode 402, Remove K Digits, is this numeral for `1 <= k <= length <= 10⁵`, digits only, and no leading zero except the numeral `0` itself. A k at least as large as the length returns `0` here, which covers the end of that range.

```python
def remove_k_digits(num: str, k: int) -> str:
    if k >= len(num):
        return "0"
    stack: list[str] = []
    for digit in num:
        while k and stack and stack[-1] > digit:
            stack.pop()
            k -= 1
        stack.append(digit)
    if k:
        stack = stack[:-k]
    trimmed = "".join(stack).lstrip("0")
    return trimmed or "0"


print(remove_k_digits("42035", 2))
print(remove_k_digits("1002", 1), remove_k_digits("9", 1), remove_k_digits("20", 2))
print(remove_k_digits("112", 1))
# 35
# 2 0 0
# 11
```

## Pour only when the outbox is empty

Start from two empty stacks and run this exercise sequence: push 5, push 8, pop, push 1, peek, pop, pop. The end of each list is the top. How many values move from the inbox to the outbox, and what does a pour that ignores a non-empty outbox return for the peek?

**Answer:** The recorded results are a pop of 5, a peek of 8, a pop of 8, and a pop of 1. The first pop pours 8 and then 5, returns 5, and leaves 8 in the outbox. That is two moves. The push of 1 lands on the inbox. The peek sees a non-empty outbox and returns 8 without pouring. The next pop returns that 8. The last pop finds an empty outbox, pours the 1, and returns it. Three values moved, once each. Pouring on the peek even though the outbox holds 8 puts 1 on top of 8. The broken replay then records `[5, 1, 1, 8]`: the peek and the following pop both return 1, and the 8 comes out last. The guard is the whole algorithm. The [Two-stack queue](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card is the same two stacks. This drill counts the moves on a different sequence. LeetCode 232 promises that pop and peek are called only when the queue is non-empty, allows values from 1 through 9, and caps the calls at 100. Its follow-up is the amortized bound this count is measuring.

```python
def replay(always_pour: bool) -> tuple[list[int], int]:
    inbox: list[int] = []
    outbox: list[int] = []
    moves = 0
    seen: list[int] = []

    def pour() -> None:
        nonlocal moves
        if outbox and not always_pour:
            return
        while inbox:
            outbox.append(inbox.pop())
            moves += 1

    def push(value: int) -> None:
        inbox.append(value)

    def pop() -> int:
        pour()
        return outbox.pop()

    def peek() -> int:
        pour()
        return outbox[-1]

    push(5)
    push(8)
    seen.append(pop())
    push(1)
    seen.append(peek())
    seen.append(pop())
    seen.append(pop())
    return seen, moves


print(replay(False))
print(replay(True))
# ([5, 8, 8, 1], 3)
# ([5, 1, 1, 8], 3)
```

## The maximum that was stored as a value

This deque stores values, and once the first window is full it pops the front on every later step. The exercise readings are `[3, 1, 4, 2]` and the window length is 3. What does it report, and what is the maximum of each window?

**Answer:** The buggy scan reports `[4, 2]`. The windows are `[3, 1, 4]` and `[1, 4, 2]`, so the maximums are `[4, 4]`. At the 4, the 3 and the 1 are smaller and they leave the back of the deque. The next step pops the front because the window moved, and the front is now that 4, which is still inside `[1, 4, 2]`. The value that actually left was the 3, and it was already gone. A value has no index, so the deque cannot tell those two facts apart. Store the index, drop the front only when `index <= i - k`, and the same readings report `[4, 4]`. Both scans push each entry once and pop it at most once, so both are linear and both stay inside the window. The correct one stores indexes. The buggy one stores the value, so a moved window and a dominated value look the same. The [Monotonic deque: sliding window maximum](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card is the index version on a different list. LeetCode 239 requires `1 <= k <= length`. This pair of functions uses a k of 3 on a list of 4.

```python
from collections import deque


def window_max_values(values: list[int], k: int) -> list[int]:
    dq: deque[int] = deque()
    out = []
    for i, value in enumerate(values):
        if i >= k and dq:
            dq.popleft()
        while dq and dq[-1] <= value:
            dq.pop()
        dq.append(value)
        if i >= k - 1 and dq:
            out.append(dq[0])
    return out


def window_max_indexes(values: list[int], k: int) -> list[int]:
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


print(window_max_values([3, 1, 4, 2], 3))
print(window_max_indexes([3, 1, 4, 2], 3))
# [4, 2]
# [4, 4]
```

## An equal reading is not strictly greater

The exercise readings are `[6, 6, 2, 6]` and `[5, 5, 5]`. One scan pops while the top is `<` the new value. Another pops while the top is `<=` the new value. For a next strictly greater value, which row is right, and what does the other row write on the ties?

**Answer:** The strict row is `[-1, -1, 6, -1]` on the first list and `[-1, -1, -1]` on the second. Nothing to the right of a 6 is larger than 6, and the 2's next greater value is the last 6. The `<=` row is `[6, 6, 6, -1]` and `[5, 5, -1]`. It records an equal value as if it were greater, and the earlier copy never gets another chance. The stack is still linear either way: each index is pushed once and popped at most once. The wrong operator is a wrong answer at the same cost. The [Monotonic stack: next greater element](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card is the strict scan. LeetCode 496 asks that question only for unique values in a second array, so this tie does not arise there. This drill is one array, and the tie is the point.

```python
def next_greater(values: list[int], strict: bool) -> list[int]:
    answer = [-1] * len(values)
    stack: list[int] = []
    for i, value in enumerate(values):
        while stack and (values[stack[-1]] < value if strict else values[stack[-1]] <= value):
            answer[stack.pop()] = value
        stack.append(i)
    return answer


print(next_greater([6, 6, 2, 6], True))
print(next_greater([6, 6, 2, 6], False))
print(next_greater([5, 5, 5], True))
print(next_greater([5, 5, 5], False))
# [-1, -1, 6, -1]
# [6, 6, 6, -1]
# [-1, -1, -1]
# [5, 5, -1]
```
