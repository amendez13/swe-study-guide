## Sliding window: a range that only moves forward

A sliding window is a contiguous span of an array or a string, named by a left index and a right index, whose edges move only forward while a small piece of state stays equal to that span.

One index can visit every element. Recomputing the sum, the product, or the character counts of every span from scratch visits the same element once for every span that contains it, which is quadratic. The second index is what lets you add the value that enters on the right and drop the value that leaves on the left. The [Sliding window](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) card, the [Sliding window](../../07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/) card, and the [Sliding window](../06_Moderate_Problems/) card name that update. This topic is how to tell a fixed length from a longest span and a shortest span, what invariant the two indexes maintain, and when the shrink is not a legal discard. Two indexes that move inward on a sorted array are [Two pointers: what a second index buys](../09_Two_Pointers/). A window maximum, where the value that leaves may be the max, is a deque and is covered with the failure cases below.

You reach for a window when the statement says contiguous, subarray, or substring, and it asks for a longest span, a shortest span, a count of spans, or every span of a given length. A subsequence can skip elements, so it is a different question. The shrink is legal when growing the span only makes the condition harder and shrinking only makes it easier: a sum of non-negative numbers, a product of integers that are all at least 1, a count of distinct values, or "at most k" of something that only increases as the span grows. The words to listen for are contiguous, subarray, substring, longest, shortest, at most k, and a length that the problem already names.

The same picture shows up outside interview problems, with a different state. A 50-day simple moving average of closing prices is the mean of 50 contiguous closes, recomputed after each new close. A 7-day moving average is the same shape on a daily count. `pandas.Series.rolling` is the library call for that mean. In June 2017 Julien Desgats described Cloudflare's edge rate limiter in "How we built rate limiting capable of scaling to millions of domains." A limit of 50 requests per minute, with 18 requests in the current minute and 42 in the previous minute, 15 seconds into the current minute, is estimated as `42 * ((60 - 15) / 60) + 18 = 49.5`. The post's check of 400 million requests from 270,000 sources found 0.003% allowed or limited on the wrong side of the threshold, because the estimate assumes the previous minute was spread evenly. That is a weighted counter over a time span. The [Sliding Window](../../09_System_Design_Interview/17_Rate_Limiting_and_Throttling/) card works the same estimate with its own figures. It is not an array search. TCP is a looser cousin. RFC 9293 section 3.8.6 defines the window in a segment as the range of sequence numbers the receiver is prepared to accept, tied to buffer space. As acknowledgements arrive, the left edge of unacknowledged data advances. That is flow control. The interview pattern is the array version of a span whose edges advance and whose state is updated from what entered and what left.

Three moves cover the problems in this topic. Expand steps the right index and adds the new value. Shrink steps the left index and removes the value that left. Slide steps both, which keeps the length fixed: one value in, one value out. The invariant you should be able to say before the loop is: the state describes exactly the closed span `[left, right]`, and `left` never decreases. Each index is added once. Each index is removed at most once. An inner loop that shrinks is therefore linear across the whole scan, even though one outer step can move `left` several times. That aggregate bound is the same family of accounting as the [Amortized time](../../07_Data_Structures_and_Algorithms/01_Algorithmic_Complexity/) card, which spreads a rare expensive step across a sequence. Here the "expensive" step is a burst of shrinks, and the budget is one removal per index.

**Trade-offs.** A window is linear time and a small amount of extra memory: a sum is a constant, a 26-slot count is a constant, and a map is proportional to the number of distinct values inside the span. The quadratic scan uses no extra memory and needs no monotone condition, and it is the check you run on a tiny input. A window that shrinks on a condition that is not monotone drops a start index it may still need. Negatives do that to a sum. Zeros and negatives do that to a product. A fixed length does not have this problem, because a fixed window never discards a span for being over a budget. It reports every span of that length.

**Interview.** Say "contiguous" back to the interviewer and name the move: fixed, longest, or shortest. State the invariant, then the monotone reason that makes a shrink safe. Give the aggregate bound in one sentence: every index enters once and leaves at most once. If the values can be negative, or the question is a subsequence, or the question is the maximum inside every block, stop and name the other tool before you write the loop.

