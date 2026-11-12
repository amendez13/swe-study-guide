## Two pointers: what a second index buys

A pointer here is an index into a sequence. Two pointers are two indexes that move under a rule, so each comparison can throw away many pairs instead of one.

One index can visit every element. It cannot, by itself, compare two ends or keep a read position and a write position apart. The second index is what makes that comparison possible. POSIX `comm` already uses the idea on text: it compares two files that should be ordered in the current collating sequence, and it walks those files together. PostgreSQL can plan a merge join on inputs ordered by the join key, and it sorts a side first when that order is missing. The order is what tells the scan which side may advance.

On one array the same idea shows up in three shapes. Inward traversal puts an index at each end and moves the end that cannot contain the answer. Same-direction traversal uses a fast reader and a slower writer, so the writer marks the next slot that is allowed to keep a value. Staged traversal uses the first scan only to find a break in the structure, then a second scan does the work from that break. The [Two-pointer technique](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) card and the [Two pointers](../../07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/) card name the pattern. The [Two pointers](../06_Moderate_Problems/) card in Moderate Problems is the kayak-packing version of the inward scan. This topic is how to recognize each move and how to apply it.

You reach for it when the data is linear and either already ordered, symmetric, or being compacted in place, or when the answer is a pair (or a pair plus one fixed value). A nested loop is the honest first answer: compare every pair, which is proportional to the square of the length. Two pointers replace that nest only when a move has a proof that the skipped pairs are useless. Floyd's cycle scan, on the [Cycle detection with Floyd's algorithm](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) card, and the [Sliding window](../06_Moderate_Problems/) card are also two indexes, with different rules. They are separate patterns.

**Trade-offs.** Two indexes use a constant amount of extra memory and one pass, once the order or the symmetry is real. Sorting first, so that the discard becomes legal, costs the sort. A hash map answers an unsorted pair question in one pass and keeps the original indexes, and it spends memory proportional to the input. The nested loop spends no extra memory and needs no order, and it does not scale. On a pair search, moving both indexes after one comparison can drop a pair the rule has not rejected.

**Interview.** Say "index" before you say "pointer," so nobody thinks you mean a C address. Name which shape you are using, inward, reader and writer, or staged, and say the sentence that makes a move safe. If the input is not sorted and the problem does not give you symmetry, say so and switch to the [Unsorted pair-sum with a hash set](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) card or to a sort you account for. Mention that a sliding window and a fast/slow cycle check are neighboring patterns, then stay on the one this problem is.

**Recap.** A second index lets one pass compare two positions and discard everything that position can no longer be part of. The move is safe only when the input is sorted, symmetric, or being written in a single direction. Inward, reader and writer, and staged are the three shapes. A hash map, a sort, and a nested loop are the alternatives, and each one wins on a different constraint.

## Inward traversal

Inward traversal starts one index at the left end and one at the right end, and each step moves exactly one of them toward the middle.

It is the right shape when the sequence is sorted, or when it is symmetric, so the ends mean something. A sorted price list is the everyday case. You want two different prices that add to a budget. Look at the cheapest remaining item and the most expensive remaining item. If they add to more than the budget, the expensive item cannot be saved by a different partner: every other remaining partner costs at least as much as the cheap end, so the sum stays over the budget. Drop the expensive item. If they add to less than the budget, the cheap item cannot be saved either: every other remaining partner costs no more than the expensive end, so the sum stays under the budget. Drop the cheap item. Each step deletes every pair that used the rejected end. That is why the scan is linear after the array is sorted.

The loop invariant is the sentence you should be able to say out loud: every pair that used an index outside the current `[left, right]` window has already been rejected, and any pair still inside is still possible. The condition is `left < right`, so a value is never paired with itself. When the two indexes meet, the window is empty.

```python
def inward_hit(values: list[int], target: int) -> list[tuple[int, int, int]]:
    """Exercise numbers. Record each end pair the scan actually adds."""
    left, right = 0, len(values) - 1
    seen: list[tuple[int, int, int]] = []
    while left < right:
        total = values[left] + values[right]
        seen.append((left, right, total))
        if total == target:
            break
        if total < target:
            left += 1
        else:
            right -= 1
    return seen


print(inward_hit([1, 4, 8, 11, 15], 19))
# [(0, 4, 16), (1, 4, 19)]
```

