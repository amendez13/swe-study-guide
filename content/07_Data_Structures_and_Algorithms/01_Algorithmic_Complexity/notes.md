# Algorithmic Complexity (Big O)

Algorithmic complexity is the framework engineers use to reason about how algorithms scale. Instead of measuring raw execution time, which varies across machines and inputs, Big O notation captures the growth rate of time or space as a function of input size. Mastering this lets you predict performance bottlenecks, choose between competing approaches, and communicate tradeoffs precisely during design discussions and interviews.

## Key Points

- **Big O describes growth, not speed** - It tells you how runtime or memory scales with input size, not how many milliseconds something takes on your laptop.
- **Tightest bound wins in practice** - Although O is technically an upper bound, engineers use it to mean the tight bound; say O(N), not O(N^2), when the algorithm is linear.
- **Best, worst, and expected cases differ** - QuickSort is O(N log N) expected but O(N^2) worst case; randomized pivots make the worst case extremely unlikely.
- **Space counts separately** - Recursive Fibonacci uses O(N) stack space even though its time complexity is O(2^N); always analyze both dimensions.
- **Drop constants and non-dominant terms** - O(3N^2 + 5N + 12) simplifies to O(N^2); asymptotic analysis cares about the shape of growth, not the coefficients.
- **Sequential steps add, nested steps multiply** - Two independent O(N) loops are O(N + N) = O(N); an O(N) loop inside another O(N) loop is O(N^2).
- **Amortized analysis averages over sequences** - A dynamic array append is O(1) amortized because the occasional O(N) resize is spread across N cheap appends.
- **Halving yields log N** - Any algorithm that cuts the problem in half each step runs in O(log N); binary search is the textbook example.
- **Recursive branching explodes exponentially** - O(branches^depth); naive Fibonacci is O(2^N) but memoization collapses it to O(N) by caching overlapping subproblems.
- **Know the complexity ladder** - O(1) < O(log N) < O(N) < O(N log N) < O(N^2) < O(2^N) < O(N!); anything above N log N struggles at scale.

## Example

```python
"""
Three algorithms solving the same problem at different complexities:
find whether any pair in a list sums to a target value.
"""

# --- O(N^2): brute-force nested loops ---
def has_pair_sum_quadratic(items: list[int], target: int) -> bool:
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] + items[j] == target:
                return True
    return False


# --- O(N log N): sort then use two pointers ---
def has_pair_sum_nlogn(items: list[int], target: int) -> bool:
    items = sorted(items)                     # O(N log N)
    lo, hi = 0, len(items) - 1
    while lo < hi:                            # O(N)
        s = items[lo] + items[hi]
        if s == target:
            return True
        elif s < target:
            lo += 1
        else:
            hi -= 1
    return False


# --- O(N): hash set lookup ---
def has_pair_sum_linear(items: list[int], target: int) -> bool:
    seen: set[int] = set()
    for x in items:                           # O(N)
        if (target - x) in seen:              # O(1) average lookup
            return True
        seen.add(x)
    return False


# All three produce the same result, but scale very differently
data = list(range(10_000))
target = 19_997

print(has_pair_sum_quadratic(data, target))   # True -- slow at scale
print(has_pair_sum_nlogn(data, target))       # True -- faster
print(has_pair_sum_linear(data, target))      # True -- fastest
```

This example demonstrates the real-world consequence of algorithmic complexity: the brute-force O(N^2) approach examines nearly 50 million pairs for 10,000 elements, while the hash-set O(N) approach checks 10,000 elements with constant-time lookups. Choosing the right complexity class is often the single most impactful performance decision in a codebase.
