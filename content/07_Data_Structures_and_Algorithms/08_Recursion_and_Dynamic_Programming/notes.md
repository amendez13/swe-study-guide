# Recursion and Dynamic Programming

Recursion decomposes a problem into smaller instances of itself until reaching a trivial base case. Dynamic programming extends this idea by recognizing when the same subproblems appear repeatedly and caching their results, transforming exponential brute-force solutions into polynomial ones. Mastering both techniques is essential because they underpin a huge share of algorithm design — from tree traversals and divide-and-conquer to optimization problems like shortest paths and resource allocation.

## Key Points

- **Recursive decomposition** — break a problem into smaller copies of itself; trust the recursive call for the smaller input and only reason about how one level combines results.
- **Base case** — write the termination condition first and check it is reachable for every input; prefer `n <= 0` over `n == 0` when the step can jump past zero.
- **Call stack and stack space** — every nested call adds a frame, so space is O(maximum depth); Python's default limit is 1000 frames and there is no tail-call elimination.
- **Recursive vs. iterative** — any recursion can become a loop or an explicit stack; recurse when depth is small or logarithmic, iterate when depth grows with N.
- **Top-down approach** — start from the size-N problem and ask how to split it into subproblems whose answers combine into the whole.
- **Bottom-up approach** — start from the simplest case and extend the answer for k to k + 1; in DP this becomes tabulation.
- **Half-and-half approach** — split the data in two (binary search, merge sort) for O(log N) depth; independent halves mean no DP is needed.
- **Recursion tree** — sketch one node per call; branches^depth is the first estimate of total calls (naive Fibonacci makes 177 calls for n = 10).
- **Overlapping subproblems** — the naive tree recomputes the same inputs; DP cost becomes distinct states x work per state.
- **Optimal substructure** — an optimal whole is built from optimal sub-answers; it fails when subproblems interact (longest simple path).
- **Is this a DP problem?** — both overlapping subproblems and optimal substructure; min, max, count, or feasibility questions are the usual clues, while "list every solution" points to backtracking.
- **State definition** — the smallest set of parameters that determines a sub-answer; it is the memo key and the table shape, and nothing else (such as the path so far) belongs in it.
- **Memoization** — top-down recursion plus a cache keyed by the state; solves only reachable states but keeps stack risk; use a fresh cache per top-level call.
- **Tabulation** — fill a table from base cases in dependency order; no stack risk and easy to space-optimize, but computes every cell.
- **Space optimization** — keep only the earlier values or rows the recurrence reads (two variables for Fibonacci, one row for grids), at the cost of losing reconstruction.
- **Fibonacci case study** — naive, memoized, tabulated, space-optimized: the four-step playbook for most DP problems.
- **Common DP patterns** — 1D linear, grid, knapsack-style choice, two sequences, and interval; the pattern tells you the table dimensions and fill order.
- **Knapsack-style choices** — unbounded reuse loops the budget upward; 0/1 choice with a 1D table loops it downward; greedy is not safe for arbitrary coin systems.
- **Reconstructing the solution** — keep the table or a choice record and walk back from the final state to recover the actual answer, not just its value.
- **Backtracking vs. DP** — backtracking lists solutions and pays for output size; memoized DP aggregates (count, min, max) over overlapping states.

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

print("fib(10) =", fib_opt(10))   # fib(10) = 55
print("fib(20) =", fib_opt(20))   # fib(20) = 6765
print("fib(30) =", fib_opt(30))   # fib(30) = 832040
```

Running this script prints the Fibonacci values and confirms that all four implementations produce identical results. The progression from naive to space-optimized is the standard DP optimization playbook: get the recurrence right first, then eliminate redundant work, then reduce memory.

## More practice

Work the original exercises on the **Drills** tab: read each prompt, commit to an answer, then open the card to check it. For background reading, open CTCI Chapter 8 on the private reader under `#chapter-8-recursion-and-dynamic-programming`, with the approach sections `#bottom-up-approach`, `#top-down-approach`, and `#half-and-half-approach`, then `#recursive-vs-iterative-solutions`, `#dynamic-programming-memoization`, and `#fibonacci-numbers`. Do not copy book text or solutions into these study files.
