# Arrays, Strings, and Hash Tables — Drills

Original mini-drills for array, string, and hash table skills. Each card is one exercise: read the prompt and snippet, commit to an answer, then check it. No copyrighted book text.

## Doubling: count the copies

A dynamic array starts with capacity 1 and doubles whenever an append finds it full. You append 9 items. How many element copies happen in total, and what is the final capacity?

```python
cap, size, copies = 1, 0, 0
for _ in range(9):
    if size == cap:
        copies += size      # move every existing element
        cap *= 2
    size += 1
print(copies, cap)
```

**Answer:** 15 copies (1 + 2 + 4 + 8), final capacity 16. The copies stay under 2N, which is why append is amortized O(1) even though individual resizes are O(N).

## Two pointers: which pairs get skipped?

Trace the pointers for `nums = [2, 4, 7, 10, 13]`, `target = 17`. Which pair is returned, and why is it safe to move `left` after the first comparison?

```python
def find_pair(nums: list[int], target: int) -> tuple[int, int] | None:
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return (left, right)
        if s < target:
            left += 1
        else:
            right -= 1
    return None
```

**Answer:** Returns `(1, 4)` → 4 + 13. First check is 2 + 13 = 15 < 17. Since 13 is the largest value, 2 cannot reach 17 with any partner, so every pair containing index 0 is eliminated at once. O(N) time, O(1) space.

## Write pointer: what is left behind?

What does this return, and what does `data` look like afterwards?

```python
def keep_non_multiples_of_3(xs: list[int]) -> int:
    write = 0
    for read in range(len(xs)):
        if xs[read] % 3 != 0:
            xs[write] = xs[read]
            write += 1
    return write

data = [3, 1, 6, 4, 9, 5]
n = keep_non_multiples_of_3(data)
```

**Answer:** `n == 3` and `data == [1, 4, 5, 4, 9, 5]`. Only the first `n` slots are meaningful; the tail keeps stale values. The caller should use `data[:n]` (or `del data[n:]`). O(N) time, O(1) extra space.

## Matrix mirror: where does (r, c) go?

Mirror a 2×3 grid left-to-right. Give the new position of the value at `(r, c)` and the resulting grid. Then: can a 2×3 grid be transposed in place?

```python
grid = [[1, 2, 3],
        [4, 5, 6]]
cols = len(grid[0])
mirrored = [[row[cols - 1 - c] for c in range(cols)] for row in grid]
transposed = [list(col) for col in zip(*grid)]
```

**Answer:** `(r, c) → (r, cols - 1 - c)`, giving `[[3, 2, 1], [6, 5, 4]]`. The transpose is `[[1, 4], [2, 5], [3, 6]]` — its shape changes from 2×3 to 3×2, so a list-of-rows layout cannot be transposed in place; you need a new grid. Square grids can swap `(r, c)` with `(c, r)` in place.

## Repeated += vs join: characters copied

Assume every `+=` copies the whole new string. Roughly how many characters are copied to build a 1,000-character string one character at a time? How many with `"".join(parts)`?

```python
s = ""
for ch in "x" * 1000:
    s += ch            # copy len(s) + 1 characters

parts = []
for ch in "x" * 1000:
    parts.append(ch)
s2 = "".join(parts)    # one pass over 1000 characters
```

