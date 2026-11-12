# Hash Maps and Sets — Drills

Original drills for lookup by a key: a complement, a count, a key you design, and marks stored in the input. Each answer has an approach, a cost, and Python. The lists and strings are exercise numbers, not measured data. None of these repeats the frequency-map tile drill, the first-repeated-id drill, the seen-set pair-sum bug, or the group-by-key drill.

## The second pass returns the same index

This two-pass pair search stores the last index of each value, then looks up `target - value`. On the exercise list `[5, 2, 8]` with target `10` it returns `(0, 0)`. What does the repaired search return, and what do both versions return for `[5, 5]` and for `[5]` with the same target?

**Answer:** The broken search returns `(0, 0)` because the stored index of `5` is `0`, and the check accepts that index. The real pair is `2 + 8` at `(1, 2)`, and the function never reaches it. The repair requires a different index. It returns `(1, 2)` on that list, `(0, 1)` on `[5, 5]`, and `None` on `[5]`. The broken search happens to return `(0, 1)` on `[5, 5]`, because the overwrite kept the later five, and it returns `(0, 0)` on a lone five. An empty list is `None` for both. The one-pass version of "insert, then check" is the [Seen-set pair sum: spot the bug](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) drill, on `[3, 8]` with target `6`. This drill is the two-pass overwrite. The [Pair Sum in an Unsorted Array (LeetCode-style: Two Sum)](../10_Hash_Maps_and_Sets/) card is the one-pass check-then-store version. Expected time is O(n). Extra memory is O(n). The collision worst case is O(n^2).

```python
def broken_two_pass(values: list[int], target: int) -> tuple[int, int] | None:
    last: dict[int, int] = {}
    for index, value in enumerate(values):
        last[value] = index
    for index, value in enumerate(values):
        partner = last.get(target - value)
        if partner is not None:
            return (index, partner)
    return None


def repaired_two_pass(values: list[int], target: int) -> tuple[int, int] | None:
    last: dict[int, int] = {}
    for index, value in enumerate(values):
        last[value] = index
    for index, value in enumerate(values):
        partner = last.get(target - value)
        if partner is not None and partner != index:
            return (index, partner)
    return None


print(broken_two_pass([5, 2, 8], 10), repaired_two_pass([5, 2, 8], 10))
print(broken_two_pass([5, 5], 10), repaired_two_pass([5, 5], 10))
print(broken_two_pass([5], 10), repaired_two_pass([5], 10))
print(broken_two_pass([], 0), repaired_two_pass([-2, 7, 1], 5))
# (0, 0) (1, 2)
# (0, 1) (0, 1)
# (0, 0) None
# None (0, 1)
```

## Two strings, one pattern

The exercise strings `"loop"` and `"beek"` follow one pattern: a character, then a different character twice, then a fourth character. `"boot"` and `"care"` do not. Decide whether two strings follow one pattern. What do `"ab"` and `"aa"` return, and what do the empty strings return?

**Answer:** `"loop"` and `"beek"` match, with `l` mapping to `b`, `o` mapping to `e`, and `p` mapping to `k`. `"boot"` and `"care"` fail because `o` would need both `a` and `r`. `"ab"` and `"aa"` fail because `b` would also map to `a`, which is already used. `"aa"` and `"ab"` fail because the second `a` would change its image. `"abba"` and `"cddc"` match. Different lengths fail. The empty strings match. A single character maps to a single character. The comparison is case-sensitive. `"aA"` and `"aa"` fail because `A` is a different character from `a`, and `a` is already used as an image. Folding case first would make both strings `"aa"`, and that pair would match. One map records the image of each left character. A set records images already used, which is the other direction. Expected time is O(n). Extra memory is O(n) for the distinct characters. A collision worst case is O(n^2). Two independent frequency counts are a different question: they ignore which character sits in which position. LeetCode 205, Isomorphic Strings, promises equal lengths of at least 1. This drill also returns false for unequal lengths and true for two empty strings.

```python
def same_pattern(left: str, right: str) -> bool:
    if len(left) != len(right):
        return False
    image: dict[str, str] = {}
    used: set[str] = set()
    for source, dest in zip(left, right):
        mapped = image.get(source)
        if mapped is None:
            if dest in used:
                return False
            image[source] = dest
            used.add(dest)
        elif mapped != dest:
            return False
    return True


print(same_pattern("loop", "beek"), same_pattern("boot", "care"), same_pattern("abba", "cddc"))
print(same_pattern("ab", "aa"), same_pattern("aa", "ab"), same_pattern("aA", "aa"))
print(same_pattern("", ""), same_pattern("a", "b"), same_pattern("abc", "de"))
# True False True
# False False False
# True True False
```

## A repeat in the last k readings

