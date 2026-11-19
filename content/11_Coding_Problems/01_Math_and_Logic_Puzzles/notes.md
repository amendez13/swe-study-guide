# Math and Logic Puzzles

Interview math in this chapter is a small toolbox plus a way of talking through a puzzle. The toolbox is divisibility, primes, the sieve, probability of "and" and "or," Euclid's algorithm, modular arithmetic, and exponentiation by squaring. The way of talking is the rest of the topic: restate the assumption, build a pattern from small cases, and choose the test that cuts the worst case down fastest. The numbers below are original examples, not a substitute for working the drills.

## Key Points

- **Divisibility** — `a % d == 0`. Digit sums settle divisibility by 3 and 9 because 10 ≡ 1 (mod 9). The last two digits settle divisibility by 4 because 100 is a multiple of 4.
- **Checking for primality** — 1 is not prime. Trial division stops at `floor(sqrt(n))`, and `math.isqrt` is the exact bound. After 2, skip even candidates.
- **Sieve of Eratosthenes** — mark composites in bulk, starting each prime `p` at `p*p`. Use it when you need every prime up to `n`: O(n log log n) time and O(n) memory.
- **Probability of A and B** — `P(A) * P(B | A)`. Multiply the bare probabilities only when the events are independent.
- **Probability of A or B** — `P(A) + P(B) - P(A and B)`. The complement, `1 - P(neither)`, is often the short path to "at least one."
- **Independence** — learning A does not change B. Check it with `P(A and B) == P(A) * P(B)`, not with a vibe that both things are "random."
- **Mutual exclusivity** — the overlap is empty, so "or" is a sum and "and" is zero. Two positive disjoint probabilities are dependent, because one event rules the other out.
- **Start talking** — restate the goal, name the assumption, and solve a smaller case out loud before committing to a formula.
- **Develop rules and patterns** — compute the first cases, look at differences, and test the candidate rule on a case you did not use to invent it.
- **Worst case shifting** — split the remaining possibilities as evenly as the test allows. `k` tests with `b` outcomes cover at most `b^k` possibilities.
- **Algorithm approaches** — state a correct brute force, then switch tools: one prime uses trial division, many primes use a sieve, a GCD uses Euclid, a power uses squaring.
- **GCD and LCM** — `gcd(a, b) = gcd(b, a % b)` until the remainder is 0. `lcm(a, b) = |a| / gcd(a, b) * |b|`, dividing before multiplying.
- **Modular arithmetic** — reduce before adding or multiplying, then reduce again. Division mod `m` needs an inverse. Normalize a negative remainder before you use it as an index.
- **Fast exponentiation** — square the base and multiply into the result on the 1-bits of the exponent. O(log n) multiplications, and every step can be reduced mod `m`.
- **Overflow awareness** — a sum of two in-range endpoints can leave the type. Write `lo + (hi - lo) / 2`, divide out a GCD before a product, and reduce mod `m` inside a power loop. Python's growing `int` will not save the Java or C version.

## Example

```python
"""One pass over the toolbox: sieve, Euclid, a safe LCM, and a modular power."""
import math


def sieve(n: int) -> list[int]:
    is_prime = [False, False] + [True] * (n - 1)
    for p in range(2, math.isqrt(n) + 1):
        if is_prime[p]:
            for multiple in range(p * p, n + 1, p):
                is_prime[multiple] = False
    return [i for i, prime in enumerate(is_prime) if prime]


def gcd(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return abs(a) // gcd(a, b) * abs(b)


def mod_pow(base: int, exp: int, mod: int) -> int:
    result = 1
    base %= mod
    while exp:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result


print(sieve(30))                  # 10 primes, ending at 29
print(gcd(1071, 462), lcm(18, 24))  # 21 72
print(mod_pow(5, 13, 100))        # 25
print((1 / 6 + 1 / 6 - 1 / 36))   # 11/36, at least one six
```

The sieve builds the list once. Euclid replaces factoring. The LCM divides before it multiplies, which is the same identity as `|a * b| / gcd` with a smaller intermediate. `mod_pow` is the overflow-safe way to ask for a last two digits. The probability line is the "or" rule with the double-counted overlap removed.

## More practice

Work the original exercises on the **Drills** tab. Read the prompt, commit to a number or a procedure, then open the card. The drills cover the same ideas as the cards: digit rules, a primality fencepost, the sieve, both probability combinations, a fixed-gap waiting assumption, a score sequence, balance-scale and yes/no worst cases, Euclid, modular multiplication, squaring, a wrapping midpoint, and one mislabeled-bin deduction.