On this exercise list, `1 + 15` is 16, which is short of 19, so index 0 is finished: 15 is the largest legal partner, and a smaller partner would be even shorter. The next comparison is `4 + 15`, which hits. The pairs `(0, 1)`, `(0, 2)`, and `(0, 3)` were never added. They are safe to skip because each of them replaces 15 with something smaller.

The [Sort, then scan](../06_Moderate_Problems/) card is the neighboring tool when the question is about neighbors after sorting rather than about two ends. Sorting is what makes the discard legal. If you sort a copy, the indexes you return are indexes into the copy, not into the caller's original order.

**Trade-offs.** The scan itself is O(n) time and O(1) extra memory. If the array is not sorted yet, the sort dominates: O(n log n) time, and `sorted` builds a second list, so the extra memory grows with the input. A hash map is the better pair search when the array is unsorted and you need the original indexes. Inward traversal is the better pair search when the array is already sorted and extra memory is tight.

**Interview.** Write `left < right` before the body. Then say which comparison moves which index, and name one pair the move deletes. Equal sums are a hit; do not move both indexes unless the problem asked for every pair and you have a duplicate rule. If the interviewer removes the sorted guarantee, stop and change the algorithm.

**Recap.** Inward traversal keeps a window on a sorted or symmetric sequence and shrinks it from the end that cannot hold the answer. Because the ends are the extreme values, one comparison deletes every pair that used the rejected index. The loop stops when the indexes meet, and it never uses one index as both members of a pair.

## Reader and writer on one pass

A reader and a writer are two indexes that move in the same direction. The reader scans every slot. The writer marks the next slot that is allowed to keep a value.

This is how you compact a sequence in place. C++ `std::remove` does it for a value you want to drop: it shifts the elements you are keeping toward the front, preserves their relative order, and returns the new logical end. The container's size does not change until you erase from that end to the physical end, which is the erase-remove idiom. The writer is the slow index. Everything before it is final. The reader is the fast index. It is allowed to see values the writer has not dealt with yet, and it must not move backward. The [In-place array manipulation](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) card shows the same split on a sorted duplicate-removal.

The template keeps values that pass a test, then drops the stale tail. The numbers below are exercise numbers.

```python
def keep_at_least(values: list[int], floor: int) -> list[int]:
    write = 0
    for value in values:
        if value >= floor:
            values[write] = value
            write += 1
    del values[write:]
    return values


print(keep_at_least([1, 4, 2, 8, 3], 3))
# [4, 8, 3]
```

`4`, `8`, and `3` stay in the order the reader met them. `1` and `2` never get a write. Deleting the tail makes the list's length match the number of kept values. If you return the length and leave the tail in place, the caller has to ignore it; the write-pointer drill on the arrays topic is that leftover.

A second same-direction shape walks two already sorted sequences and advances the side whose current value is smaller. That is the merge `comm` and a PostgreSQL merge join are doing, and it is the [Merging two sorted lists](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) card for nodes. When the destination is the first array and it has spare slots at the end, both indexes start at the back so a write cannot cover a value that has not been read. That variant is a drill on this topic.

**Trade-offs.** The compaction is O(n) time and O(1) extra memory, and it keeps the order of the values you retain. Building a second list is easier to read and uses memory proportional to the output. Swapping from both ends, the inward habit, is the wrong tool when order matters: the right end is not "the next kept value," it is just the other end. A writer that runs ahead of the reader will copy a value that has already been overwritten.

**Interview.** Say the invariant before the loop: every slot before `write` is final, and `read` has seen everything before it. Name what you do with the tail. If the problem says "in place," a new list fails that constraint even when the values are right. If the problem also says "keep the original order," say why an inward swap breaks it.

**Recap.** The reader walks the whole sequence once. The writer lags behind and records only the values that stay, so the prefix before the writer is the finished result. The pass is linear and uses a constant amount of extra memory. Order is preserved because kept values are written in the order the reader sees them.

## Staged traversal

Staged traversal splits the job into a find and an act. The first scan locates the index where the structure breaks. The second scan does the work from there, using whatever the first scan proved about the rest of the sequence.

