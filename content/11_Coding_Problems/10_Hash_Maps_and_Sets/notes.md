# Hash Maps and Sets

A hash map stores a payload under a key. A hash set stores the keys alone. The lookup is expected constant time, and it is linear when every key collides. The cards are the decisions that make the lookup answer the question you were asked: check before you insert, count then scan, design the key, and record marks before you mutate. These notes are those decisions. They are not a catalog of published problems.

## Key Points

- **Hash maps and sets: lookup by a key** — a map carries a payload, a set carries membership. Python's `dict` keeps insertion order. A `set` does not promise an order. Expected O(1) per operation, O(n) when every key collides. The hash, the collisions, and the resize stay on the arrays cards.
- **Complement lookup** — for each value, ask whether `target - value` is already stored, then store the value. A set answers yes or no. Inserting first lets one value pair with itself.
- **Counting with a map** — one pass writes counts. An array of 26 is the same idea when the key is a lowercase letter, with a worst-case bound. `uniq -c` counts adjacent lines and wants a sort first.
- **Designing the key** — the key is the definition of "same." A block index groups cells. Sorted letters group anagrams. A key that drops counts answers a different question at the same speed.
- **Marks stored in the input** — record original zeros before writing new ones. Two flags remember the first row and the first column. A sign is a legal mark only when every value is positive.
- **Pair Sum in an Unsorted Array (LeetCode-style: Two Sum)** — store the index after the check. Return the earlier index first, or an empty result. LeetCode 1 promises one pair and a length of at least 2. The sorted twin is two pointers.
- **Valid Digit Grid (LeetCode-style: Valid Sudoku)** — one pass, three families of sets, block index `(r // 3) * 3 + c // 3`. Dots are ignored. A pass is validity, not a completed grid. LeetCode 36 promises the alphabet and the 9 by 9 shape.
- **Zero a Row and a Column (LeetCode-style: Set Matrix Zeroes)** — sets of indexes are O(m + n) extra memory. Marks in the first row and column are O(1), if the marker row is cleared after the interior. LeetCode 73 starts at 1 by 1 and allows negatives.
- **Longest Run of Consecutive Values (LeetCode-style: Longest Consecutive Sequence)** — walk only from a missing predecessor, so the inner walks add up to n. Duplicates do not extend the run. A sort is the guaranteed O(n log n).
- **Triplets at a Fixed Ratio (HackerRank-style: Count Triplets)** — each value is the middle. Multiply the earlier partner count by the later one, after dropping the middle from the later map. Ratio 0, ratio 1, and a non-exact division are the edges. HackerRank stays positive.
- **A hash map, an array, a sort, or two pointers** — a complement or a count wants a hash. A dense range wants an array. Order or a guarantee wants a sort. A sorted pair with tight memory wants two pointers.

## Example

```python
def pair_sum_unsorted(values: list[int], target: int) -> tuple[int, int] | tuple[()]:
    seen: dict[int, int] = {}
    for index, value in enumerate(values):
        need = target - value
        if need in seen:
            return (seen[need], index)
        seen[value] = index
    return ()


def longest_run(values: list[int]) -> int:
    present = set(values)
    best = 0
    for value in present:
        if value - 1 in present:
            continue
        length = 1
        nxt = value + 1
        while nxt in present:
            length += 1
            nxt += 1
        if length > best:
            best = length
    return best


def count_fixed_ratio(values: list[int], ratio: int) -> int:
    earlier: dict[int, int] = {}
    later: dict[int, int] = {}
    for value in values:
        later[value] = later.get(value, 0) + 1
    total = 0
    seen = 0
    for value in values:
        later[value] -= 1
        if ratio == 0:
            if value == 0:
                total += seen * later.get(0, 0)
        elif value % ratio == 0:
            total += earlier.get(value // ratio, 0) * later.get(value * ratio, 0)
        earlier[value] = earlier.get(value, 0) + 1
        seen += 1
    return total


print(pair_sum_unsorted([4, 1, 7, 3], 8), pair_sum_unsorted([6], 12))
print(longest_run([9, 1, 8, 2, 7, 2]), longest_run([]))
print(count_fixed_ratio([4, 4, 4, 4], 1), count_fixed_ratio([5, 0, 0], 0))
# (1, 2) ()
# 3 0
# 4 1
```

The pair scan stores an index only after the lookup misses. The run walks from the bottom of each chain. The ratio count drops the current value from the later map before it multiplies. The lists are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the structure, the cost, and a Python check. None of them is a published problem from a book list.
