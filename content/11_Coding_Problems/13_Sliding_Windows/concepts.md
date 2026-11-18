## Sliding window
A sliding window is a contiguous span `[left, right]` whose edges move only forward while its state stays equal to that span. Recomputing every span is quadratic. Expand steps `right` and adds. Shrink steps `left` and removes. Slide steps both and keeps the length fixed. The invariant is that the state is exactly `[left, right]` and `left` never decreases. Keeping that edge put is sound when a discarded start cannot become legal again. Each index is added once and removed at most once, so a burst of shrinks is linear across the scan ([Amortized time](#07_Data_Structures_and_Algorithms/01_Algorithmic_Complexity/concepts/amortized-time)). [Sliding window](#07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/concepts/sliding-window), [Sliding window](#07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/concepts/sliding-window), and [Sliding window](#11_Coding_Problems/06_Moderate_Problems/concepts/sliding-window) name the update. Inward indexes on a sorted array are [Two indexes](#11_Coding_Problems/09_Two_Pointers/concepts/two-indexes).

Use it for a contiguous longest span, a shortest span, a count, or a given length. A subsequence can skip. Shrink only when growing makes the condition harder: a non-negative sum, a product of integers at least 1, a distinct count, or "at most k." A fixed length never discards a span for a budget. Cloudflare's weighted minute is the [Sliding Window](#09_System_Design_Interview/17_Rate_Limiting_and_Throttling/concepts/sliding-window) estimate. TCP's receive window, RFC 9293 section 3.8.6, is flow control, and its right edge can move backward. A block maximum is the deque on [When a shrink is not legal](#11_Coding_Problems/13_Sliding_Windows/concepts/when-a-shrink-is-not-legal).

```python
def entries_and_removals(values: list[int], limit: int) -> tuple[int, int]:
    left = 0
    total = 0
    removed = 0
    for right, value in enumerate(values):
        total += value
        while total > limit and left <= right:
            total -= values[left]
            left += 1
            removed += 1
    return (len(values), removed)


print(entries_and_removals([3, 1, 2, 1, 4, 1], 5))
# (6, 4)
```

![Sliding window: a range that only moves forward](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows-1-a-range-that-only-moves-forward.png)

*Source: [`diagrams/sliding-windows.drawio`](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows.drawio), page 1.*

## Fixed-size window
The length is given. There are `n - k + 1` spans when `k` is from 1 through `n`. The first costs `k` additions. Each later span is one addition and one subtraction, with no inner loop, so the O(n) bound is direct. After `right` has reached at least `k - 1`, the total is `values[right - k + 1]` through `values[right]`. On `[8, 2, 6, 4, 10]` and `k` of 2 the totals are 10, 8, 10, and 14. `pandas.Series.rolling(window).mean()` is this update, and a boxcar filter is that mean. The best sum, including a negative, is the [Fixed window: best 3-day total](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) drill.

A `k` of 0, a `k` longer than the list, and an empty list produce no block. A `k` of 1 is the list. `[7, -2, 5]` with `k` of 2 sums to 5, then 3. A negative is legal: a fixed window never drops an index for being too large. Keeping only the best total is O(1) extra memory. Storing every total is O(n - k + 1) memory. Re-summing each block is O(n · k). Subtracting the leaving value does not name the new maximum when that value was the maximum ([When a shrink is not legal](#11_Coding_Problems/13_Sliding_Windows/concepts/when-a-shrink-is-not-legal)).

```python
def fixed_totals(values: list[int], k: int) -> list[int]:
    if k <= 0 or k > len(values):
        return []
    total = sum(values[:k])
    totals = [total]
    for right in range(k, len(values)):
        total += values[right] - values[right - k]
        totals.append(total)
    return totals


print(fixed_totals([8, 2, 6, 4, 10], 2))
print(fixed_totals([8, 2, 6, 4, 10], 1))
print(fixed_totals([8, 2, 6, 4, 10], 0), fixed_totals([8, 2, 6, 4, 10], 6), fixed_totals([], 2))
print(fixed_totals([7, -2, 5], 2))
# [10, 8, 10, 14]
# [8, 2, 6, 4, 10]
# [] [] []
# [5, 3]
```

![Fixed window: the length is part of the problem](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows-2-fixed-window.png)

*Source: [`diagrams/sliding-windows.drawio`](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows.drawio), page 2.*

## Longest window under a budget
Grow `right`, shrink `left` while the span is illegal, and keep the largest legal length. A sum at most a budget needs non-negative values. Growing cannot lower that sum, so an over-budget start stays over if you keep it. Dropping it never skips a valid window, which is why `left` never moves backward. [Sliding window](#11_Coding_Problems/06_Moderate_Problems/concepts/sliding-window) is that rule on a watering log. After each right step, `[left, right]` is legal, and if `left` is positive then `[left - 1, right]` is not. Every later start is a shorter non-negative suffix, so it is legal too. The longest span ending at `right` starts at `left`.

On `[3, 1, 2, 1, 4, 1]` and limit 5 the best length is 3. An empty log is 0. A 9 against 5 shrinks until the window is empty. A value equal to the limit has length 1. Two zeros against 0 have length 2. `right` moves `n` times and `left` at most `n`, so the inner loop is O(n) and extra memory is O(1). Remove a value larger than the limit before recording the length. Recording first counts an illegal span. Sorting destroys the order. Negatives are [Prefix sums](#11_Coding_Problems/06_Moderate_Problems/concepts/prefix-sums) and [When a shrink is not legal](#11_Coding_Problems/13_Sliding_Windows/concepts/when-a-shrink-is-not-legal). Every pair of ends is O(n²).

```python
def longest_at_most(values: list[int], limit: int) -> int:
    left = 0
    total = 0
    best = 0
    for right, value in enumerate(values):
        total += value
        while total > limit and left <= right:
            total -= values[left]
            left += 1
        if total <= limit:
            best = max(best, right - left + 1)
    return best


print(longest_at_most([3, 1, 2, 1, 4, 1], 5))
print(longest_at_most([], 5), longest_at_most([9], 5), longest_at_most([2], 2), longest_at_most([0, 0], 0))
# 3
# 0 0 1 2
```

![Longest valid window: shrink while the span is over budget](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows-3-longest-valid-window.png)

*Source: [`diagrams/sliding-windows.drawio`](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows.drawio), page 3.*

## Shortest window to a target
Record while the span is still legal, then shrink. The longest scan records after the repair. Here the shortest span ending at `right` is the last length before a non-negative sum falls under a positive target. Shrinking lowers that sum. The [Shortest window to a target](../../07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/) drill is the same sum on another list.

On `[4, 2, 5, 1, 3]` and 8 the recorded length is 3, and no neighboring pair reaches 8. An empty list and two 1s against 10 return 0. A value that meets the target has length 1. A non-positive target is outside the contract: every non-negative sum is at least 0, so the empty span and every non-empty span qualify, and this loop never measures the empty one. It returns 0, also the result when no span reaches a positive target. LeetCode 209 uses positive integers, a positive target, lengths 1 through 10⁵, values 1 through 10⁴, and a target through 10⁹, or 0 when none qualifies. Zeros are outside that contract and accepted here. `left` moves at most `n` times: O(n) time and O(1) extra memory. `best` starts at `len(values) + 1`, and returning that sentinel leaks it. Recording after the shrink measures the first illegal length.

```python
def shortest_at_least(values: list[int], target: int) -> int:
    if target <= 0:
        return 0
    left = 0
    total = 0
    best = len(values) + 1
    for right, value in enumerate(values):
        total += value
        while total >= target and left <= right:
            best = min(best, right - left + 1)
            total -= values[left]
            left += 1
    return best if best <= len(values) else 0


print(shortest_at_least([4, 2, 5, 1, 3], 8))
print(shortest_at_least([], 3), shortest_at_least([9], 3), shortest_at_least([1, 1], 10), shortest_at_least([4], 4))
# 3
# 0 1 0 1
```

![Shortest valid window: shrink while the span still qualifies](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows-4-shortest-valid-window.png)

*Source: [`diagrams/sliding-windows.drawio`](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows.drawio), page 4.*

## Window state
State is what one enter and one leave can update: a sum, a product of positive integers, or character counts ([Frequency map and character counting](#07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/concepts/frequency-map-and-character-counting), [Frequency map](#07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/concepts/frequency-map), [Count with a map](#11_Coding_Problems/06_Moderate_Problems/concepts/count-with-a-map)). [A second pass for arrival order](#11_Coding_Problems/10_Hash_Maps_and_Sets/concepts/a-second-pass-for-arrival-order) is a later read of the same counts. Lowercase letters are 26 slots ([Counting and buckets](#11_Coding_Problems/07_Hard_Problems/concepts/counting-and-buckets)), so the compare is constant time. A matches counter starts at the slots that are still 0 and moves by one when a window count lands on the pattern count or leaves it. The window is an anagram when the counter equals 26. Rebuilding each window is O(n · m). A [Rolling hash for substrings](#07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/concepts/rolling-hash-for-substrings) answers "same string." Counts answer "same multiset."

The length is the pattern's. `bca` and `acb` in `bcaacb` match `abc`. Empty text, an empty pattern, or a longer pattern returns 0. An empty pattern would otherwise be `len(text) + 1` blocks. A code point before `a` indexes from the end, so the arrays can agree for the wrong reason. Past `z` raises `IndexError`. Delete a key at 0, or compare arrays: `Counter` ignores zeros. Time is O(n), the arrays are O(1), and a wider alphabet is O(m). LeetCode 438 returns start indexes (lowercase, lengths 1 through 3 · 10⁴), and that list can be O(n). LeetCode 567 returns a boolean (lengths 1 through 10⁴). Both exclude empty strings.

```python
from collections import Counter


def anagram_hits(text: str, pattern: str) -> tuple[int, int]:
    if not pattern or len(pattern) > len(text):
        return (0, 0)
    base = ord("a")
    need = [0] * 26
    have = [0] * 26
    for ch in pattern:
        need[ord(ch) - base] += 1
    matched = sum(slot == 0 for slot in need)

    def bump(idx: int, delta: int) -> None:
        nonlocal matched
        if have[idx] == need[idx]:
            matched -= 1
        have[idx] += delta
        if have[idx] == need[idx]:
            matched += 1

    for ch in text[: len(pattern)]:
        bump(ord(ch) - base, 1)
    by_counter = int(matched == 26)
    by_array = int(have == need)
    for right in range(len(pattern), len(text)):
        bump(ord(text[right]) - base, 1)
        bump(ord(text[right - len(pattern)]) - base, -1)
        by_counter += int(matched == 26)
        by_array += int(have == need)
    return (by_array, by_counter)


print(anagram_hits("bcaacb", "abc"))
print(anagram_hits("aaaa", "aa"), anagram_hits("zz", "z"))
print(anagram_hits("ab", "abcd"), anagram_hits("", "a"), anagram_hits("abc", ""))
print({"a": 1, "b": 0} == {"a": 1}, Counter({"a": 1, "b": 0}) == Counter({"a": 1}))
# (2, 2)
# (3, 3) (2, 2)
# (0, 0) (0, 0) (0, 0)
# False True
```

![Window state: a sum, a count, or a matches counter](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows-5-window-state.png)

*Source: [`diagrams/sliding-windows.drawio`](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows.drawio), page 5.*

![Count of Anagram Windows (LeetCode-style: Find All Anagrams in a String)](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows-6-count-anagram-windows.png)

*Source: [`diagrams/sliding-windows.drawio`](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows.drawio), page 6.*

## Longest substring without repeats
The longest contiguous piece with no repeated character is a window. A subsequence that skips is a different problem. Shrink a set until the new character is gone, then add it and measure. Measuring first counts the repeat. On `diction` the second `i` leaves `ction`, length 5. A space counts. Each character is inserted and removed at most once: O(n) time and O(m) memory. A 26-slot array misses digits, symbols, and spaces. LeetCode 3 allows length 0 through 10⁵ and that alphabet. A dict or a set covers it, and a 128-slot array covers that ASCII range.

`left = max(left, previous + 1)` jumps the gap a set shrinks one character at a time. Without `max`, an index already outside the window pulls `left` backward. On `success` the second `c` sets `left` to 3. The later `s` still has a copy at 0, the buggy assignment sets `left` to 1, and the length 5 holds both copies of `c`. `max(3, 1)` keeps 3 (`suc`, or `ces`). Store the new index after reading the old one, or the jump lands on the current index. A missing character uses `-1`, so `-1 + 1` leaves a left edge at 0. The set only removes the character at `left`, so it cannot move backward. The jump needs `max` for that same bound.

```python
def longest_unique(text: str) -> int:
    seen: set[str] = set()
    left = 0
    best = 0
    for right, ch in enumerate(text):
        while ch in seen:
            seen.remove(text[left])
            left += 1
        seen.add(ch)
        best = max(best, right - left + 1)
    return best


def buggy_jump(text: str) -> int:
    last: dict[str, int] = {}
    left = 0
    best = 0
    for right, ch in enumerate(text):
        if ch in last:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best


def jump_unique(text: str) -> int:
    last: dict[str, int] = {}
    left = 0
    best = 0
    for right, ch in enumerate(text):
        left = max(left, last.get(ch, -1) + 1)
        last[ch] = right
        best = max(best, right - left + 1)
    return best


print(longest_unique("diction"), jump_unique("diction"))
print(buggy_jump("success"), jump_unique("success"))
print(longest_unique(""), longest_unique("aaaa"), longest_unique("a b a"))
# 5 5
# 5 3
# 0 1 3
```

![Longest Stretch With No Repeated Character (LeetCode-style: Longest Substring Without Repeating Characters)](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows-7-longest-no-repeat.png)

*Source: [`diagrams/sliding-windows.drawio`](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows.drawio), page 7.*

![Jump the left edge to one past the previous copy](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows-8-jump-the-left-edge.png)

*Source: [`diagrams/sliding-windows.drawio`](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows.drawio), page 8.*

## Repeating character replacement
The longest piece you can make into one character with at most `k` changes is legal when its length minus its most frequent count is at most `k`. The high-water mark is the largest count seen, and it is not lowered when `left` moves. On `AAAB` with `k` of 0 the mark reaches 3, one slide leaves `AAB`, and the length 3 belongs to `AAA`. Empty text or a negative `k` is 0.

A count rises by at most 1, and only a live count raises the mark, so one added character changes `length - high` by 1 or by 0. One slide restores `length = high + k`. Before any slide the mark is live, so slack can absorb an add that does not raise it. After a slide, the length grows only when the add sets a new live mark. A stale mark cannot authorize a longer window, and the final slice can still be over budget. Recompute the true maximum when the caller wants the slice. Over 26 letters that recompute is still linear. Time is O(n). A dict is O(m), and 26 uppercase slots are O(1). LeetCode 424 is uppercase, length 1 through 10⁵, and `k` from 0 through the length. Fewer than `k` changes is allowed, to any other uppercase letter. A `k` past the length returns the whole string.

```python
def longest_uniform(text: str, k: int) -> tuple[int, str]:
    if k < 0 or not text:
        return (0, "")
    counts: dict[str, int] = {}
    left = 0
    high = 0
    for right, ch in enumerate(text):
        counts[ch] = counts.get(ch, 0) + 1
        high = max(high, counts[ch])
        if (right - left + 1) - high > k:
            counts[text[left]] -= 1
            left += 1
    return (len(text) - left, text[left:])


print(longest_uniform("AAAB", 0))
print(longest_uniform("AAAB", 1))
print(longest_uniform("AAAA", 0), longest_uniform("ABC", 0), longest_uniform("", 2))
# (3, 'AAB')
# (4, 'AAAB')
# (4, 'AAAA') (1, 'C') (0, '')
```

![Longest Run You Can Make Uniform (LeetCode-style: Longest Repeating Character Replacement)](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows-9-longest-run-made-uniform.png)

*Source: [`diagrams/sliding-windows.drawio`](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows.drawio), page 9.*

## When a shrink is not legal
A shrink is a legal discard only when a larger span cannot become legal again. On a longest sum at most 4, `[3, 3, -2]` drops the first 3 at sum 6, then `[3, -2]` has length 2. The `-2` repairs that dropped start: the whole list sums to 4, length 3, and `left` cannot move back. The prefix `[0, 3, 6, 4]` makes that obvious, since `4 - 0` is 4 ([Prefix sums](#11_Coding_Problems/06_Moderate_Problems/concepts/prefix-sums)). Checking every pair of ends is the reference. A fixed window still adds negatives.

Integers at least 1 do not fall as the window grows, so every inner subarray of a legal product window is legal. A zero breaks that. `[2, 0, 5]` under a strict ceiling of 4 stays at product 0, never moves `left`, and counts 6, while `[5]` is illegal and the true count is 5. Dividing that 0 out raises `ZeroDivisionError`. A negative can make a longer product smaller: `[4, -2]` under 3 counts 1 against a true 2, because `left` cannot return to the dropped 4. `[8, 3, 5]` then `[3, 5, 1]` have maxima 8 then 5, and subtracting 8 does not recover 5. [Monotonic deque: sliding window maximum](#07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/concepts/monotonic-deque-sliding-window-maximum) keeps those candidates in linear time. A heap that deletes the leaving value is O(n log k).

```python
def shrink_sum(values: list[int], limit: int) -> int:
    left = 0
    total = 0
    best = 0
    for right, value in enumerate(values):
        total += value
        while total > limit and left <= right:
            total -= values[left]
            left += 1
        if total <= limit:
            best = max(best, right - left + 1)
    return best


def every_sum(values: list[int], limit: int) -> int:
    best = 0
    for start in range(len(values)):
        total = 0
        for end in range(start, len(values)):
            total += values[end]
            if total <= limit:
                best = max(best, end - start + 1)
    return best


def shrink_products(values: list[int], limit: int) -> int:
    left = 0
    prod = 1
    total = 0
    for right, value in enumerate(values):
        prod *= value
        while left <= right and prod >= limit:
            prod //= values[left]
            left += 1
        total += right - left + 1
    return total


def every_product(values: list[int], limit: int) -> int:
    total = 0
    for start in range(len(values)):
        prod = 1
        for end in range(start, len(values)):
            prod *= values[end]
            if prod < limit:
                total += 1
    return total


print(shrink_sum([3, 3, -2], 4), every_sum([3, 3, -2], 4))
print(shrink_products([2, 0, 5], 4), every_product([2, 0, 5], 4))
print(shrink_products([4, -2], 3), every_product([4, -2], 3))
print([7 + -2, -2 + 5])
print([max(block) for block in ([8, 3, 5], [3, 5, 1])])
# 2 3
# 6 5
# 1 2
# [5, 3]
# [8, 5]
```

![When a sliding window is the wrong tool](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows-10-when-a-window-is-wrong.png)

*Source: [`diagrams/sliding-windows.drawio`](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows.drawio), page 10.*

## Window, two pointers, or prefix sums
A named length is the fixed window. A longest contiguous budget, at most k distinct values or at most k changes, is the longest window. A shortest non-negative sum that reaches a quota is the shortest window. A count of products under a ceiling, with values at least 1, adds `right - left + 1`, because every subarray of a legal window is legal. A sorted pair sum is [Two pointers](#11_Coding_Problems/06_Moderate_Problems/concepts/two-pointers) and [Pair sum in a sorted array](#11_Coding_Problems/09_Two_Pointers/concepts/pair-sum-in-a-sorted-array). An unsorted complement is [Pair sum in an unsorted array](#11_Coding_Problems/10_Hash_Maps_and_Sets/concepts/pair-sum-in-an-unsorted-array). A range sum, or a budget that must survive negatives, is [Prefix sums](#11_Coding_Problems/06_Moderate_Problems/concepts/prefix-sums). A block maximum is [Monotonic deque: sliding window maximum](#07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/concepts/monotonic-deque-sliding-window-maximum). The pair loop is the O(n²) check on a short list ([Optimize brute force in steps](#11_Coding_Problems/07_Hard_Problems/concepts/optimize-brute-force-in-steps)).

The non-negative word is what makes the shortest sum legal to shrink. A block maximum only looks like a fixed window, because the leaving value may be the one a total would have remembered. The shrink is linear only when growing makes the condition harder. Two pointers need order or symmetry and do not keep a multiset ([Two pointers, a hash map, or brute force](#11_Coding_Problems/09_Two_Pointers/concepts/two-pointers-a-hash-map-or-brute-force)). Prefix sums answer a range after one build. The shortest span still needs a window or a deque.

```python
def choose(kind: str) -> str:
    return {
        "mean of 5 tank readings": "fixed window",
        "longest stretch with at most 2 status codes": "longest window",
        "fewest non-negative days that reach a quota": "shortest window",
        "maximum inside each block of 4 hours": "monotonic deque",
    }[kind]


print(choose("mean of 5 tank readings"))
print(choose("longest stretch with at most 2 status codes"))
print(choose("fewest non-negative days that reach a quota"))
print(choose("maximum inside each block of 4 hours"))
# fixed window
# longest window
# shortest window
# monotonic deque
```

![A window, two pointers, or prefix sums](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows-11-window-two-pointers-or-prefix-sums.png)

*Source: [`diagrams/sliding-windows.drawio`](/content/11_Coding_Problems/13_Sliding_Windows/diagrams/sliding-windows.drawio), page 11.*