**Recap.** A sliding window keeps a sum or a count equal to a contiguous span while the two ends move only forward. Fixed, longest, and shortest are the three questions, and each one has its own rule for when the left end moves. The scan is linear because each index is added once and removed at most once. The shrink is safe only when a larger span cannot become legal again by itself.

## Fixed window: the length is part of the problem

A fixed window has a length the problem already gives you. Every span you report has that length, and the next span is the current span with one new value on the right and one old value on the left.

A 50-day average does not search for the best length. The length is 50. There are `n - k + 1` spans of length `k` in a sequence of length `n`, when `k` is between 1 and `n`. Filling the first span costs `k` additions. Each later span changes the total by one addition and one subtraction, so the rest of the scan is proportional to `n - k`. The whole pass is linear. It is a direct bound, not only an aggregate one: there is no inner loop. `pandas.Series.rolling(window).mean()` is this update. A moving-average filter in signal processing, sometimes called a boxcar, replaces each sample with the mean of a fixed neighborhood. The [Fixed window: best 3-day total](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) drill is the same slide aimed at the largest sum, on a list that includes a negative. This card is the invariant and the edges. The totals below are exercise numbers.

```python
def fixed_totals(values: list[int], k: int) -> list[int]:
    """Sums of every contiguous block of length k. Empty when k is not a real block."""
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

After the right index has reached at least `k - 1`, the running total equals the sum of `values[right - k + 1]` through `values[right]`. That is the invariant. On the exercise list, `8 + 2` is 10, then `10 - 8 + 6` is 8, then `8 - 2 + 4` is 10, then `10 - 6 + 10` is 14. Dividing each total by `k` is the average. These four totals divide by 2 with nothing left over, so the averages are 5, 4, 5, and 7. A `k` of 0 is not a block. A `k` longer than the list has no block either, including a `k` of 6 on a list of 5. An empty list has no block. A `k` of 1 is the list itself. `[7, -2, 5]` with `k` of 2 sums to 5 and then 3. The negative is legal, because a fixed window never decides to drop an index for being too large. It reports the span the length asked for.

**Trade-offs.** The slide is O(n) time and O(1) extra memory if you keep only the best total, or O(n - k + 1) memory if you store every total. Re-summing each block is O(n · k) and is the right first answer on a dozen elements. A dynamic window is the wrong shape when the length is given: there is nothing to shrink. A deque is the right shape when the question is the maximum inside each block, because subtracting the value that leaves does not tell you the new maximum when that value was the maximum.

**Interview.** Repeat `k` back, and ask what to return when `k` is larger than the input. Write the first window before the loop, then one line that adds the new value and subtracts the value `k` steps back. Name the invariant on a block you can add by hand. If the interviewer removes the fixed length and asks for the longest span under a budget, switch to the next card.

**Recap.** A fixed window visits every contiguous block of a given length by adding the value that enters and subtracting the value that leaves. The first block costs `k` additions, and every later block costs a constant amount of work, so the scan is linear. A length that is not between 1 and the input length produces no block. Negatives do not break a fixed sum.

## Longest valid window: shrink while the span is over budget

A longest-window scan grows the right end on every step, then moves the left end forward only while the span is illegal, and remembers the largest legal length it held.

This is the shape of "the longest contiguous stretch whose sum is at most a budget," when every value is non-negative. Growing the stretch cannot lower the sum, so a start index that is already over budget stays over budget if you keep it and add more. Dropping it is a discard you can defend. The [Sliding window](../06_Moderate_Problems/) card uses that rule on a watering log. The invariant after each right step is: `[left, right]` is legal, and if `left` is still positive then `[left - 1, right]` is not. Because the values are non-negative, every start to the right of `left` is a shorter suffix and is also legal. The longest legal span that ends at `right` is therefore the one that starts at `left`. The best answer is the maximum of those lengths. The hours below are exercise numbers.

```python
def longest_at_most(values: list[int], limit: int) -> int:
    """Longest contiguous sum that is <= limit. Values are non-negative."""
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