You can hear it in the problem statement. The interesting position is defined by a neighbor relationship, often read from the right, and the work after that position is a different operation: a swap, a reverse, a copy. One loop that tries to find and rewrite at the same time tends to destroy the evidence the second step needed. `std::next_permutation` states the contract for the letter-rearrangement problem later in this topic: rearrange into the next permutation in lexicographic order, and if the sequence is already the last one, rearrange it into the first. The library specifies that result. A linear way to produce it is staged. The first scan finds the rightmost place where a value is strictly smaller than its right neighbor. That proof is "the suffix after this place is non-increasing." The second scan is allowed to trust that, so it can find a successor from the right end and then reverse the suffix instead of sorting it.

The numbers in `"1322"` are exercise characters, not a measurement. The pivot is index 0 (the value `1`, because `3`, `2`, `2` is already non-increasing). The successor is index 3, the rightmost value strictly larger than `1`.

```python
def pivot_and_successor(chars: list[str]) -> tuple[int | None, int | None]:
    pivot = len(chars) - 2
    while pivot >= 0 and chars[pivot] >= chars[pivot + 1]:
        pivot -= 1
    if pivot < 0:
        return None, None
    successor = len(chars) - 1
    while chars[successor] <= chars[pivot]:
        successor -= 1
    return pivot, successor


print(pivot_and_successor(list("1322")), pivot_and_successor(list("cba")))
# (0, 3) (None, None)
```

`"cba"` has no ascent, so there is no pivot. The whole string is the non-increasing suffix, and the act stage is "reverse everything," which produces the first arrangement. The full swap-and-reverse is the next-sequence card. This card is only the split between the two scans.

**Trade-offs.** Two short linear scans are still O(n), and they keep the invariant visible. Folding both jobs into one loop saves no asymptotic time and makes the proof harder to say. Sorting the suffix instead of reversing it is correct and costs O(n log n) on that piece. Reversing is legal only because the first scan proved the suffix was non-increasing, and the successor swap preserves that.

**Interview.** Tell the interviewer you are about to walk the sequence from the right, and say what you will know when that walk stops. Then write the second scan. If the first scan finds nothing, say the fallback out loud before you code it. A staged problem is usually lost in the first minute by people who start swapping before they have named the pivot.

**Recap.** The first pass only finds the break. The second pass acts on that index and is allowed to use what the first pass proved about the suffix. Next permutation is the shape: find the rightmost ascent, then swap and reverse. A sequence with no ascent reverses as a whole, back to the first arrangement.

## Pair Sum in a Sorted Array (LeetCode-style: Two Sum II)

Given integers that are already sorted from low to high, and a target, return the indexes of any two different positions that add up to the target. If no pair exists, return an empty result. A value may not be paired with itself.

This is inward traversal with the price-list rule. The array is sorted, so the left end is the smallest remaining value and the right end is the largest. A sum that is too small can only be raised by moving the left index. A sum that is too large can only be lowered by moving the right index. The list below is exercise numbers.

```python
def pair_sum_sorted(values: list[int], target: int) -> tuple[int, int] | tuple[()]:
    left, right = 0, len(values) - 1
    while left < right:
        total = values[left] + values[right]
        if total == target:
            return (left, right)
        if total < target:
            left += 1
        else:
            right -= 1
    return ()


print(pair_sum_sorted([1, 3, 4, 7, 9, 12], 11))
print(pair_sum_sorted([1, 3, 4, 7, 9, 12], 2))
print(pair_sum_sorted([1, 4, 4, 9], 8))
print(pair_sum_sorted([4], 8))
# (2, 3)
# ()
# (1, 2)
# ()
```

`4 + 7` is the hit, at indexes 2 and 3. Target 2 never hits, because the smallest sum in that list is `1 + 3`. `[4, 4]` may contribute both indexes to a target of 8: they are different positions, even though the values match. A one-element list cannot, because `left < right` fails immediately. The same guard answers a target of `10` on `[5, 5]` with `(0, 1)`, and it refuses `[5]` with a target of `10`.

The scan is O(n) time and O(1) extra memory. The sort is not part of the bill, because the problem handed you a sorted array. A hash map still works and still takes one pass, and it spends extra memory proportional to the length, which throws away the only hint the statement gave you.

**Trade-offs.** Two pointers use the sorted order and a constant amount of memory. A hash map uses more memory and does not need the order, so it is the tool on the unsorted card, not this one. A double loop is fine for a dozen elements and is the thing you name before you optimize. Returning indexes into a freshly sorted copy is a different problem: those indexes are not the caller's indexes.

