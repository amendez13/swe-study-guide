# Prefix Sums

A prefix sum array stores running totals, so the sum of any contiguous block is one subtraction. The short version is [Prefix sums](#11_Coding_Problems/06_Moderate_Problems/concepts/prefix-sums). This topic builds on it: range queries, counts and longest runs with a hash map of earlier prefixes, products from both sides, remainders, rectangles, range updates, and weighted picks. The two decisions are the layout, with or without a leading 0, and the tool: a prefix array for fixed data, a [sliding window](#11_Coding_Problems/13_Sliding_Windows/concepts/window-two-pointers-or-prefix-sums) for non-negative budgets, and a Fenwick tree when values change.

## Key Points

- **Prefix sum array** — `prefix[0] = 0` and `prefix[i + 1] = prefix[i] + nums[i]`. The inclusive range `[i, j]` is `prefix[j + 1] - prefix[i]`. Without the leading 0 it is `run[j] - run[i - 1]`, and `i == 0` needs a branch.
- **Recognize a prefix sum problem** — many range sums, a count of subarrays with an exact sum, a running balance, or a sum target with negatives. One query needs only a loop.
- **Range sum queries** — build once in O(n), answer each query in O(1). Dropping the `+ 1` on an inclusive end loses the last value.
- **When the array changes** — one update rewrites every later prefix. A Fenwick tree does updates and prefix queries in O(log n).
- **Count subarrays that sum to k** — count earlier prefixes equal to `running - k` in a map seeded with `{0: 1}`. Look up before recording. O(n).
- **Longest subarray that sums to k** — store the first index of each prefix, seeded with `{0: -1}`. Overwriting with the latest index shortens the answer.
- **Product of array except self** — left products, then a running right product. No division, so zeros need no case.
- **Prefix remainders** — equal prefix remainders mod m enclose a divisible run. Python's `%` is non-negative. C and Java need normalizing.
- **2D prefix sums** — a padded summed-area table. A rectangle is the block minus two strips plus the corner. The integral image in Viola–Jones.
- **Difference arrays** — `+d` at the start, `-d` after the end, then one prefix pass. All updates before any read.
- **Prefix counts and prefix XOR** — any operation with an inverse works. Max and min do not.
- **Prefix sums, sliding window, or Fenwick tree** — fixed data or negatives take prefixes, non-negative budgets take a window, and changing data takes a tree.
- **Weighted random pick** — running totals of weights and `bisect_right` on a draw in `[0, total)`. The binary search side is [Random pick by weight](#11_Coding_Problems/14_Binary_Search/concepts/random-pick-by-weight).

## Example

```python
def count_sum_k(nums: list[int], k: int) -> int:
    seen = {0: 1}
    running = count = 0
    for value in nums:
        running += value
        count += seen.get(running - k, 0)
        seen[running] = seen.get(running, 0) + 1
    return count


def range_sum(prefix: list[int], i: int, j: int) -> int:
    return prefix[j + 1] - prefix[i]


prefix = [0]
for value in [6, -2, 4, -4, 2]:
    prefix.append(prefix[-1] + value)
print(prefix, range_sum(prefix, 1, 3), range_sum(prefix, 0, 4))
print(count_sum_k([6, -2, 4, -4, 2], 4), count_sum_k([], 0))
# [0, 6, 4, 8, 4, 6] -2 6
# 3 0
```

The range `[1, 3]` is `-2 + 4 - 4`. The three runs that sum to 4 are `[6, -2]`, `[4]`, and `[6, -2, 4, -4]`. The first and the last start at index 0, so the seed finds them. An empty list has no runs. All inputs are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the rule, the cost, and a Python check.
