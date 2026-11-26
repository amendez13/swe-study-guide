# Math and Geometry

Math and geometry problems hide a small identity behind a brute-force-looking prompt: reverse a number's digits without overflowing 32 bits, find the most points on one line without trusting floats, walk a matrix in a spiral, pick the survivor of a counting-out circle, or answer for row 10⁹ of a triangle in O(1). Divisibility, primes, gcd, modular arithmetic, and fast powers are taught on [Math and Logic Puzzles](#11_Coding_Problems/01_Math_and_Logic_Puzzles), and digit and overflow basics on [Moderate Problems](#11_Coding_Problems/06_Moderate_Problems). This topic is the problem set: spotting the problem, exact arithmetic, overflow checks, digits of negatives, canonical ratio keys, modular answers, shrinking boundaries, patterns from small cases, recurrences, and five worked problems. The two decisions are how to keep every step exact (integers, reduced fractions, checks before the operation) and whether a recurrence or a verified pattern can replace the simulation.

## Key Points

- **Spotting a math and geometry problem** — digits, 32-bit limits, points and slopes, matrix walks, circles, "row 10⁹ in O(1)"; keep geometry in integers (shoelace area doubled).
- **Floats and exact answers** — `0.1 + 0.2 != 0.3`; cross-multiply to compare fractions; integer cross product for collinearity and turn direction.
- **Overflow checks before the operation** — test `r > (LIMIT - d) // 10` before `r * 10 + d`; the negative limit is one larger; Year 2038 and Ariane 5.
- **Digits with truncating division** — Python floors (`-123 % 10 == 7`), C and Java truncate; strip the sign, work on `abs`, restore it.
- **Reduced fractions as keys** — divide by gcd, make the run positive, one key for vertical; O(log C) per key.
- **Modular answers for huge counts** — reduce after every `+` and `*` modulo 10⁹ + 7; inverse via `pow(b, M - 2, M)`; fix negative remainders outside Python.
- **Walking shrinking boundaries** — four bounds, walk a side, move it in; stop when `top > bottom` or `left > right`; O(m · n).
- **Patterns from small cases** — brute force small n, reduce mod what matters, guess the cycle or formula, verify on many more values.
- **Recurrences that shrink the problem** — express n through n − 1 (`R(n) = R(n - 1) + n`), then a loop or a closed form.
- **Spiral order of a matrix** — four bounds; re-check `top <= bottom` and `left <= right` before the backward walks; O(m · n).
- **Reverse a 32-bit integer** — pop digits of `abs(x)`, check before each push, sign-dependent limit; O(digits).
- **Most points on one line** — per anchor, count reduced direction keys; duplicates join every line; O(n² log C).
- **The last survivor in a circle** — `J(n) = (J(n - 1) + k) % n`, 0-based; loop for O(n) time and O(1) space.
- **First even number in a sum triangle** — work mod 2; the answer cycles with period 4 from row 3 (2, 3, 2, 4); O(1).
- **Formula, simulation, or search** — simulate when n is small, use math when it is large, and keep the simulation as a test oracle.

## Example

```python
from math import gcd


def fence_posts(a: tuple[int, int], b: tuple[int, int]) -> int:
    dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
    return gcd(dx, dy) + 1


print(fence_posts((0, 0), (12, 8)), fence_posts((3, 7), (3, 1)), fence_posts((-2, 5), (4, -4)))
print(fence_posts((1, 1), (1, 1)), fence_posts((0, 0), (7, 5)))
# 5 7 4
# 1 2
```

A straight fence runs between two grid corners, and a post goes at every point along it with whole-number coordinates. Walking from one end, the posts repeat every `(dx / g, dy / g)` step, where g is the gcd of the two distances, so there are g steps and g + 1 posts, counting both ends. That is O(log C) time with no floats and no loop over the fence, and it handles vertical, horizontal, and zero-length fences in the same formula. The coordinates are exercise values.

## More practice

Work the original exercises on the **Drills** tab. Each one names the approach, the cost, and a Python check.