**Interview.** Repeat the sorted guarantee back, and ask whether any one pair is enough. State `left < right` as the guard against using one index twice. Walk `1 + 12`, then the move, on a list you can add in your head, before you write the loop. If the interviewer says the array might be unsorted, switch to the hash map and say the memory cost.

**Recap.** On a sorted array, the pair search moves the left index when the sum is short and the right index when the sum is too high. Each move drops every pair that used the rejected end. The result is one index pair or an empty result, in linear time and constant extra memory. The same index is never used twice.

## Zero-Sum Triplets (LeetCode-style: 3Sum)

Return every unique triplet of values that adds to zero. The same value may appear more than once in the input. Report each triplet of values once, even if several index combinations would produce it.

Sort, then the problem is the pair search repeated. After the sort, pick a fixed value at index `i`. The other two values have to sum to the negation of that fixed value, and they have to sit strictly to its right, so the same position is not reused. That inner search is the inward scan from the pair-sum card. Duplicates are adjacent after the sort, which is the fact the skip rules use. Skip a fixed value that equals the one before it. After a hit, move both inner indexes, and keep moving either of them while it sits on a copy of the value you just used. The input below is exercise numbers.

```python
def zero_sum_triplets(values: list[int]) -> list[tuple[int, int, int]]:
    ordered = sorted(values)
    found: list[tuple[int, int, int]] = []
    for i in range(len(ordered)):
        if ordered[i] > 0:
            break
        if i > 0 and ordered[i] == ordered[i - 1]:
            continue
        left, right = i + 1, len(ordered) - 1
        while left < right:
            total = ordered[i] + ordered[left] + ordered[right]
            if total == 0:
                found.append((ordered[i], ordered[left], ordered[right]))
                left += 1
                right -= 1
                while left < right and ordered[left] == ordered[left - 1]:
                    left += 1
                while left < right and ordered[right] == ordered[right + 1]:
                    right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    return found


print(zero_sum_triplets([-4, -1, -1, 0, 1, 2, 2]))
print(zero_sum_triplets([0, 0, 0]))
print(zero_sum_triplets([1, 2, 3]))
# [(-4, 2, 2), (-1, -1, 2), (-1, 0, 1)]
# [(0, 0, 0)]
# []
```

Once the fixed value is greater than zero, stop. The array is sorted, so everything to its right is at least that large, and three positive numbers cannot add to zero. Do not stop on zero itself: `[0, 0, 0]` is a real triplet. `[1, 2, 3]` stops on the first value.

The inner scan is linear and it runs once per index, so the time is O(n^2). `sorted` allocates a new list, so the extra memory is O(n) before you count the output. The output itself can grow with the square of the input when many distinct triplets hit zero. A set of tuples would also remove duplicates, and it hides a hash cost plus storage for every accepted triplet. The adjacent skips do the same filtering while the scan is already walking the sorted list.

**Trade-offs.** The sort-plus-inward approach makes the duplicate rule local: you compare a value with its neighbor. A hash-based three-sum exists and is easier to get wrong around duplicates and around reusing one index. The double loop over pairs, with the third value looked up in a set, is the same complexity class and spends more memory. For a nonzero target the early stop at "fixed value > 0" is false; that stop is special to a target of zero.

**Interview.** Say "sort, then two-sum for the complement" before you write code. Call out three skips: the repeated fixed value, and both inner neighbors after a hit. Say you move both inner indexes on a hit. Mention the early stop, and say it depends on the target being zero. Give the time as quadratic and the extra memory as the sort, with the output excluded.

**Recap.** Sorting turns three-sum into a linear pair search for each fixed value, which is quadratic overall. Adjacent duplicates are skipped at the fixed index and on both inner indexes after a hit, so each value triplet is emitted once. A positive fixed value ends the search when the target is zero. The sort, not the pointer scan, is the extra memory.

## Palindrome Check That Skips Punctuation (LeetCode-style: Valid Palindrome)

Decide whether a string reads the same forward and backward after you ignore characters that are not ASCII letters or digits, and after you treat uppercase and lowercase as the same letter.

The string is symmetric around its middle, so the indexes start at the two ends. A letter or digit is compared, case-folded, with the letter or digit at the other end. Anything else is skipped by the end that is sitting on it. Building a cleaned copy is correct and spends memory proportional to the length. Skipping inside the loop keeps the extra memory constant. The phrases below are exercise strings.

