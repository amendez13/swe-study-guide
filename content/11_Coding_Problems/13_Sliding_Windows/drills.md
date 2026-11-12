# Sliding Windows — Drills

Original drills for a fixed block, a longest span, a shortest span, and the cases where a shrink is not a legal discard. Each answer has an approach, a cost, and Python. The lists and the strings are exercise inputs, not measured data. None of these repeats the 3-day total, the liter-budget hours, or the shortest sum already in the pattern catalog.

## Moving average of the last k readings

The exercise readings are `[6, 3, 9, 12, 6, 15]`. Report the average of every contiguous block of 3 readings, then say what a block length of 0, a block length of 7, an empty list, and a block length of 2 on `[4, 4, 4, 4]` produce. These totals divide by the block length with nothing left over.

**Answer:** The block totals are 18, 24, 27, and 33, so the averages are 6, 8, 9, and 11. Fill the first block with a sum, then add the reading that enters and subtract the reading that leaves. A length of 0 is not a block, a length longer than the list has no block, and an empty list has no block, so each of those returns an empty list. Four 4s in blocks of 2 average to 4, 4, and 4. The slide is O(n) time. Storing every average uses O(n - k + 1) memory. Keeping only the latest average uses O(1) extra memory. Negatives would still add and subtract correctly, because a fixed block does not shrink on a budget. The [Fixed window: best 3-day total](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) drill is that best-sum form, on a different list. This drill reports every average.

```python
def moving_averages(readings: list[int], k: int) -> list[int]:
    if k <= 0 or k > len(readings):
        return []
    total = sum(readings[:k])
    averages = [total // k]
    for right in range(k, len(readings)):
        total += readings[right] - readings[right - k]
        averages.append(total // k)
    return averages


print(moving_averages([6, 3, 9, 12, 6, 15], 3))
print(moving_averages([6, 3, 9, 12, 6, 15], 0))
print(moving_averages([6, 3, 9, 12, 6, 15], 7))
print(moving_averages([], 3))
print(moving_averages([4, 4, 4, 4], 2))
# [6, 8, 9, 11]
# []
# []
# []
# [4, 4, 4]
```

## At most two distinct readings

The exercise ids are `[4, 4, 5, 4, 6, 6, 5, 5]`. What is the longest contiguous stretch that uses at most two distinct ids? Also answer an empty list, a single id, a run of one id, and `[1, 2, 3]`.

**Answer:** The longest stretch has length 4. `[4, 4, 5, 4]` is one such stretch, and `[6, 6, 5, 5]` is another. Grow the right end and count ids in a map. While the map holds three ids, drop the left id and delete the key whose count hits 0. Each index enters once and leaves at most once, so the scan is O(n) time. The map holds at most three keys, so the extra memory is O(1) for this budget of two. An empty list has length 0. One id, and a run of one id, have the length of the list. `[1, 2, 3]` has length 2, because the third distinct id forces a shrink. LeetCode 904, Fruit Into Baskets, is this length with at most two types, a length from 1 through 10⁵, and type ids in `0 .. length - 1`. This drill allows an empty list and any integers.

```python
def longest_two(values: list[int]) -> int:
    counts: dict[int, int] = {}
    left = 0
    best = 0
    for right, value in enumerate(values):
        counts[value] = counts.get(value, 0) + 1
        while len(counts) > 2:
            counts[values[left]] -= 1
            if counts[values[left]] == 0:
                del counts[values[left]]
            left += 1
        best = max(best, right - left + 1)
    return best


print(longest_two([4, 4, 5, 4, 6, 6, 5, 5]))
print(longest_two([]), longest_two([7]), longest_two([3, 3, 3]), longest_two([1, 2, 3]))
# 4
# 0 1 3 2
```

## Products that stay under a ceiling

The exercise factors are `[2, 3, 4, 1, 5]`, each at least 1. How many contiguous blocks have a product strictly under 12? What do an empty list, a single 8 against ceilings 5 and 9, a ceiling of 1, and `[1, 1, 1]` against a ceiling of 2 return?