**Answer:** 1 + 2 + … + 1000 = 500,500 copies → O(N²). The join version copies about 1,000 characters → O(N). (CPython sometimes optimizes `+=` in place, but do not rely on it; Java's `String` never does.)

## Frequency map: spell it from tiles

You hold letter tiles `rack` and want to spell `word` using each tile at most once. Fill in the condition and state the complexity.

```python
from collections import Counter

def can_spell(word: str, rack: str) -> bool:
    have = Counter(rack)
    for ch, needed in Counter(word).items():
        if ???:
            return False
    return True

print(can_spell("kettle", "tlekeat"))   # ?
print(can_spell("kettle", "tlekea"))    # ?
```

**Answer:** Condition `have[ch] < needed` (a missing key reads as 0 from a `Counter`). First call `True`, second `False` (only one `t`). O(len(word) + len(rack)) time, O(distinct letters) space.

## Hash set: first repeated ID

A stream of order IDs should be unique. Return the first ID that shows up a second time. Compare this to nested loops and to sorting.

```python
def first_repeat(ids: list[int]) -> int | None:
    seen: set[int] = set()
    for x in ids:
        if x in seen:
            return x
        seen.add(x)
    return None

print(first_repeat([41, 7, 19, 7, 41]))
```

**Answer:** Prints `7` (it repeats at index 3, before `41` repeats at index 4). O(N) average time, O(N) space. Nested loops are O(N²) with O(1) space; sorting is O(N log N) but loses "first in stream order" unless you also track positions.

## Seen-set pair sum: spot the bug

This unsorted pair-sum returns a wrong answer for `[3, 8]` with `target = 6`. What does it return and how do you fix it?

```python
def pair_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    seen: dict[int, int] = {}
    for j, x in enumerate(nums):
        seen[x] = j
        if target - x in seen:
            return (seen[target - x], j)
    return None
```

**Answer:** Returns `(0, 0)` — the 3 pairs with itself because it is recorded before the check. Swap the two steps: check for `target - x` first, then store `seen[x] = j`. Still one pass: O(N) time, O(N) space.

## Chaining: walk the bucket

A chained table has 5 buckets and uses `key % 5`. Insert 12, 7, 22, 3, 17 in that order (new keys append to the end of a chain). How many key comparisons does `get(17)` make? And `get(2)`?

```python
buckets = [[] for _ in range(5)]
for k in [12, 7, 22, 3, 17]:
    buckets[k % 5].append(k)
print(buckets)
```

**Answer:** Bucket 2 holds `[12, 7, 22, 17]` and bucket 3 holds `[3]`. `get(17)` compares 4 keys before matching; `get(2)` also lands in bucket 2 and compares all 4 keys before reporting a miss. A poor key distribution turns O(1) average into a linear chain walk.

## Fixed window: best 3-day total

Return the largest sum of any 3 consecutive values. What is the answer for this input, and what does each slide cost?

```python
def best_window(xs: list[int], k: int) -> int:
    cur = sum(xs[:k])
    best = cur
    for right in range(k, len(xs)):
        cur += xs[right] - xs[right - k]   # add entering, drop leaving
        best = max(best, cur)
    return best

print(best_window([4, -1, 2, 7, -3, 5], 3))
```

**Answer:** `9` from `[7, -3, 5]` (windows sum to 5, 8, 6, 9). Each slide is O(1), so the scan is O(N) instead of O(N·k) for re-summing every window.

## Load factor: when does it grow?

A table starts with 8 buckets and doubles whenever an insert would push the load factor above 0.75. You insert 20 distinct keys. How many rehashes happen, on which inserts, and what is the final load factor?

```python
size, count, events = 8, 0, []
for n in range(1, 21):
    if (count + 1) / size > 0.75:
        size *= 2
        events.append((n, size))
    count += 1
print(events, count / size)
```

**Answer:** Two rehashes: on insert 7 (7/8 > 0.75 → 16 buckets) and on insert 13 (13/16 > 0.75 → 32 buckets). Final load factor 20/32 = 0.625. Each rehash reinserts every key (O(N)), but doubling keeps inserts amortized O(1).

## Open addressing: linear probe

A 7-slot table uses `key % 7` and linear probing (try the next slot on a collision). Insert 10, 17, 3, 24. Where does each land? If you then delete 17 by simply emptying its slot, what goes wrong with `get(24)`?

```python
table = [None] * 7
for k in [10, 17, 3, 24]:
    i = k % 7
    while table[i] is not None:
        i = (i + 1) % 7
    table[i] = k
print(table)
```

**Answer:** All four hash to 3: 10 → slot 3, 17 → 4, 3 → 5, 24 → 6. If slot 4 becomes empty, `get(24)` starts at 3, sees 10, then hits the empty slot 4 and stops — a false miss. Deletes must leave a tombstone marker so probes keep walking.

## Ordered map vs hash map

A leaderboard needs: update a player's score, and list every player with a score between 70 and 90 in sorted order, many times per second. What does the dict-only version cost per range query, and what structure fixes it?

```python
scores: dict[str, int] = {"ana": 88, "ben": 72, "cy": 95, "dee": 64}

def in_range(lo: int, hi: int) -> list[tuple[int, str]]:
    return sorted((s, p) for p, s in scores.items() if lo <= s <= hi)
```

**Answer:** O(N log N) per query in the worst case (scan everything, then sort the hits). A balanced-BST map keyed by `(score, player)` (Java `TreeMap`, Python `sortedcontainers.SortedList`) answers it in O(log N + k) for k results, with O(log N) updates. Keep the dict too for O(1) player → score lookup.

## Strings are immutable: mutate a copy

What happens on the marked line, and how do you swap the first and last characters of `word`?

```python
word = "stack"
word[0] = "k"        # ?

chars = list(word)
chars[0], chars[-1] = chars[-1], chars[0]
word = "".join(chars)
print(word)
```

**Answer:** `TypeError: 'str' object does not support item assignment`. Convert to a list, mutate, and join: prints `ktacs`. The conversion and join are O(N) each, so batch all edits on one list instead of rebuilding the string per edit.

## Group-by key: which key?

Group these words two ways: by sorted letters, and by the set of distinct letters. How many groups does each key produce?

```python
from collections import defaultdict

words = ["loop", "pool", "polo", "lop", "plop"]
by_sorted: dict[str, list[str]] = defaultdict(list)
by_letters: dict[frozenset[str], list[str]] = defaultdict(list)
for w in words:
    by_sorted["".join(sorted(w))].append(w)
    by_letters[frozenset(w)].append(w)
```

**Answer:** Sorted key → 3 groups: `[loop, pool, polo]`, `[lop]`, `[plop]` (letter counts must match). Frozenset key → 1 group with all five (same letters `{l, o, p}`, counts ignored). The key you hash defines what "the same" means; it must be hashable, hence `frozenset` rather than `set`.

## Rolling hash with digits

Treat each character of `"31415"` as a digit and hash 3-character windows as base-10 numbers (no modulus, to keep it readable). Roll from the first window to the second in O(1). Where does the pattern `"141"` match?

```python
text, k = "31415", 3
h = int(text[:k])                 # 314
high = 10 ** (k - 1)              # weight of leftmost digit
for start in range(1, len(text) - k + 1):
    h = (h - int(text[start - 1]) * high) * 10 + int(text[start + k - 1])
    print(start, h)
```

**Answer:** 314 → (314 − 3·100)·10 + 1 = 141, then (141 − 1·100)·10 + 5 = 415. The hash 141 equals the pattern's at start index 1, so `"141"` matches there (confirm with a direct compare). Real implementations add a large prime modulus so the numbers stay small; that introduces collisions, which is why the confirming compare is required.