```python
def is_ascii_alnum(ch: str) -> bool:
    return ("0" <= ch <= "9") or ("A" <= ch <= "Z") or ("a" <= ch <= "z")


def is_palindrome(text: str) -> bool:
    left, right = 0, len(text) - 1
    while left < right:
        while left < right and not is_ascii_alnum(text[left]):
            left += 1
        while left < right and not is_ascii_alnum(text[right]):
            right -= 1
        if left < right and text[left].lower() != text[right].lower():
            return False
        left += 1
        right -= 1
    return True


def unicode_palindrome(text: str) -> bool:
    left, right = 0, len(text) - 1
    while left < right:
        while left < right and not text[left].isalnum():
            left += 1
        while left < right and not text[right].isalnum():
            right -= 1
        if left < right and text[left].lower() != text[right].lower():
            return False
        left += 1
        right -= 1
    return True


print(is_palindrome("7, level, 7"), is_palindrome("ab!"), is_palindrome("!!!"), is_palindrome(""))
print(is_palindrome("A b, a"), is_palindrome("éa"), unicode_palindrome("éa"))
# True False True True
# True True False
```

`"7, level, 7"` compares `7` with `7`, `l` with `l`, `e` with `e`, and `v` with itself. `"ab!"` compares `a` with `b` and rejects. `"!!!"` and the empty string never find a mismatch, so they count as palindromes: there is no pair of kept characters that disagrees. The inner skips also test `left < right`. Without that test, a string of punctuation walks `left` off the end and raises `IndexError`.

Python's `str.isalnum` is a different predicate. It is true for Unicode letters such as `"é"`. On the exercise string `"éa"`, the ASCII test ignores `é` and sees a single `a`, which is a palindrome. The Unicode test keeps both characters, and `"é"` does not equal `"a"`. Ask which alphabet you are supposed to keep before you call `isalnum`. Also ask about case. This card folds with `str.lower`. A problem that treats `"A"` and `"a"` as different is a one-line change, and it is a change you want to confirm.

**Trade-offs.** The inward skip is O(n) time and O(1) extra memory. A cleaned string is easier to explain and uses O(n) extra memory. Filtering to ASCII avoids a surprise on accented letters and rejects letters an international name would want kept. Comparing before case-folding fails `"A b, a"`, which is a palindrome under the rule this card stated.

**Interview.** Ask three questions: what is ignored, whether case matters, and whether the empty string and an all-punctuation string should pass. Then write both inner loops with the same `left < right` bound as the outer loop. Say that you are not deleting a mismatched letter; a problem that allows one deletion is a different state machine. Walk a string that starts with punctuation so the skip is visible.

**Recap.** Two ends walk toward the middle, passing over characters the predicate rejects, and compare the characters it keeps after case-folding. The check is linear and uses constant extra memory. The inner loops have to stop when the indexes meet. The empty string and a string with nothing to keep are palindromes under this rule.

## Largest Container (LeetCode-style: Container With Most Water)

You are given the heights of vertical lines, one per index, standing on a shared baseline. Pick two lines. The container they form has width equal to the distance between their indexes and height equal to the shorter line. Return the largest area. The heights below are exercise numbers, not a surveyed dock.

The area is `width * min(left height, right height)`. The shorter line is the limit. Every container that still uses that shorter line and a closer partner has a smaller width, and its height cannot exceed the shorter line, so its area cannot beat the area you just measured. Move the shorter side. When the heights are equal, each of them is a limiting side, so moving either one is safe. The code below moves the left side in that tie.

```python
def largest_container(heights: list[int]) -> int:
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        width = right - left
        if heights[left] <= heights[right]:
            best = max(best, width * heights[left])
            left += 1
        else:
            best = max(best, width * heights[right])
            right -= 1
    return best


print(largest_container([2, 7, 4, 3, 8]), largest_container([1, 1]), largest_container([5]))
# 21 1 0
```

On `[2, 7, 4, 3, 8]`, the ends are height 2 and height 8, four units apart, area 8. The left line is shorter, so it moves. The next pair is 7 and 8, three apart, area 21. Every later pair is smaller. A brute-force check of the same list also returns 21. Two lines of height 1, one unit apart, hold area 1. One line cannot form a container, so the result is 0.

Moving the taller side is the usual bug. That taller side might be the short side of a wider pair you have not finished with. Trapping rain water is a different quantity: it asks how much water sits above every position, given taller lines somewhere on both sides, not the single rectangle between the two chosen lines.