**Answer:** Eight blocks: `[2]`, `[2, 3]`, `[3]`, `[4]`, `[4, 1]`, `[1]`, `[1, 5]`, and `[5]`. `[2, 3, 4]` is 24, which is not under 12, and the scan shrinks past it. Because every factor is at least 1, a shorter block cannot have a larger product, so once the window product is under the ceiling, every block inside it is under the ceiling too. Each right end therefore adds `right - left + 1` new blocks, one for each legal start. The right index and the left index each move at most n times, so the time is O(n) and the extra memory is O(1). The division is exact: the product was built by multiplying the factor you divide out. Python's `int` grows, so the product stays exact. A fixed-width multiply can wrap, which is the [Overflow-safe arithmetic](../06_Moderate_Problems/) card. An empty list contributes 0. A single 8 is not under 5 and is under 9. A ceiling of 1 rejects every product, because a product of integers that are at least 1 is at least 1. Three 1s under a ceiling of 2 contribute all six blocks. LeetCode 713, Subarray Product Less Than K, is this count for factors from 1 through 1000, a length from 1 through 3 · 10⁴, and a ceiling from 0 through 10⁶. A zero or a negative factor is outside that contract and outside this function.

```python
def count_under(values: list[int], ceiling: int) -> int:
    if ceiling <= 1:
        return 0
    left = 0
    prod = 1
    total = 0
    for right, value in enumerate(values):
        prod *= value
        while left <= right and prod >= ceiling:
            prod //= values[left]
            left += 1
        total += right - left + 1
    return total


print(count_under([2, 3, 4, 1, 5], 12))
print(count_under([], 5), count_under([8], 5), count_under([8], 9), count_under([2, 3], 1), count_under([1, 1, 1], 2))
# 8
# 0 0 1 0 6
```

## Smallest span that covers the pattern

The exercise text is `zbazab` and the pattern is `aab`. Return the shortest contiguous piece that contains at least two `a`s and one `b`. If two pieces share that length, return the earlier one. What does `xyz` against `ab` return, and what does `AaBbA` against `aA` return?

**Answer:** The shortest piece is `baza`. A set of distinct letters would accept a piece with one `a`, and `baza` is the witness that the counts matter. Grow the right end until every pattern letter has met its count, record the piece, and shrink while the piece still covers the pattern. The shrink is where the shortest piece that ends at this right index shows up. `xyz` never covers `ab`, so the result is an empty string. `AaBbA` against `aA` is case sensitive and returns `Aa`. Each index enters once and leaves at most once, so the time is O(n). The maps hold one entry per distinct letter in the text and the pattern. LeetCode 76, Minimum Window Substring, returns one minimum covering piece, or an empty string when none exists. Its tests promise that piece is unique, so they do not ask which tie to keep. Both strings may mix letter cases, lengths run from 1 through 10⁵, and a repeated pattern letter must be covered that many times. This drill returns the earliest piece when two pieces share the minimum length, and it maps an empty pattern or an empty text to an empty string.

```python
def smallest_cover(text: str, pattern: str) -> str:
    if pattern == "" or text == "":
        return ""
    need: dict[str, int] = {}
    for ch in pattern:
        need[ch] = need.get(ch, 0) + 1
    have: dict[str, int] = {}
    formed = 0
    left = 0
    best_len = len(text) + 1
    best_start = 0
    for right, ch in enumerate(text):
        if ch in need:
            have[ch] = have.get(ch, 0) + 1
            if have[ch] == need[ch]:
                formed += 1
        while formed == len(need) and left <= right:
            length = right - left + 1
            if length < best_len:
                best_len = length
                best_start = left
            left_ch = text[left]
            if left_ch in need:
                have[left_ch] -= 1
                if have[left_ch] < need[left_ch]:
                    formed -= 1
            left += 1
    if best_len == len(text) + 1:
        return ""
    return text[best_start : best_start + best_len]


print(repr(smallest_cover("zbazab", "aab")))
print(repr(smallest_cover("xyz", "ab")))
print(repr(smallest_cover("AaBbA", "aA")))
print(repr(smallest_cover("", "ab")), repr(smallest_cover("abc", "")))
# 'baza'
# ''
# 'Aa'
# '' ''
```

## The jump that walks backwards

This unique-character scan stores the last index of each character. On the exercise string `abba` it returns 3. The true length is 2. Why does the left edge move backward, and what does the repaired scan return for `abba`, `success`, an empty string, and `aaaa`?

```python
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
```

**Answer:** The second `b` in `abba` puts the left edge on that `b`. The final `a` has an earlier copy at index 0, and `0 + 1` is 1, which is behind the left edge. The span from index 1 is `bba`, length 3, and it contains two `b`s. The repair is `left = max(left, previous + 1)`, so the old `a` does not pull the edge backward and the length stays 2. `deed` is 2, an empty string is 0, and `bbbb` is 1. Read the stored index before you overwrite it. The time is O(n) and the map is proportional to the distinct characters. The jump card on this topic walks the same bug through `success`. This drill is `abba`.