The exercise readings are `[8, 1, 8, 4, 4]`. Return the indexes of the first value that repeats at a distance of at most `k`. What do `k = 2` and `k = 1` return?

**Answer:** For `k = 2` the pair is `(0, 2)`, the two eights. For `k = 1` the first pair is `(3, 4)`, the two fours. Distance `2` is too far for `k = 1`, so the eights do not qualify, and the fours do. `k = 0` and a negative `k` return `None`, because two different indexes cannot be that close. An empty list and a one-element list return `None`. The structure is a map of the values inside the last `k` positions: add the new reading on the right, and drop the reading that just fell off the left. That window is the [Sliding window](../06_Moderate_Problems/) card with a set's membership test. A set is enough when the answer is only yes or no. The indexes need the position stored too. A map of the most recent index of every value, with no deletion, also works and uses O(n) extra memory rather than O(k). Expected time is O(n). The collision worst case is O(n^2). The function returns on the first repeat, so the window never holds two copies of one value. LeetCode 219, Contains Duplicate II, returns a boolean. Its length is at least 1, and its `k` may be 0. This drill returns the indexes, treats an empty list as no pair, and `k` of 0 is `None`.

```python
def close_repeat(values: list[int], k: int) -> tuple[int, int] | None:
    if k <= 0 or len(values) < 2:
        return None
    window: dict[int, int] = {}
    for index, value in enumerate(values):
        previous = window.get(value)
        if previous is not None:
            return (previous, index)
        window[value] = index
        expired = index - k
        if expired >= 0:
            leaving = values[expired]
            if window.get(leaving) == expired:
                del window[leaving]
    return None


print(close_repeat([8, 1, 8, 4, 4], 2), close_repeat([8, 1, 8, 4, 4], 1))
print(close_repeat([8, 1, 8, 4, 4], 0), close_repeat([], 3), close_repeat([4], 5))
# (0, 2) (3, 4)
# None None None
```

## Pairs a fixed gap apart

The exercise readings are `[1, 5, 3, 4, 2, 3]`. How many unordered pairs of distinct values differ by `2`, and how many index pairs differ by `2`? What changes when the gap is `0` on `[1, 1, 1]`?

**Answer:** Three value pairs differ by 2: `(1, 3)`, `(3, 5)`, and `(2, 4)`. The extra `3` does not add a value. Five index pairs differ by 2, because each of `(1, 3)` and `(3, 5)` occurs at two index combinations and `(2, 4)` occurs at one. On `[1, 1, 1]` with gap `0`, one value appears at least twice, and the index pairs are `C(3, 2) = 3`. A set can see that `1` exists and cannot see that it exists twice, so gap `0` needs the counts. A negative gap is the same pairs as its absolute value. An empty list and a one-element list have no pairs. A single value with gap `0` has no pair. Expected time is O(n). Extra memory is O(n). The collision worst case is O(n^2). This is a difference, not the target sum on the pair-sum card. LeetCode 532, K-diff Pairs in an Array, asks for the value-pair count with `k >= 0` and an array length of at least 1. This drill also returns the index-pair count, answers an empty list with `(0, 0)`, and a negative gap uses its absolute value.

```python
def gap_pairs(values: list[int], gap: int) -> tuple[int, int]:
    gap = abs(gap)
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    if gap == 0:
        value_pairs = sum(1 for count in counts.values() if count > 1)
    else:
        value_pairs = sum(1 for value in counts if value + gap in counts)
    seen: dict[int, int] = {}
    index_pairs = 0
    for value in values:
        index_pairs += seen.get(value - gap, 0)
        if gap != 0:
            index_pairs += seen.get(value + gap, 0)
        seen[value] = seen.get(value, 0) + 1
    return value_pairs, index_pairs


print(gap_pairs([1, 5, 3, 4, 2, 3], 2), gap_pairs([1, 5, 3, 4, 2, 3], -2))
print(gap_pairs([1, 1, 1], 0), gap_pairs([1], 0), gap_pairs([], 2))
# (3, 5) (3, 5)
# (1, 3) (0, 0) (0, 0)
```

## Which block holds this cell

On a 9 by 9 grid the blocks are 3 by 3. On a 16 by 16 grid the blocks are 4 by 4. Which block contains each exercise cell, and what does a cell outside the grid return?

**Answer:** On the 9-wide grid, `(0, 0)` and `(2, 2)` are block `(0, 0)`, `(0, 3)` is `(0, 1)`, `(3, 5)` is `(1, 1)`, and `(8, 8)` is `(2, 2)`. Column 3 starts the next block. On the 16-wide grid, `(4, 7)` is `(1, 1)` and `(15, 15)` is `(3, 3)`. A negative index and a row equal to the side return `None`. The block is `(row // box, col // box)` when `box` divides `side` and the cell sits inside the grid. The linear id `(row // box) * (side // box) + col // box` is 4 for `(3, 5)` on the 9-wide grid. The [Valid Digit Grid (LeetCode-style: Valid Sudoku)](../10_Hash_Maps_and_Sets/) card uses that id as a set index. The arithmetic is O(1). A hash is not required to name the block. It is required to remember which digits are already in it.