**Trade-offs.** The inward scan is O(n) time and O(1) extra memory. Checking every pair is O(n^2) and also correct, and it is the right check on a short list while you are still unsure which side to move. There is no hash-map version worth reaching for, because the constraint is geometric, not a complement. Sorting the heights would destroy the widths, which are index distances.

**Interview.** Define the area as width times the shorter height before any code. Say why the shorter side is the one that moves, and say the equal-height tie in the same breath. Give the one-line and empty inputs as 0. Separate this problem from trapping rain water if the interviewer says "water" without drawing the rectangle.

**Recap.** The best container is an inward scan that always abandons the shorter line, because that line cannot do better with a narrower partner. Equal heights can move either side. The scan is linear and uses constant extra memory. The answer is one rectangle, not the sum of water trapped above every index.

## Shift Zeros to the End (LeetCode-style: Move Zeroes)

Move every zero to the end of the list without allocating a second list. Keep the relative order of the nonzero values.

This is the reader and the writer. The reader walks the list. Each nonzero is swapped into the writer slot, and the writer then advances. Everything before the writer is a nonzero in its final position. Zeros drift toward the end because the swap parks them in the slot the reader just left. The list below is exercise numbers.

```python
def shift_zeros(values: list[int]) -> list[int]:
    write = 0
    for read, value in enumerate(values):
        if value != 0:
            values[write], values[read] = values[read], values[write]
            write += 1
    return values


def push_zeros_from_the_ends(values: list[int]) -> list[int]:
    left, right = 0, len(values) - 1
    while left < right:
        if values[left] == 0:
            values[left], values[right] = values[right], values[left]
            right -= 1
        else:
            left += 1
    return values


print(shift_zeros([4, 0, 0, 2, 0, 5]))
print(push_zeros_from_the_ends([4, 0, 0, 2, 0, 5]))
# [4, 2, 5, 0, 0, 0]
# [4, 5, 2, 0, 0, 0]
```

The reader/writer result keeps `4`, `2`, `5` in that order. The inward swap also ends with the zeros at the end, and it puts `5` before `2`. That is a legal compaction only if the problem does not care about order. This problem does. A new list with the nonzeros followed by the right number of zeros is easier, and it is not in place.

The pass is O(n) time and O(1) extra memory. A list that is all zeros, or that contains no zeros, is unchanged. Swapping an element with itself, when the reader and the writer sit on the same nonzero, is a no-op in Python, so a leading nonzero is safe.

**Trade-offs.** The in-place swap keeps order and uses constant extra memory. A second list keeps order and uses memory proportional to the length, which fails an in-place constraint. An inward swap uses constant memory and scrambles the nonzeros. Overwriting the tail with zeros in a second loop, instead of swapping, also keeps order; the swap version does that work inside the same pass because the displaced zero stays behind the writer.

**Interview.** Repeat "in place" and "keep the order of the other values." Name the writer invariant. Show one input where an end-swap changes that order, so the interviewer can see you chose the same-direction scan on purpose. State the all-zeros input.

**Recap.** A reader scans every slot and a writer receives the nonzeros in the order they appear. Zeros end up behind the writer. The pass is linear and uses constant extra memory. Swapping from the two ends also gathers the zeros, and it does not keep the other values in order.

## Next Lexicographical Sequence (LeetCode-style: Next Permutation)

Rearrange the characters of a string into the next arrangement in dictionary order. If the string is already the last arrangement, return the first one, the characters in nondecreasing order.

"Next" means the next permutation in lexicographic order, the same contract as C++ `std::next_permutation`: the following arrangement of these same characters, or the first arrangement if this one is the last. Walk an example before coding. For the exercise string `"bac"`, the arrangements in order are `abc`, `acb`, `bac`, `bca`, `cab`, `cba`. The next one after `bac` is `bca`. After `cba` there is nothing later, so the answer wraps to `abc`.

The algorithm is the staged scan. Find the rightmost index `i` with `s[i] < s[i + 1]`. That is the pivot. The suffix after it is non-increasing, which is why it was not chosen. Swap the pivot with the rightmost suffix character that is strictly larger than the pivot. That successor is the smallest increase that still sits as far right as possible, which matters when the suffix has duplicates. Then reverse the suffix. The reverse is the smallest order of a non-increasing run. Sorting the suffix would also work and would cost an extra log factor on that piece.