```python
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


print(buggy_jump("abba"), jump_unique("abba"))
print(jump_unique("deed"), jump_unique(""), jump_unique("bbbb"))
# 3 2
# 2 0 1
```

## Ones you can buy with k flips

The exercise bits are `[1, 0, 1, 1, 0, 0, 1, 1]`. You may flip at most 2 zeros into ones. What is the longest contiguous run of ones you can produce? Also answer an empty list, three zeros with 0 flips, three zeros with 2 flips, three ones with 0 flips, and `[0, 1, 0]` with 0 flips.

**Answer:** The longest run has length 6, the stretch `[1, 1, 0, 0, 1, 1]` with both zeros flipped. Count zeros inside the window and shrink while that count passes `k`. You are buying ones, so a run of zeros is not a win unless you flip them. That is a different budget from "make the window any one character." Each index enters once and leaves at most once, so the time is O(n) and the extra memory is O(1). An empty list has length 0. Three zeros with no flips have length 0. Three zeros with 2 flips have length 2. Three ones with no flips have length 3. `[0, 1, 0]` with no flips has length 1. LeetCode 1004, Max Consecutive Ones III, is this length on bits that are 0 or 1, with a length from 1 through 10⁵ and `k` from 0 through the length. This drill allows an empty list.

```python
def longest_ones(bits: list[int], k: int) -> int:
    left = 0
    zeros = 0
    best = 0
    for right, bit in enumerate(bits):
        zeros += int(bit == 0)
        while zeros > k and left <= right:
            zeros -= int(bits[left] == 0)
            left += 1
        best = max(best, right - left + 1)
    return best


print(longest_ones([1, 0, 1, 1, 0, 0, 1, 1], 2))
print(longest_ones([], 1), longest_ones([0, 0, 0], 0), longest_ones([0, 0, 0], 2))
print(longest_ones([1, 1, 1], 0), longest_ones([0, 1, 0], 0))
# 6
# 0 0 2
# 3 1
```

## The negative that the shrink already dropped

The exercise list is `[5, 1, -4]` and the limit is 5. A longest-window shrink that treats the sum as monotone returns 2. What is the true longest contiguous sum that is at most 5, and which prefix subtraction shows the span the shrink dropped?

**Answer:** The true length is 3. The whole list sums to 2, which is inside the limit. The shrink adds 5, adds 1, sees 6, and drops the 5 before `-4` arrives. The later `-4` would have pulled `[5, 1, -4]` back to 2, and the left index cannot move backward. The prefix array is `[0, 5, 6, 2]`. The sum from the start through the last index is `2 - 0`, which is 2. A fixed block still adds the negative: blocks of length 2 sum to 6 and then -3. The [Prefix sums](../06_Moderate_Problems/) card is the range subtraction. The dynamic shrink is the wrong tool once a value can be negative. The O(n²) check is the reference that catches it. The concept card walks the same failure on `[3, 3, -2]`. This drill is `[5, 1, -4]`.

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


def prefix(values: list[int]) -> list[int]:
    sums = [0]
    for value in values:
        sums.append(sums[-1] + value)
    return sums


values = [5, 1, -4]
sums = prefix(values)
print(shrink_sum(values, 5), every_sum(values, 5))
print(sums, sums[3] - sums[0])
print([5 + 1, 1 + -4])
# 2 3
# [0, 5, 6, 2] 2
# [6, -3]
```

## Fixed, longest, shortest, or a deque

Label each exercise prompt with `fixed window`, `longest window`, `shortest window`, or `monotonic deque`.

1. The average of the last 8 closing prices, recomputed after each new close.
2. The longest contiguous stretch of sensor ids that uses at most 2 distinct ids.
3. The fewest contiguous minutes, with non-negative counts, whose sum is at least 20.
4. The maximum value inside every contiguous block of 4 samples.

**Answer:** The average names a length, 8, so it is a fixed window. The sensor stretch asks for a longest contiguous span under a distinct-count budget, so it is a longest window. The minutes ask for a shortest contiguous sum, and the non-negative word is what makes the shrink legal, so it is a shortest window. The block maximum looks like a fixed window and is a monotonic deque, because the sample that leaves may be the maximum. The [Monotonic deque: sliding window maximum](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card is that deque. The [Name the pattern](../../07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/) drill includes a longest rainfall stretch among other patterns. These four stay on the window choice.

```python
def label(prompt: str) -> str:
    return {
        "average of the last 8 closes": "fixed window",
        "longest stretch with at most 2 sensor ids": "longest window",
        "fewest non-negative minutes that reach 20": "shortest window",
        "maximum of every block of 4 samples": "monotonic deque",
    }[prompt]


