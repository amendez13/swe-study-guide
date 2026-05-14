# Recursion and Dynamic Programming

Recursion decomposes a problem into smaller instances of itself until reaching a trivial base case. Dynamic programming extends this idea by recognizing when the same subproblems appear repeatedly and caching their results, transforming exponential brute-force solutions into polynomial ones. Mastering both techniques is essential because they underpin a huge share of algorithm design — from tree traversals and divide-and-conquer to optimization problems like shortest paths and resource allocation.

## Key Points

- **Recursive decomposition** — break a problem into smaller copies of itself; each call handles one piece and delegates the rest until a base case returns directly.
- **Base case first** — always write and verify the termination condition before the recursive step; a missing or unreachable base case causes infinite recursion and stack overflow.
- **Call stack cost** — every recursive call adds a frame to the stack, so linear recursion uses O(N) space even with no auxiliary data structure; deep recursion can exceed Python's default 1000-frame limit.
- **Top-down thinking** — start with the full problem, express it in terms of smaller subproblems, and trust recursion to handle them; this is the natural way to derive a recurrence.
- **Bottom-up building** — solve the smallest subproblems first and iterate forward to the full answer; avoids recursion overhead and stack overflow risk.
- **Half-and-half splitting** — divide the input in two and process each half (merge sort, binary search); yields O(log N) recursion depth instead of O(N).
- **Overlapping subproblems** — the key signal for DP: the naive recursive tree recomputes the same inputs many times; without this property, plain recursion or divide-and-conquer suffices.
- **Memoization (top-down DP)** — cache each subproblem's result on first computation and return it on subsequent calls; same recursive structure, exponential-to-polynomial speedup.
- **Tabulation (bottom-up DP)** — fill a table iteratively from base cases forward; no recursion, no stack risk, cache-friendly memory access.
- **Space optimization** — when the recurrence only references a fixed number of prior values, collapse the table to that many variables; Fibonacci needs only two, grid problems often need only the current and previous row.
- **DP applicability test** — a problem is a DP candidate when it has both overlapping subproblems and optimal substructure (the global optimum is composed of subproblem optima).
- **Common DP patterns** — staircase counting (Fibonacci variant), grid pathfinding (sum of cell above and cell left), coin change (unbounded knapsack), longest common subsequence (2D table with match/skip transitions).

## Example

```python
"""Fibonacci: four progressively optimized implementations."""


# 1. Naive recursion — O(2^N) time, O(N) stack space
def fib_naive(n: int) -> int:
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


# 2. Memoization — O(N) time, O(N) space (cache + stack)
def fib_memo(n: int, cache: dict[int, int] | None = None) -> int:
    if cache is None:
        cache = {}
    if n in cache:
        return cache[n]
    if n <= 1:
        return n
    cache[n] = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)
    return cache[n]


# 3. Tabulation — O(N) time, O(N) space (table only, no stack)
def fib_tab(n: int) -> int:
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


# 4. Space-optimized — O(N) time, O(1) space
def fib_opt(n: int) -> int:
    if n <= 1:
        return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev2 + prev1
    return prev1


# Verify all four agree
for n in range(15):
    values = [fib_naive(n), fib_memo(n), fib_tab(n), fib_opt(n)]
    assert len(set(values)) == 1, f"Mismatch at n={n}: {values}"

print("fib(10) =", fib_opt(10))   # 55
print("fib(20) =", fib_opt(20))   # 6765
print("fib(30) =", fib_opt(30))   # 832040
```

Running this script prints the Fibonacci values and confirms that all four implementations produce identical results. The progression from naive to space-optimized is the standard DP optimization playbook: get the recurrence right first, then eliminate redundant work, then reduce memory.