```python
def next_sequence(text: str) -> str:
    chars = list(text)
    pivot = len(chars) - 2
    while pivot >= 0 and chars[pivot] >= chars[pivot + 1]:
        pivot -= 1
    if pivot >= 0:
        successor = len(chars) - 1
        while chars[successor] <= chars[pivot]:
            successor -= 1
        chars[pivot], chars[successor] = chars[successor], chars[pivot]
    left, right = pivot + 1, len(chars) - 1
    while left < right:
        chars[left], chars[right] = chars[right], chars[left]
        left += 1
        right -= 1
    return "".join(chars)


print(next_sequence("bac"), next_sequence("cba"), next_sequence("1322"), next_sequence("a"))
# bca abc 2123 a
```

`"1322"` shows the duplicate trap. The pivot is the leading `1`. The rightmost character larger than `1` is the final `2`, not the `3`. Swap to `"2321"`, then reverse the suffix to `"2123"`. Swapping with the `3` and then reversing the suffix produces `"3221"`, which skips `"2123"`. A string with no pivot, such as `"cba"`, reverses as a whole. A one-character string is already both the first and the last arrangement.

The scans are O(n). A Python string is immutable, so the function copies it into a list, which is O(n) extra memory. The same steps on a list the caller owns can mutate that list with O(1) extra memory.

**Trade-offs.** The staged scan is linear. Generating every permutation and picking the next one is factorial and answers a different question, "list them all." Sorting the suffix is easier to remember and slower by a log factor. Taking the leftmost larger successor instead of the rightmost one skips arrangements whenever more than one suffix character is larger than the pivot.

**Interview.** Define "next" with four arrangements of a three-letter exercise string, including the wrap from the last arrangement to the first. Name the pivot, then the rightmost larger successor, then the reverse. Say what you do when the first scan falls off the left end. Mention the string copy if the input is immutable.

**Recap.** The next arrangement is the one that increases the rightmost position that can still increase, then leaves the suffix in the smallest order. Find that pivot from the right, swap it with the rightmost strictly larger successor, and reverse the suffix. If there is no pivot, reverse the whole string. The work is linear, plus a list copy when the input is a Python string.

## Skipping duplicates after a sort

After a sort, equal values sit next to each other, so a duplicate is a neighbor comparison instead of a search.

That is why the triplet scan can promise unique results without a set. A fixed value that equals the value at the previous index is the same start you already ran. An inner value that equals the one you just used would rebuild the same triplet with a different index. Unix `uniq` is the same observation on text: it collapses adjacent duplicate lines, so a file has to be sorted first if duplicates that were not already neighbors should collapse too. The [Sort, then scan](../06_Moderate_Problems/) card is the general "neighbors become meaningful" idea. This card is the skip you add when the scan would otherwise emit the same answer again.

The early stop at a positive fixed value is a separate fact, and it is only valid for a target of zero. The indexes below are the fixed positions the triplet scan is willing to use on one exercise list.

```python
def fixed_indexes_to_use(ordered: list[int]) -> list[int]:
    use: list[int] = []
    for i, value in enumerate(ordered):
        if value > 0:
            break
        if i > 0 and value == ordered[i - 1]:
            continue
        use.append(i)
    return use


print(fixed_indexes_to_use([-4, -1, -1, 0, 1, 2, 2]))
# [0, 1, 3]
```

Index 2 is the second `-1`, and it is skipped. Indexes of the positive values are never used as the fixed position. On `[-2, 0, 0, 2]`, a hit at `(-2, 0, 2)` has to move both inner indexes. Moving only the left one lands on the second `0` and emits the same values again.

The same neighbor rule is how the pattern grows past three values. Sort once. To find k values that sum to a target, fix one value and ask the same question for k - 1 values in the suffix, until the question is a pair and the inward scan can finish it. The pair scan is linear, so three values are quadratic, and each extra value adds another factor of n. The sort is O(n log n), which is smaller than that for three or more values, and in this Python it is still an extra list.

**Trade-offs.** Neighbor skips cost a few comparisons and no extra memory. A set of answer tuples is shorter to write, hashes every answer, and can store a quadratic number of them. It also lets a buggy inner loop look correct. Skipping is easy to forget at one of the three sites, and the tests that catch it are inputs with repeated values, not inputs with all distinct values.

