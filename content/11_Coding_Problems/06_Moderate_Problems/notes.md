# Moderate Problems

A moderate problem is a direct task plus one shortcut: a count, an order, a window, a formula, or a small machine. These notes are the shortcuts. They are not a catalog of published problems. Say the obvious cost, the cost after the shortcut, and the empty input.

## Key Points

- **One insight and its cost** — name the brute force, then the structure that removes the repeated work, then whether that cost fits the limit.
- **Bit tests and masks** — test, set, and clear a flag. The lowest set bit is `mask & -mask`. Say the width if the word is fixed.
- **Swap without a temporary** — a tuple swap is the normal code. XOR swaps two different locations and clears a slot if both indexes are the same.
- **Overflow-safe arithmetic** — `lo + (hi - lo) // 2`, and reduce a product before it exceeds the width. Python grows. Java does not.
- **Count with a map** — one pass records how many times a key appears. Expected O(n). Use an array when the key is a small integer.
- **Two pointers** — on a sorted sequence, move the end that the rule discards. The scan is linear. The sort is the cost.
- **Sliding window** — add on the right, drop from the left while the rule is broken. Each index enters and leaves once. The rule has to be monotone.
- **Prefix sums** — `prefix[right + 1] - prefix[left]` is a range sum. Worth it when many ranges share one array.
- **Sort, then scan** — neighbors after a sort answer "closest" and "next change." Keep indexes if you must point back at the original order.
- **Merge intervals** — sort by start, extend the current end when the next start overlaps, otherwise emit a new span.
- **Simulate a small machine** — name the states and the legal events. Each event is O(1). An unnamed state becomes a wrong edge.
- **Digits, not the whole number** — `% 10` and `// 10`. Integers do not have leading zeros. A string code is a different problem.
- **Modulo and gcd** — wrap with `%`. The longest equal offcut of two lengths is `gcd`. Euclid replaces the larger length with the remainder.
- **Estimate, then the edges** — check that the data fits, then write empty, one element, all equal, and the boundary value.
- **Check the fast path** — a tiny input computed by hand, or a slow function, must match. A correct slow answer is allowed if the shortcut is not finished.

## Example

```python
"""One studio morning: pair kayaks, then the smallest gap between crate weights."""


def trips(weights: list[int], limit: int) -> int:
    ordered = sorted(weights)
    lo, hi = 0, len(ordered) - 1
    boats = 0
    while lo <= hi:
        if ordered[lo] + ordered[hi] <= limit:
            lo += 1
        hi -= 1
        boats += 1
    return boats


def smallest_gap(weights: list[int]) -> int | None:
    if len(weights) < 2:
        return None
    ordered = sorted(weights)
    return min(b - a for a, b in zip(ordered, ordered[1:]))


print(trips([1, 2, 4, 5], 6))       # 2
print(smallest_gap([8, 1, 5, 3]))   # 2
print(smallest_gap([4]))            # None
```

The kayak count is two pointers after a sort: each step discards the heavy boat, and the light boat only when it fits. The gap is a sort and a neighbor scan. The single crate is the edge the scan cannot answer.

## More practice

Work the original exercises on the **Drills** tab. Each one names the shortcut, the cost, and a Python check. None of them is a published problem from a book list.