`3 + 1` is 4, still inside 5. Adding 2 makes 6, so the leading 3 leaves and the span is `[1, 2]`. Adding the next 1 makes `[1, 2, 1]`, which sums to 4 and has length 3. Adding 4 forces the left end forward until `[1, 4]`, which sums to 5. The last 1 makes `[4, 1]`. No legal span is longer than 3. An empty log has length 0. A single hour of 9 against a limit of 5 shrinks until the window is empty, so the length stays 0. A single hour that equals the limit has length 1. Two zeros against a limit of 0 have length 2, because zero is non-negative and the sum never goes over.

The right index walks forward `n` times. The left index walks forward at most `n` times in total, because it never moves backward. The body of the inner loop therefore runs at most `n` times across the whole function, which is why a loop inside a loop is still O(n) time. Extra memory is O(1). A value larger than the limit never fits, and the inner loop removes it before the length is recorded. That guard is `left <= right` together with the `total <= limit` test. Recording the length before the shrink would count an illegal span.

**Trade-offs.** The linear scan needs the monotone sum. Sorting the array destroys the contiguous order, so it answers a different question. A prefix array, on the [Prefix sums](../06_Moderate_Problems/) card, still answers a range sum in constant time after a linear build, and with negatives it is the tool this shrink is not. Checking every pair of ends is O(n²) and is the brute force you compare against.

**Interview.** Say the invariant before the code: after each new right end, the span is legal and the previous start is not. Walk one over-budget step by hand and name the index that leaves. State that each index leaves at most once. If a value can be negative, do not offer this loop.

**Recap.** For a longest legal span, grow the right end, shrink the left end while the span is illegal, and keep the largest length. Non-negative values make the shrink safe, because a start that is already over budget cannot be saved by a longer span. The nested loops are linear because the left index only moves forward. Record the length after the shrink.

## Shortest valid window: shrink while the span still qualifies

A shortest-window scan grows the right end until the span qualifies, records the length, and then keeps shrinking from the left while the span still qualifies.

The longest card shrinks while the span is illegal and records after the window is calm. The shortest card does the opposite with the record: the interesting lengths are the ones you see while the span is still legal, and you shrink in order to find a shorter one that ends at the same right index. For a sum of non-negative values that must reach a positive target, shrinking lowers the sum. The shortest legal span that ends at `right` is the last one you record before the sum falls under the target. The [Shortest window to a target](../../07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/) drill is that sum on a different list. This card is the template and the contrast with the longest scan. The readings below are exercise numbers.