**Interview.** Say "duplicates are adjacent, so I skip equals as I go" rather than "I will unique it at the end." Name the sites you skip. Say the positive-value stop is about the target, not about duplicates. If the interviewer asks about four values, describe the extra fixed index and the same inner pair scan, and give the time as O(n^3) after the sort.

**Recap.** Sorting puts copies side by side, so uniqueness is a neighbor test at the fixed index and at both inner indexes after a hit. A set of tuples also deduplicates, and it hides the cost. The same reduction, fix one value and scan the rest, is how the pair scan answers sums of more than three values. The sort's extra list is the memory, and the scans dominate the time.

## Two pointers, a hash map, or brute force

The choice follows the constraint you can point at: sorted order, original indexes, extra memory, or a structure that is not a pair at all.

A nested loop is the baseline. It uses constant extra memory, it works unsorted, and its time grows with the square of the length. Say it, give that cost, and then replace it. Two pointers replace it when a move has a proof. On a sorted array the proof is the inward one, and the pair scan becomes linear with constant extra memory. A hash map replaces it when the array is unsorted and you want a complement: for each value, ask whether `target - value` is already stored, then store the value. That is one expected linear pass and extra memory proportional to the length, and it is written out on the [Unsorted pair-sum with a hash set](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) card. Check the map before you insert, or a single copy of a number will look like a pair with itself.

The counts below are for one exercise list, not a benchmark. The target 31 has one pair, indexes 1 and 7, values 2 and 29.

```python
def comparisons(values: list[int], target: int) -> tuple[int, int, int]:
    left, right = 0, len(values) - 1
    inward = 0
    while left < right:
        inward += 1
        total = values[left] + values[right]
        if total == target:
            break
        if total < target:
            left += 1
        else:
            right -= 1

    brute = 0
    for i in range(len(values)):
        found = False
        for j in range(i + 1, len(values)):
            brute += 1
            if values[i] + values[j] == target:
                found = True
                break
        if found:
            break

    seen: dict[int, int] = {}
    hashed = 0
    for index, value in enumerate(values):
        hashed += 1
        if target - value in seen:
            break
        seen[value] = index
    return inward, brute, hashed


print(comparisons([1, 2, 4, 7, 11, 16, 22, 29], 31))
# (2, 13, 8)
```

On this list the inward scan adds twice, the double loop adds 13 times, and the hash map looks at 8 values before it sees 29. A different target moves those counts around. The bounds do not: linear for the inward scan on sorted input, quadratic for the nested loop, expected linear for the hash map. Sorting an unsorted array so you can run the inward scan costs O(n log n) time and, with `sorted`, a new list. It also changes indexes unless you sort `(value, index)` pairs and return the stored indexes. If you needed those original indexes, the hash map was the direct tool.

Some problems in this topic are not pair-sum problems, so the hash map is not a competitor. The palindrome check needs symmetry. The container needs index distance, and sorting the heights would throw the widths away. The zero shift needs a writer. The next arrangement needs the staged suffix proof. A sliding window, on the [Sliding window](../06_Moderate_Problems/) card, is the right tool when the answer is a contiguous segment with a monotone sum. Floyd's scan is the right tool when the structure is a linked list and the question is a cycle.

**Trade-offs.** Two pointers buy linear time and constant extra memory when the discard is real, and they are simply wrong when it is not. A hash map buys expected linear time on unsorted pair searches and spends memory. Sorting first buys the discard and spends the sort. The nested loop buys an obvious correct answer and spends quadratic time. Using a set to clean up duplicates after the fact buys shorter code and hides both time and memory.

**Interview.** Start from the constraint in the sentence, not from a favorite loop. Sorted, or safe to sort, and constant memory: two pointers, and say which end moves. Unsorted, original indexes, pair complement: hash map, and say you insert after the check. Contiguous sum: sliding window. Cycle in a list: Floyd. Then give both costs, time and extra memory, including the sort if you introduced one. Offer the nested loop as the check you would run on a tiny input.

**Recap.** Two pointers are the linear, constant-memory scan when order or symmetry lets a move delete whole groups of candidates. A hash map is the linear, extra-memory scan when the question is an unsorted complement and the original indexes matter. A nested loop is the correct baseline you name first. Palindromes, containers, compaction, and next arrangements stay on two pointers even though a hash map solves pair sums, because those problems are not complement lookups.
