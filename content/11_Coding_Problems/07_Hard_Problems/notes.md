# Hard Problems

This topic is an outline for problems whose next step is not obvious: define the state, make the argument shrink, cache subproblems that repeat, and look for a mathematical rewrite before building a large search. The cards are a skeleton. They do not include published problems or solutions.

## Key Points

- **Hard means the structure is not obvious** — the brute force exists; the model that makes it cheap does not, yet.
- **Spend time on the model** — define the subproblem in one sentence and check it on a tiny input.
- **Shrink the argument** — name what gets smaller and the base case in the same vocabulary.
- **Cache repeated subproblems** — the cache key is exactly the arguments the answer depends on.
- **Rewrite the question in math** — a bound, a count, or an invariant can replace the search; check it against the brute force.
- **Keep the state small** — every extra field multiplies the states. Drop a field only with a reason.
- **A correct slower solution beats a stuck clever one** — submit the slow correct version and describe the faster state separately.

## Example

```python
from functools import lru_cache

def ways_brute(target: int) -> int:
    """Number of ordered ways to write target as a sum of 1s and 2s."""
    def rec(left: int) -> int:
        if left == 0:
            return 1
        if left < 0:
            return 0
        return rec(left - 1) + rec(left - 2)
    return rec(target)

@lru_cache(maxsize=None)
def ways(left: int) -> int:
    if left == 0:
        return 1
    if left < 0:
        return 0
    return ways(left - 1) + ways(left - 2)

for n in range(8):
    assert ways_brute(n) == ways(n)
```

The state is the remaining total, which shrinks on every call. The same remaining total is reached by many orders of steps, so the cache is the whole improvement. The loop is the check against the brute force. A later pass can replace the cache with the closed Fibonacci form and show that the rewrite matches these values; that replacement is the "rewrite in math" card, not something to assume untested.