print(label("average of the last 8 closes"))
print(label("longest stretch with at most 2 sensor ids"))
print(label("fewest non-negative minutes that reach 20"))
print(label("maximum of every block of 4 samples"))
# fixed window
# longest window
# shortest window
# monotonic deque
```

## A zero that is still in the dictionary

This anagram count compares two plain dicts. On the exercise text `cab` and the pattern `ab` it returns 0. The true count is 1, the block `ab`. Why does the compare miss, and what do a dict that deletes a zero key and a 26-slot array return for `cab` / `ab` and for `bcaacb` / `abc`?

```python
def broken_anagrams(text: str, pattern: str) -> int:
    need: dict[str, int] = {}
    for ch in pattern:
        need[ch] = need.get(ch, 0) + 1
    have: dict[str, int] = {}
    if not pattern or len(pattern) > len(text):
        return 0
    width = len(pattern)
    for ch in text[:width]:
        have[ch] = have.get(ch, 0) + 1
    hits = int(have == need)
    for right in range(width, len(text)):
        have[text[right]] = have.get(text[right], 0) + 1
        have[text[right - width]] -= 1
        hits += int(have == need)
    return hits
```

**Answer:** The first block of `cab` is `ca`. Sliding to `ab` decrements `c` to 0 and leaves the key in the dict, so the window dict is `{c: 0, a: 1, b: 1}` and the pattern dict is `{a: 1, b: 1}`. A plain dict compares keys, so the leftover zero misses a real anagram. Delete the key when the count hits 0. A 26-slot array keeps an explicit 0 on both sides, so the same zero does not break `==`. Both repairs return 1 for `cab` / `ab` and 1 for `wxyz` / `xyz`. `collections.Counter` would also report 1 here, because Counter equality ignores a zero count. That is a reason to know which mapping you compared, not a reason to leave the zero in a plain dict. The scan stays O(n) time and O(1) extra memory for a lowercase alphabet.

```python
def broken_anagrams(text: str, pattern: str) -> int:
    need: dict[str, int] = {}
    for ch in pattern:
        need[ch] = need.get(ch, 0) + 1
    have: dict[str, int] = {}
    if not pattern or len(pattern) > len(text):
        return 0
    width = len(pattern)
    for ch in text[:width]:
        have[ch] = have.get(ch, 0) + 1
    hits = int(have == need)
    for right in range(width, len(text)):
        have[text[right]] = have.get(text[right], 0) + 1
        have[text[right - width]] -= 1
        hits += int(have == need)
    return hits


def delete_zero(text: str, pattern: str) -> int:
    need: dict[str, int] = {}
    for ch in pattern:
        need[ch] = need.get(ch, 0) + 1
    have: dict[str, int] = {}
    if not pattern or len(pattern) > len(text):
        return 0
    width = len(pattern)
    for ch in text[:width]:
        have[ch] = have.get(ch, 0) + 1
    hits = int(have == need)
    for right in range(width, len(text)):
        have[text[right]] = have.get(text[right], 0) + 1
        outgoing = text[right - width]
        have[outgoing] -= 1
        if have[outgoing] == 0:
            del have[outgoing]
        hits += int(have == need)
    return hits


def array_anagrams(text: str, pattern: str) -> int:
    if not pattern or len(pattern) > len(text):
        return 0
    base = ord("a")
    need = [0] * 26
    have = [0] * 26
    for ch in pattern:
        need[ord(ch) - base] += 1
    for ch in text[: len(pattern)]:
        have[ord(ch) - base] += 1
    hits = int(have == need)
    for right in range(len(pattern), len(text)):
        have[ord(text[right]) - base] += 1
        have[ord(text[right - len(pattern)]) - base] -= 1
        hits += int(have == need)
    return hits


print(broken_anagrams("cab", "ab"), delete_zero("cab", "ab"), array_anagrams("cab", "ab"))
print(delete_zero("wxyz", "xyz"), array_anagrams("wxyz", "xyz"))
# 0 1 1
# 1 1
```