```python
def shortest_at_least(values: list[int], target: int) -> int:
    """Shortest contiguous sum that is >= target. Values are non-negative and target is positive."""
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

`4 + 2` is 6, still short of 8. Adding 5 makes 11, so the length 3 is recorded, the leading 4 leaves, and 7 is under the target. `[2, 5, 1]` sums to 8, another length of 3, and shrinking again drops under. `[5, 1, 3]` sums to 9, still length 3. No pair of neighbors reaches 8: `4 + 2` is 6, `2 + 5` is 7, `5 + 1` is 6, and `1 + 3` is 4. The answer is 3. An empty list cannot reach a positive target. A single 9 reaches a target of 3. Two 1s cannot reach 10. A single value equal to the target has length 1. A non-positive target is outside this contract: the empty span sums to 0 and would otherwise win, and this function returns 0 for that input the same way it returns 0 when no non-empty span qualifies.

The aggregate bound is the same as the longest scan. The right index moves `n` times and the left index moves at most `n` times, so the time is O(n) and the extra memory is O(1). `best` starts one past the length of the input so that "no span worked" is distinct from a real length. Returning `len(values) + 1` to the caller would leak that sentinel.

**Trade-offs.** Recording the length after the shrink, which is correct for a longest span, misses the shortest span: by then the sum is already under the target and the length you would record is the first illegal one. Shrinking while illegal, the longest habit, never looks at the legal lengths that this problem is asking for. A fixed window cannot answer "shortest," because the length is the unknown.

**Interview.** Say which way the record runs: while legal for a shortest span, after the repair for a longest span. Walk the first time the sum reaches the target, including the shrink that follows the record. Ask whether the values are non-negative. Name the sentinel you used for "no span," and return 0 instead of that sentinel.

**Recap.** For a shortest legal span, grow until the span qualifies, record the length, and shrink while it still qualifies. Non-negative values make each shrink a step toward a shorter candidate that ends at the same place. The scan is linear for the same reason as the longest scan: the left index only moves forward. A missing span returns 0, not the sentinel you used inside the loop.

## Window state: a sum, a count, or a matches counter

The window's state is whatever you can update when one element enters and one element leaves. A sum is one integer. A product of positive integers is one integer. A multiset of characters is a count per character.

A sum is the fixed-window card and the two sum cards above. Character problems need counts. A lowercase English letter is one of 26 slots, so two arrays of length 26 compare in constant time and use constant memory. A dict is the same idea when the alphabet is not a fixed 26, including digits, spaces, and symbols. The [Frequency map and character counting](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) card, the [Frequency map](../../07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/) card, and the [Counting with a map](../10_Hash_Maps_and_Sets/) card are that map. The window only changes how the map is updated: one character in, and, when the length is fixed or the left end moves, one character out.

Comparing two arrays of 26 on every slide is still linear, because 26 does not grow with the string. A matches counter removes even that scan. Start it at the number of slots that already agree, which is every slot whose pattern count is 0 while the window is still empty. When a slot's window count moves onto the pattern count, or off it, adjust the counter by one. The window is an anagram when the counter equals 26. Rebuilding the counts from the whole window on every step is the slow version, O(n · m) for a pattern of length `m`. A [Rolling hash for substrings](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) fingerprints a window in constant time for an exact match. An anagram does not care about order, so the counts are the fingerprint that answers it. The strings below are exercise strings.

```python
def anagram_hits(text: str, pattern: str) -> tuple[int, int]:
    """Array compare, then a matches counter. Both count fixed windows that match pattern."""
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
print(anagram_hits("aaaa", "aa"))
print(anagram_hits("ab", "abcd"))
# (2, 2)
# (3, 3)
# (0, 0)
```

`bca`, `caa`, `aac`, and `acb` are the four windows. `bca` and `acb` match `abc`. Both counters report 2. Three windows of `aaaa` match `aa`. A pattern longer than the text matches nothing. A plain dict that leaves a count at 0 will not compare equal to a pattern dict that has no zero keys. `collections.Counter` hides that particular mistake: Counter equality ignores keys whose count is 0, which is a Python fact worth knowing before you use `==` on one. The repair for a plain dict is to delete the key when the count hits 0. Arrays do not have the problem, because both sides have an explicit 0 in every unused slot.

**Trade-offs.** A 26-slot array is the right state for a lowercase contract and uses constant memory. A dict handles the wider alphabet of the unique-character problem and uses memory proportional to the distinct characters you have seen. The matches counter and the array compare are both linear. The counter does less work per slide. A rolling hash answers "is this the same string," and a count answers "is this the same multiset."

**Interview.** Name the state before the pointers. Say why a 26-slot array is constant memory, and say when a dict is required instead. Mention the zero-key trap if you compare dicts. If you offer the matches counter, say what it counts: slots that agree, including the slots that are 0 on both sides.

**Recap.** Window state is a value you can fix up from the character that entered and the character that left. Sums and products are one number. Lowercase counts are 26 slots, and a matches counter turns the 26-slot compare into a constant-time check. A dict is the state when the alphabet is not 26 letters. Delete a dict key that falls to 0, or compare arrays, or use a Counter, which treats a zero count as absent.

## Count of Anagram Windows (LeetCode-style: Find All Anagrams in a String)

Count the contiguous blocks of `text` that use the same letters, with the same counts, as `pattern`. Order does not matter. The block length is the pattern length, so this is a fixed window.

A word-game rack is a multiset of letters. "bca" and "abc" are the same rack. The scan keeps two 26-slot counts, slides one letter in and one letter out, and adds one to the answer when the counts agree. The strings below are exercise strings, and the letters are lowercase.

```python
def count_anagram_windows(text: str, pattern: str) -> int:
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
    width = len(pattern)
    for right in range(width, len(text)):
        have[ord(text[right]) - base] += 1
        have[ord(text[right - width]) - base] -= 1
        hits += int(have == need)
    return hits


