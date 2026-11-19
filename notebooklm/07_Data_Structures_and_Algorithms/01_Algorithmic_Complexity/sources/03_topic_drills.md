# Algorithmic Complexity — Drills

Original mini-drills for Big O skills. Each card is one exercise: read the snippet, state the bound, then check the answer. No copyrighted book text.

## Single pass / early exit

State the tightest practical time and space for this function. Justify in one sentence.

```python
def find_first_negative(xs: list[int]) -> int | None:
    for x in xs:
        if x < 0:
            return x
    return None
```

**Answer:** Worst-case time O(N), best-case O(1) if the first element is negative; O(1) extra space. One linear scan with possible early exit.

## Nested loops, same length → N²

```python
def count_pairs(xs: list[int]) -> int:
    n = len(xs)
    c = 0
    for i in range(n):
        for j in range(n):
            if xs[i] < xs[j]:
                c += 1
    return c
```

**Answer:** Time O(N²), space O(1). Outer and inner both run N times → multiply.

## Triangle nested loops still N²

```python
def count_ordered_pairs(xs: list[int]) -> int:
    n = len(xs)
    c = 0
    for i in range(n):
        for j in range(i + 1, n):
            c += 1
    return c
```

**Answer:** Time O(N²), space O(1). ~N(N−1)/2 iterations — drop the constant, still O(N²).

```python
n = 10
iterations = sum(1 for i in range(n) for _ in range(i + 1, n))
print(iterations, n * (n - 1) // 2)  # 45 45 — still quadratic
```

## Independent loops → add

```python
def prep_then_scan(xs: list[int]) -> int:
    positives = [x for x in xs if x > 0]  # pass 1
    total = 0
    for x in positives:                   # pass 2
        total += x
    return total
```

**Answer:** Time O(N), space O(N) for the filtered list. Two sequential O(N) passes → add → O(N).

## Loop to N/2 is still O(N)

```python
def sum_first_half(xs: list[int]) -> int:
    n = len(xs)
    total = 0
    for i in range(n // 2):
        total += xs[i]
    return total
```

**Answer:** Time O(N), space O(1). N/2 iterations drop the constant → O(N).

## Loop to √N

```python
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True
```

**Answer:** Time O(√N), space O(1). The loop bound is √N, not N.

```python
n = 97  # prime, so the loop runs to completion
steps, d = 0, 2
while d * d <= n:
    steps += 1
    d += 1
print(steps)  # 8, on the order of sqrt(97) rather than 97
```

## Doubling step → log N

```python
def highest_power_of_two(n: int) -> int:
    p = 1
    while p * 2 <= n:
        p *= 2
    return p
```

**Answer:** Time O(log N), space O(1). Each step doubles p → about log₂ N iterations.

```python
n, steps, p = 1000, 0, 1
while p * 2 <= n:
    p *= 2
    steps += 1
print(steps, p)  # 9 512 — about log2(1000) steps
```

## Two input sizes — keep A and B

```python
def any_in_set(needles: list[int], haystack: set[int]) -> bool:
    for x in needles:
        if x in haystack:
            return True
    return False
```

**Answer:** Time O(A) average with a hash set of size B already built; building the set from a list of length B would be O(A + B). Do not collapse to a fake single N.

## Nested over A and B → multiply

```python
def cross_count(a: list[int], b: list[int]) -> int:
    c = 0
    for x in a:
        for y in b:
            if x < y:
                c += 1
    return c
```

**Answer:** Time O(A · B), space O(1). For each of A elements, scan all B → multiply.

## One recursive call down by 1

```python
def sum_to_zero(n: int) -> int:
    if n <= 0:
        return 0
    return n + sum_to_zero(n - 1)
```

**Answer:** Time O(N), space O(N) stack. N frames, constant work each.

## Two branches without memo → exponential

```python
def count_paths(steps: int) -> int:
    if steps <= 1:
        return 1
    return count_paths(steps - 1) + count_paths(steps - 2)
```

**Answer:** Time O(2^N), space O(N) stack. Two recursive calls per level without caching.

```python
def count_calls(steps: int) -> int:
    """How many calls this recursion makes, including itself."""
    if steps <= 1:
        return 1
    return 1 + count_calls(steps - 1) + count_calls(steps - 2)

print(count_calls(10))  # 177 calls — far more than 10
```

## Sum the recursion tree (balanced)

```python
def merge_sort_work(n: int) -> int:
    """Toy model: cost of merge-sort-style recursion on size n."""
    if n <= 1:
        return 1
    return merge_sort_work(n // 2) + merge_sort_work(n // 2) + n
```

**Answer:** Time O(N log N). log N levels, ~N work per level → sum the tree, do not stop at branches^depth.

## Memoization collapses exponential

```python
from functools import lru_cache

@lru_cache(None)
def count_paths_memo(steps: int) -> int:
    if steps <= 1:
        return 1
    return count_paths_memo(steps - 1) + count_paths_memo(steps - 2)
```

**Answer:** Time O(N), space O(N) for the cache (+ stack). Each `steps` value computed once.

```python
from functools import lru_cache

@lru_cache(None)
def count_paths_memo(steps: int) -> int:
    if steps <= 1:
        return 1
    return count_paths_memo(steps - 1) + count_paths_memo(steps - 2)

count_paths_memo(10)
print(count_paths_memo.cache_info().misses)  # 11: steps 0..10, once each
```

## Permutation branching → factorial class

```python
def permutations(chars: list[str]) -> list[list[str]]:
    if len(chars) <= 1:
        return [chars[:]]
    out: list[list[str]] = []
    for i, ch in enumerate(chars):
        rest = chars[:i] + chars[i + 1 :]
        for p in permutations(rest):
            out.append([ch] + p)
    return out
```

**Answer:** Time in the Θ(N!) class for interviews (N! leaves; tree work is larger by a polynomial factor you drop). Space O(N) for the call stack besides the output.

```python
def leaf_count(n: int) -> int:
    return 1 if n <= 1 else n * leaf_count(n - 1)

print(leaf_count(4))  # 24 == 4! leaves
```

## Hidden quadratic from repeated copy

```python
def join_chars(chars: list[str]) -> str:
    s = ""
    for ch in chars:
        s = s + ch   # builds a new string each time
    return s
```

**Answer:** Time O(N²) with immutable strings (each concat copies), space O(N) for the result. Prefer a builder / `''.join` for O(N).

```python
def join_chars(chars: list[str]) -> str:
    return "".join(chars)  # one pass, O(N)

print(join_chars(["a", "b", "c", "d"]))  # abcd
```

## Interview answer: time, space, case

For this function, write the one-liner you would say in an interview (time, space, case if they differ).

```python
def has_pair_sum(items: list[int], target: int) -> bool:
    seen: set[int] = set()
    for x in items:
        if (target - x) in seen:
            return True
        seen.add(x)
    return False
```

**Answer:** "Average/expected time O(N) from one pass with O(1) hash lookups; O(N) extra space for the set; worst-case hash degradation is rare and usually not the focus unless asked."