```python
def block_of(row: int, col: int, side: int, box: int) -> tuple[int, int] | None:
    if box <= 0 or side % box != 0:
        return None
    if not (0 <= row < side and 0 <= col < side):
        return None
    return (row // box, col // box)


cells = [(0, 0), (2, 2), (0, 3), (3, 5), (8, 8), (9, 0), (-1, 4)]
print([block_of(r, c, 9, 3) for r, c in cells])
print(block_of(4, 7, 16, 4), block_of(15, 15, 16, 4), block_of(15, 16, 16, 4))
print((3 // 3) * (9 // 3) + (5 // 3))
# [(0, 0), (0, 0), (0, 1), (1, 1), (2, 2), None, None]
# (1, 1) (3, 3) None
# 4
```

## Zeroing the cell you just wrote

The exercise matrix is `[[1, 2, 0, 4], [5, 6, 7, 8], [9, 0, 1, 2]]`. One pass writes zeros as soon as it sees a zero. Another records the original zeros and writes afterward. What does each leave behind?

**Answer:** The eager pass leaves a matrix of zeros. The scan sees the original zero at `(0, 2)` and clears row 0 and column 2. It is still on row 0, so the zero just written at `(0, 3)` clears column 3. Clearing column 2 also wrote a zero at `(1, 2)`, a cell the scan has not reached. When it gets there, that painted zero clears row 1. The original zero at `(2, 1)` then clears row 2, which still held `9`. The record-then-write pass clears row 0, row 2, column 2, and column 1, and leaves `5` and `8`. On `[[1, 0, 2], [3, 4, 5]]` the eager pass sees the zero at `(0, 1)` and clears that row and that column. Clearing the row writes a zero at `(0, 2)`. Clearing the column writes a zero at `(1, 1)`. The scan is still on row 0, so `(0, 2)` clears column 2, and the later visit to `(1, 1)` clears row 1. The recorded pass leaves `3` and `5`. A 1 by 1 zero and a 1 by 1 nonzero stay as they are under both passes. An empty matrix stays empty. Time is O(m n) either way. The recorded pass uses O(m + n) extra memory for the index sets. The eager pass uses O(1) extra memory and the wrong rows. The [Zero a Row and a Column (LeetCode-style: Set Matrix Zeroes)](../10_Hash_Maps_and_Sets/) card is the recorded pass, including the constant-memory marks.

```python
def zero_as_you_go(matrix: list[list[int]]) -> list[list[int]]:
    if not matrix or not matrix[0]:
        return matrix
    rows, cols = len(matrix), len(matrix[0])
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == 0:
                for k in range(cols):
                    matrix[r][k] = 0
                for k in range(rows):
                    matrix[k][c] = 0
    return matrix


def zero_after_recording(matrix: list[list[int]]) -> list[list[int]]:
    if not matrix or not matrix[0]:
        return matrix
    zero_rows = {r for r, row in enumerate(matrix) if 0 in row}
    zero_cols = {c for row in matrix for c, value in enumerate(row) if value == 0}
    for r in range(len(matrix)):
        for c in range(len(matrix[0])):
            if r in zero_rows or c in zero_cols:
                matrix[r][c] = 0
    return matrix


print(zero_as_you_go([[1, 2, 0, 4], [5, 6, 7, 8], [9, 0, 1, 2]]))
print(zero_after_recording([[1, 2, 0, 4], [5, 6, 7, 8], [9, 0, 1, 2]]))
print(zero_as_you_go([[1, 0, 2], [3, 4, 5]]))
print(zero_after_recording([[1, 0, 2], [3, 4, 5]]))
print(zero_as_you_go([[0]]), zero_after_recording([[4]]), zero_after_recording([]))
# [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
# [[0, 0, 0, 0], [5, 0, 0, 8], [0, 0, 0, 0]]
# [[0, 0, 0], [0, 0, 0]]
# [[0, 0, 0], [3, 0, 5]]
# [[0]] [[4]] []
```

## First letter that appears once

In the exercise string `"stress"`, which index holds the first character that appears once? What do `"aabb"`, `"a"`, and `""` return?