print(count_anagram_windows("bcaacb", "abc"))
print(count_anagram_windows("aaaa", "aa"))
print(count_anagram_windows("zz", "z"))
print(count_anagram_windows("ab", "abcd"), count_anagram_windows("", "a"), count_anagram_windows("abc", ""))
# 2
# 3
# 2
# 0 0 0
```

`bca` and `acb` are the two hits inside `bcaacb`. A string of four `a`s has three blocks of length 2. `zz` against `z` has two blocks. A pattern longer than the text, an empty text, and an empty pattern all return 0 under this contract. An empty pattern is a choice: every index is the start of an empty block, which would be `len(text) + 1` hits. This function does not count those. The array index `ord(ch) - ord("a")` is valid for a lowercase letter and is the wrong index for anything else.

The time is O(n). Each slide changes two slots and compares 26, and 26 is constant. The extra memory is O(1). Rebuilding a count from each block is O(n · m). LeetCode 438, Find All Anagrams in a String, returns the start indexes of those blocks, in any order, and the count here is the length of that list. Its contract is lowercase English letters and a length from 1 through 3 · 10⁴ for both strings. LeetCode 567, Permutation in String, is the boolean form: true when this count is positive, with the same lowercase letters and lengths from 1 through 10⁴. Both published problems exclude the empty strings that this function maps to 0.

**Trade-offs.** Two arrays make the zero counts explicit, so `==` is a real multiset compare. A matches counter does the same job with less work per slide and is easier to get wrong on the first try. A dict compare is fine for a small alphabet and fails if a departed letter stays stored at 0. Returning indexes instead of a count is the same scan with a list append, and the list can hold O(n) indexes.

**Interview.** Say "fixed window of the pattern length" in the first sentence. Ask whether the alphabet is lowercase. Walk one slide on a four-letter exercise string and point at the letter that leaves. Mention that an empty pattern is a contract question, and that the published problems return indexes or a boolean rather than a count.

**Recap.** An anagram block is a fixed window whose letter counts equal the pattern's counts. Slide one letter in and one letter out, and compare two 26-slot arrays. The scan is linear and the arrays are constant memory. A pattern that is empty or longer than the text returns 0 in this contract. LeetCode 438 returns the start indexes of the same windows, and LeetCode 567 returns whether any window exists.

## Longest Stretch With No Repeated Character (LeetCode-style: Longest Substring Without Repeating Characters)

Return the length of the longest contiguous piece of a string that never uses the same character twice.

A set of the characters inside the span is enough to see a repeat. When the new character is already in the set, shrink from the left until it is gone, then add the new character and measure. The set version and the index version on the next card answer the same lengths. The set makes the shrink obvious: you remove characters one by one until the repeat is gone. The strings below are exercise strings.

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


print(longest_unique("diction"))
print(longest_unique("aaaa"), longest_unique(""), longest_unique("a"), longest_unique("a b a"))
# 5
# 1 0 1 3
```

`diction` grows through `dict`. The second `i` is already in the set, so `d` and the first `i` leave, and the span is `cti`. Then `o` and `n` extend it to `ction`, length 5. Four copies of one letter have length 1. An empty string has length 0. One letter has length 1. `a b a` treats the space as a character, so `a b` has length 3, and the second `a` shrinks the span back to a piece of length 3. Measuring before the shrink would count the repeated character.

The right index moves `n` times and each character is inserted and removed at most once, so the inner loop is linear across the scan. Time is O(n). Extra memory is O(m), where `m` is the number of distinct characters in the string. A 26-slot array is the wrong alphabet for this problem. LeetCode 3, Longest Substring Without Repeating Characters, returns this length for strings of length 0 through 10⁵ whose characters are English letters, digits, symbols, and spaces. A dict or a set covers that contract. A 128-slot array covers it only if every character is in that byte range. The next card replaces the one-by-one shrink with a jump to the previous index of the repeated character.

