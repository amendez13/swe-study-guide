# Sliding Windows

A sliding window is a contiguous span whose ends move only forward. A named length is a fixed block: add the value that enters and drop the value that leaves. A longest span shrinks while the span is illegal and records the length after the repair. A shortest span records the length while the span still qualifies and then shrinks. The shrink is a legal discard only when a larger span cannot become legal again. These notes are the moves, the state, and the check. They are not a catalog of published problems.

## Key Points

- **Sliding window: a range that only moves forward** — two indexes and a state that matches the span between them. Expand, shrink, or slide. Each index enters once and leaves at most once. A 50-day average, Cloudflare's weighted minute counter, and TCP's receive window are neighboring pictures. The interview shrink needs a monotone condition.
- **Fixed window: the length is part of the problem** — fill the first block, then add the new value and subtract the value `k` steps back. A length outside 1 through n produces no block. Negatives still add. The scan is linear with no inner loop.
- **Longest valid window: shrink while the span is over budget** — after each right end, the span is legal and the previous start is not, for a non-negative sum. Record the length after the shrink. The inner loop is linear across the whole scan.
- **Shortest valid window: shrink while the span still qualifies** — record the length while the sum still reaches a positive target, then shrink. A non-positive target is outside the contract. Return 0 when no span qualifies, not the sentinel inside the loop.
- **Window state: a sum, a count, or a matches counter** — one integer for a sum, 26 slots for lowercase letters, a dict when the alphabet is wider. A matches counter counts slots that agree. Delete a dict key that falls to 0. Counter equality ignores a zero count.
- **Count of Anagram Windows (LeetCode-style: Find All Anagrams in a String)** — a fixed window whose counts equal the pattern. Linear time, constant memory for 26 letters. An empty pattern or a pattern longer than the text returns 0 here. LeetCode 438 returns start indexes. LeetCode 567 returns a boolean.
- **Longest Stretch With No Repeated Character (LeetCode-style: Longest Substring Without Repeating Characters)** — a set shrinks until the new character is unique, then the length is recorded. Linear time, memory proportional to the distinct characters. LeetCode 3 allows an empty string and an alphabet wider than 26 letters.
- **Jump the left edge to one past the previous copy** — `left = max(left, previous + 1)`, and the old index is read before the new one is stored. Without the `max`, `success` reports 5 and the true length is 3.
- **Longest Run You Can Make Uniform (LeetCode-style: Longest Repeating Character Replacement)** — length minus the most common character, at most `k`. A high-water mark slides the window by one and can leave the final slice over budget. `AAAB` with `k` of 0 ends on `AAB` and the length 3 belongs to `AAA`. LeetCode 424 is uppercase letters, with `k` from 0 through the length.
- **When a sliding window is the wrong tool** — `[3, 3, -2]` with a limit of 4 is 2 by the shrink and 3 by checking every span. `[2, 0, 5]` with a product ceiling of 4 is 6 by the shrink and 5 by checking every product. Fixed sums still allow negatives. Block maxima are a deque.
- **A window, two pointers, or prefix sums** — a named length, a longest or shortest monotone span, a sorted pair, a range sum, or a block maximum. Say the monotone reason in the same breath as the window.

## Example

```python
def count_anagram_windows(text: str, pattern: str) -> int:
    if not pattern or len(pattern) > len(text):
        return 0
    base = ord("a")
    need = [0] * 26
    have = [0] * 26
    for ch in pattern:
        need[ord(ch) - base] += 1
    width = len(pattern)
    for ch in text[:width]:
        have[ord(ch) - base] += 1
    hits = int(have == need)
    for right in range(width, len(text)):
        have[ord(text[right]) - base] += 1
        have[ord(text[right - width]) - base] -= 1
        hits += int(have == need)
    return hits


def jump_unique(text: str) -> int:
    last: dict[str, int] = {}
    left = 0
    best = 0
    for right, ch in enumerate(text):
        left = max(left, last.get(ch, -1) + 1)
        last[ch] = right
        best = max(best, right - left + 1)
    return best


def longest_uniform(text: str, k: int) -> int:
    if k < 0 or not text:
        return 0
    counts: dict[str, int] = {}
    left = 0
    high = 0
    for right, ch in enumerate(text):
        counts[ch] = counts.get(ch, 0) + 1
        high = max(high, counts[ch])
        if (right - left + 1) - high > k:
            counts[text[left]] -= 1
            left += 1
    return len(text) - left


print(count_anagram_windows("bcaacb", "abc"), count_anagram_windows("ab", "abcd"))
print(jump_unique("diction"), jump_unique("success"), jump_unique(""))
print(longest_uniform("AAAB", 0), longest_uniform("AAAB", 1), longest_uniform("ABC", 0))
# 2 0
# 5 3 0
# 3 4 1
```

The anagram count is a fixed window of letter counts. The unique-character length jumps the left edge and never moves it backward. The uniform length uses a high-water mark, so `AAAB` with no changes allowed still reports 3. The strings are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the move, the cost, and a Python check. None of them is a published problem from a book list.