**Answer:** Index `1`, the `t`. `s` appears three times, and `t`, `r`, and `e` appear once. The scan of the string in order is what makes `t` win over `r`. `"aabb"` has no such character and returns `None`. `"a"` returns `0`. The empty string returns `None`. `"aab"` returns `2`. `"Stress"` returns `0`, because the comparison is case-sensitive and `S` is a different character from `s`. Count in one pass, then scan the original string so the order is the string's order rather than the map's order. Expected time is O(n). Extra memory is O(1) for a fixed alphabet stored in an array, or O(d) for a hash of d distinct characters. The [Counting with a map](../10_Hash_Maps_and_Sets/) card is the count. This drill is the second pass. LeetCode 387, First Unique Character in a String, returns that index or `-1`. Its string is lowercase and its length is at least 1. This drill returns `None` instead of `-1`, and it also answers the empty string and a capital letter.

```python
def first_once(text: str) -> int | None:
    counts: dict[str, int] = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    for index, ch in enumerate(text):
        if counts[ch] == 1:
            return index
    return None


print(first_once("stress"), first_once("aabb"), first_once("a"), first_once(""))
print(first_once("aab"), first_once("Stress"))
# 1 None 0 None
# 2 0
```

## Map, set, array, or sort

Name the structure for each exercise prompt, and the cost that comes with it.

1. Count the lowercase letters in a word.
2. Remember which order ids have already been printed.
3. Group short codes that use the same letters the same number of times.
4. Emit the distinct meter readings in sorted order.

**Answer:** An array of 26, a set, a map whose key is the sorted letters, and a sort. The letter tally is O(n) time and O(1) extra memory, and the bound is worst case because the index is arithmetic. The seen-id set is expected O(n) time, O(n) extra memory, and O(n^2) if every hash collides. Grouping by sorted letters is expected O(n k log k) for codes of length k. The inserts are O(n^2) if every key collides. Distinct readings in order are a sort, O(n log n) time and O(n) extra memory for `sorted`. A hash can collect the distinct readings and still needs a sort to order them. An empty collection does not change the choice. The [Group-by key: which key?](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) drill is the anagram key on a different word list. The [Two pointers, a hash map, or brute force](../09_Two_Pointers/) card is the pair-sum fork. These four prompts are the key, the set, the dense array, and the ordered output.

```python
def choose(prompt: str) -> tuple[str, str]:
    choices = {
        "letter-tally": ("array-26", "O(n) time, O(1) extra, worst case"),
        "seen-id": ("set", "expected O(n) time, O(n) extra, O(n^2) worst"),
        "anagram-groups": ("map-sorted-key", "expected O(n k log k) time"),
        "ordered-values": ("sort", "O(n log n) time, O(n) extra for sorted()"),
    }
    return choices[prompt]


print(choose("letter-tally"))
print(choose("seen-id"))
print(choose("anagram-groups"))
print(choose("ordered-values"))
# ('array-26', 'O(n) time, O(1) extra, worst case')
# ('set', 'expected O(n) time, O(n) extra, O(n^2) worst')
# ('map-sorted-key', 'expected O(n k log k) time')
# ('sort', 'O(n log n) time, O(n) extra for sorted()')
```

## Visits from the middle of a run

The exercise values are `[4, 1, 3, 2, 2, 8]`. One scan walks forward from every distinct value. Another walks only from a value whose predecessor is missing. How many set lookups does each inner walk perform, and what is the run length?

**Answer:** Walking from every distinct value performs 11 lookups: 4 from `1`, 3 from `2`, 2 from `3`, 1 from `4`, and 1 from `8`. Walking only from starts performs 5: the run `1, 2, 3, 4` and the run `8`. The length is 4. The duplicate `2` disappears in the set and adds neither a start nor a step. An empty list performs 0 lookups and has length 0. A single value performs 1 lookup under both rules and has length 1. Three copies of `7` do the same. On `[-2, -1, 0, 5]` the every-value walk performs 7 lookups and the start walk performs 4, and the length is 3. A run of n distinct values makes the every-value walk perform `n(n + 1) / 2` lookups, which is quadratic. The start rule is expected linear. The [Longest Run of Consecutive Values (LeetCode-style: Longest Consecutive Sequence)](../10_Hash_Maps_and_Sets/) card is that rule. Extra memory is O(n) for the set.

```python
def walk_counts(values: list[int]) -> tuple[int, int, int]:
    present = set(values)
    from_every = 0
    for value in present:
        nxt = value
        while nxt in present:
            from_every += 1
            nxt += 1
    from_starts = 0
    best = 0
    for value in present:
        if value - 1 in present:
            continue
        length = 0
        nxt = value
        while nxt in present:
            from_starts += 1
            length += 1
            nxt += 1
        if length > best:
            best = length
    return from_every, from_starts, best


print(walk_counts([4, 1, 3, 2, 2, 8]))
print(walk_counts([]), walk_counts([4]), walk_counts([7, 7, 7]))
print(walk_counts([-2, -1, 0, 5]))
# (11, 5, 4)
# (0, 0, 0) (1, 1, 1) (1, 1, 1)
# (7, 4, 3)
```