**Trade-offs.** The set is easy to say and uses memory proportional to the distinct characters in the current span. The index jump on the next card is the same complexity and moves `left` in one assignment. Checking every pair of ends is O(n²) and is the brute force. A fixed window cannot answer this, because the length is what you are solving for.

**Interview.** Repeat that the piece has to be contiguous. A subsequence that skips letters is a different problem. Walk `diction` as far as the second `i`, and say which characters leave. Put the length update after the shrink. Mention the alphabet: letters, digits, symbols, and spaces, so a 26-slot array does not implement the published contract.

**Recap.** The longest stretch with no repeated character grows a set and shrinks from the left until the new character is unique again. Each character enters and leaves at most once, so the scan is linear and the set is proportional to the distinct characters. The length is recorded after the shrink. LeetCode 3 allows an empty string, and its alphabet is wider than 26 letters.

## Jump the left edge to one past the previous copy

The index form of the unique-character scan stores the last index of each character and moves the left edge directly to one past the previous copy, when that copy still sits inside the window.

A set shrinks one character at a time. If the repeated character's earlier copy is far to the left, those steps are real work, even though the aggregate bound keeps them linear. The last-seen map spends the same memory and skips the gap. The assignment has to be `left = max(left, previous + 1)`. The `max` is the whole bug. A previous index that is already outside the window would pull `left` backward, and the span would contain whatever you had already shrunk away. The string below is an exercise string.

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


print(buggy_jump("success"), jump_unique("success"))
print(jump_unique("diction"), jump_unique(""), jump_unique("aaaa"))
# 5 3
# 5 0 1
```

`success` is indexes `s u c c e s s`. The second `c` puts `left` on that `c`. The later `s` has an earlier copy at index 0. The buggy assignment sets `left` to 1, which is behind the left edge, and the span it measures includes both copies of `c`. Its length is 5. The repaired assignment keeps `left` at 3, because `max(3, 1)` is 3, and the best length stays 3 (`suc`, or `ces`). `diction` is still 5, an empty string is 0, and a run of one character is 1. Update the last-seen index after you have used the old one. Updating it first makes the character look like it last occurred at the current index, and the jump goes nowhere.

The invariant is the unique-character invariant plus one sentence: `left` never decreases. The map stores one index per distinct character, so the extra memory is O(m) and the time is O(n). A missing character uses `-1`, and `-1 + 1` is 0, so the first copy does not move a left edge that is already at 0.

**Trade-offs.** The jump is one assignment instead of a loop, and it is easier to move backward if you forget the `max`. The set shrink cannot move backward, because it only removes the character at the current left edge. Both are linear. The set is the version to write if you do not yet trust the index.

**Interview.** Write `max(left, last_index + 1)` and say why the `max` is there, using a string where a character reappears after the left edge has already passed its old copy. `success` is enough. Say that you read the old index before you store the new one. Offer the set if the interviewer would rather see the shrink.

**Recap.** The last index of a character lets the left edge jump to one past the previous copy. The jump has to stay at or to the right of the current left edge, or a copy you already removed comes back into the span. Store the new index after you have read the old one. The length is the same one the set shrink computes, in linear time and in memory proportional to the distinct characters.

## Longest Run You Can Make Uniform (LeetCode-style: Longest Repeating Character Replacement)

Return the length of the longest contiguous piece you can turn into one repeated character by changing at most `k` characters.

Inside one window, the cheapest target is the character that already appears most often. Every other character is a change. The window is legal when `length - (count of that character)` is at most `k`. You do not need a window that is shorter than the best one you have already found, so a window that goes one over budget slides forward by one instead of shrinking down to a much smaller span. The high-water mark below is the largest live count you have seen. It is not lowered when the left edge moves. The string is an exercise string.

```python
def longest_uniform(text: str, k: int) -> tuple[int, str]:
    """Length, and the final slice. The slice can be over budget. The length is the answer."""
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

`AAAB` with `k` of 0 is the case that makes the high-water mark visible. The span grows through `AAA`, and `high` is 3. Adding `B` would make length 4 against a mark of 3, which is over a budget of 0, so the left edge slides once. The final slice is `AAB`. That slice needs one change, so it is over budget. The length is still 3, and `AAA` is a legal slice of that length. With `k` of 1 the whole string is legal: three `A`s and one change. Four `A`s with `k` of 0 are already uniform, length 4. `ABC` with `k` of 0 has length 1. An empty string has length 0.

The mark is safe for the length, and it is not a description of the final slice. The length grows only while `length <= high + k`. The mark rises only when the character you just added has a live count equal to the new mark, so at that moment the window really holds that many copies. You slide only when the next length would pass `high + k`, and one slide puts the length back on `high + k`. Adding one character raises the number of changes by at most 1 when the mark does not rise, which is why a single slide restores the test that uses the mark. After a slide, the character that set the mark may have left, and the current slice can be over budget. Its length is one you already achieved when the mark was still a live count. Later illegal slices do not push the length higher. Recomputing the true maximum on every step is also correct. For 26 letters that scan is still linear, because the alphabet is constant. Do that recompute when you have to return a slice that is inside the budget. The final slice of the mark version is the wrong thing to return.

The time is O(n). A dict uses O(m) extra memory for `m` distinct characters. A 26-slot array is O(1) extra memory under an uppercase contract. LeetCode 424, Longest Repeating Character Replacement, returns this length. The string is uppercase English letters, the length is from 1 through 10⁵, and `k` is from 0 through the length. You may change a character to any other uppercase letter, and you may use fewer than `k` changes. This function also accepts an empty string, a `k` past the length, and characters outside that alphabet. A `k` past the length is outside the published contract, and the length of the string is the answer, because you can change every character.

**Trade-offs.** Keeping the high-water mark avoids a 26-slot scan and makes the final slice untrustworthy. Recomputing the maximum keeps a legal slice and spends a constant 26 per step on the published alphabet. Both are linear. A shrink that runs until the true window is legal is the right loop when you need the slice. The slide is enough when you need only the length.

**Interview.** Say the budget test in words: length minus the most common character, at most `k`. Then say why you do not lower the mark, and give `AAAB` with `k` of 0 as the case where the final slice is `AAB` and the length 3 belongs to `AAA`. If the interviewer asks for the slice, recompute the true maximum and remember a legal span. Mention that `k` of 0 is the longest run of one character.

**Recap.** A window can be made into one character with at most `k` changes when its length minus its most common character is at most `k`. For the longest such window, a high-water mark of that count is enough, and the left edge slides by one when the length would pass the mark plus `k`. The final slice can be over budget. The length is the answer. LeetCode 424 is this length on uppercase letters, with `k` from 0 through the length.

## When a sliding window is the wrong tool

A shrink is a legal discard only when a larger span cannot become legal again. A sum that may contain negatives does not have that property. A product that may contain zeros or negatives does not either.

Take a longest span whose sum must be at most 4, on the exercise list `[3, 3, -2]`. The shrink that assumes non-negative values adds 3, adds 3, sees 6, and drops the first 3. Then `-2` arrives and the span `[3, -2]` sums to 1, length 2. The whole list sums to 4, which is inside the budget, and the length is 3. The `-2` would have repaired the span the algorithm had already thrown away, and the left index cannot move back. A prefix array makes that range sum obvious: `[0, 3, 6, 4]`, and `4 - 0` is 4. The [Prefix sums](../06_Moderate_Problems/) card is that array. Checking every pair of ends is the correct brute force once negatives are allowed. A fixed window still adds negatives without trouble, because it never discards a start. The 3-day drill is that case. The block of length 2 on `[7, -2, 5]` sums to 5 and then 3.

A product of integers that are all at least 1 does not fall as the window grows, so the same shrink works, and every subarray inside a legal window is legal. A zero breaks that. On `[2, 0, 5]` with a strict ceiling of 4, the window product becomes 0 and stays under the ceiling while `left` never moves, so the scan counts 6 subarrays. The subarray `[5]` is 5, which is not under 4. The true count is 5. A negative factor can make a longer product smaller, which is the same failure as a negative in a sum.

Two more questions wear the word "window" and use a different tool. The maximum inside every block of length `k` is not a running total. When the maximum slides out, the next maximum is some earlier value you would otherwise have forgotten. The [Monotonic deque: sliding window maximum](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card keeps those candidates in a deque. A subsequence that may skip elements is not a contiguous span, so moving a left index does not describe it.

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
print([7 + -2, -2 + 5])
# 2 3
# 6 5
# [5, 3]
```

**Trade-offs.** The linear shrink is worth it when the condition is monotone, and it is a wrong answer when it is not. Prefix sums handle range sums, including negatives, and a single range is a subtraction. Many ranges that must each be the longest under a budget, once negatives are allowed, are not one subtraction. The O(n²) check remains the honest reference. A deque answers window maxima in linear time. A heap answers them in O(n log k) and is easier to describe.

**Interview.** State the monotone reason before you offer a window. If you cannot say it, show a three-element counterexample rather than patching the shrink. Split "fixed length" from "dynamic budget" out loud. A fixed sum may include negatives. A dynamic sum under a budget may not, unless you change tools. Point window maxima at the deque card.

**Recap.** A dynamic sum window needs non-negative values, and a dynamic product window needs values that are at least 1. `[3, 3, -2]` with a limit of 4 is a sum the shrink gets wrong, 2 against a true 3. `[2, 0, 5]` with a product ceiling of 4 is a count the shrink gets wrong, 6 against a true 5. Fixed-length sums still allow negatives. The maximum of each block is a deque.

## A window, two pointers, or prefix sums

The first sentence of the problem picks the tool. A contiguous span with a length or a monotone budget is a window. A pair, a compaction, or a symmetric scan is two pointers. A range sum, especially once negatives appear, is a prefix array.

Listen for the constraint, then the shape. "Every block of length k" or "the average of the last k readings" is the fixed window. "Longest contiguous stretch with at most two distinct values" or "at most k changes" is the longest window. "Shortest contiguous stretch that reaches a quota," with non-negative values, is the shortest window. "How many contiguous products stay under a ceiling," with values at least 1, is the same dynamic window, and the count adds `right - left + 1` because every subarray inside the legal window is legal. "Two values that add to a target" on a sorted array is the [Two pointers](../06_Moderate_Problems/) card and [Two pointers: what a second index buys](../09_Two_Pointers/). "The sum from here to there," or a sum budget that must survive negatives, is the [Prefix sums](../06_Moderate_Problems/) card. "The maximum inside each block" is the [Monotonic deque: sliding window maximum](../../07_Data_Structures_and_Algorithms/04_Stacks_and_Queues/) card.

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

The tank readings have a length in the sentence, so the window is fixed. The status codes ask for a longest contiguous stretch under a distinct-count budget, so the window grows and shrinks. The days ask for a shortest contiguous sum, and the non-negative word is what makes the shrink legal. The block maximum looks like a fixed window and is a deque, because the leaving value may be the one the total would have needed to remember.

**Trade-offs.** A window is linear when the monotone reason is real, and it is confidently wrong when that reason is missing. Two pointers need order or symmetry, and they do not keep a multiset of a span. Prefix sums answer ranges after one linear build, and they do not by themselves give you the shortest span under a budget. The deque is linear for window maxima. The nested loop is the reference that tells you the fast answer is wrong.

**Interview.** Start from the noun in the constraint: length, longest, shortest, count, pair, range sum, or block maximum. Say the monotone reason in the same breath as the window, or say why you are not using one. Give both costs, time and extra memory. Offer the quadratic check as the thing you would run on a list of four elements.

**Recap.** A named length is a fixed window. A longest or shortest contiguous budget, when growing the span only makes the condition harder, is a dynamic window. A sorted pair is two pointers. A range sum, and any sum budget that allows negatives, is a prefix array. The maximum of each block is a deque. The quadratic scan is the check on a tiny input.
