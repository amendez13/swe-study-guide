# Math and Logic Puzzles — Drills

Original mini-drills for divisibility, primality, the sieve, probability, puzzle reasoning, Euclid, modular arithmetic, fast exponentiation, and overflow. Each card is one exercise: read the prompt, commit to an answer, then check it. Each Answer has a short Python solution that runs on its own. No copyrighted book text.

## Receipt divisibility

A receipt total is 5832 cents. Without performing the full divisions, is the total divisible by 3, by 9, and by 4? What remainder does it leave mod 9?

**Answer:** The digit sum is 5 + 8 + 3 + 2 = 18, and 1 + 8 = 9, which is divisible by both 3 and 9, so the total is too. The remainder mod 9 is 0. The last two digits are 32, and 32 / 4 = 8, so it is also divisible by 4. The digit-sum rules come from 10 ≡ 1 (mod 9) and 10 ≡ 1 (mod 3). The rule for 4 uses 100 ≡ 0 (mod 4).

```python
n = 5832
digit_sum = sum(int(ch) for ch in str(n))
print(digit_sum, n % 3, n % 9, n % 4)  # 18 0 0 0
```

## Stop at the square root

Is 143 prime? What is the largest divisor you actually need to try, and which divisor shows that it is composite?

**Answer:** `floor(sqrt(143))` is 11, because 11² = 121 and 12² = 144. Any factor larger than 11 would be paired with a factor of 11 or less. Check 2, 3, 5, 7, and 11. The number is odd, its digit sum is 8, it does not end in 5, and it is not divisible by 7 (7 * 20 = 140). It is divisible by 11: 143 = 11 * 13. So 143 is composite, and 11 is the witness at the end of the search range.

```python
import math

n = 143
limit = math.isqrt(n)
witness = next(d for d in range(2, limit + 1) if n % d == 0)
print(limit, witness, n // witness)  # 11 11 13
```

## What the sieve still has to cross off

List every prime less than or equal to 30. After you have crossed off the multiples of 2 and of 3, which composite number in that range is still unmarked, and which prime removes it?

**Answer:** The primes are 2, 3, 5, 7, 11, 13, 17, 19, 23, and 29. Every other composite up to 30 is divisible by 2 or by 3. The exception is 25 = 5 * 5. The sieve removes it when `p = 5`, and the inner loop starts at `p * p`, which is exactly 25. The next square, 49, is already past 30, so 5 is the last prime that does any crossing-off.

```python
import math

def sieve(n: int) -> list[int]:
    is_prime = [False, False] + [True] * (n - 1)
    for p in range(2, math.isqrt(n) + 1):
        if is_prime[p]:
            for multiple in range(p * p, n + 1, p):
                is_prime[multiple] = False
    return [i for i, prime in enumerate(is_prime) if prime]

print(sieve(30))
print(25 in sieve(30), 35 > 30)  # False True
```

## Both dice, one condition

You roll two fair six-sided dice. What is the probability that both show a multiple of 3? Why is multiplying allowed here?

**Answer:** A single die shows 3 or 6, so the probability is 2/6 = 1/3. The dice are separate rolls, so they are independent and the joint probability is (1/3) * (1/3) = 1/9. Counting agrees: the four outcomes (3, 3), (3, 6), (6, 3), and (6, 6) out of 36. Multiplying would be wrong for two conditions on the *same* die, such as "even and greater than 3," because those events share one outcome and are not independent.

```python
faces = range(1, 7)
both = [(a, b) for a in faces for b in faces if a % 3 == 0 and b % 3 == 0]
print(len(both), len(both) / 36)  # 4 0.111...
print((1 / 3) * (1 / 3) == 4 / 36)  # True
```

## At least one six

Two fair dice again. What is the probability that at least one of them shows a 6? Which form of the "or" rule are you using, and why is `1/6 + 1/6` too big?

**Answer:** The events "first die is 6" and "second die is 6" overlap on double six, so they are not mutually exclusive. `P(A or B) = 1/6 + 1/6 - 1/36 = 11/36`. The complement is shorter and uses independence: the chance of no six on one die is 5/6, so `1 - (5/6)*(5/6) = 11/36`. Adding the two 1/6 figures counts (6, 6) twice.

```python
faces = range(1, 7)
hits = sum(1 for a in faces for b in faces if a == 6 or b == 6)
print(hits, hits / 36)                 # 11 0.305...
print(1 / 6 + 1 / 6 - 1 / 36 == 11 / 36)  # True
```

## Hearts are not independent of spades

You draw one card from a standard 52-card deck. Let A be "the card is a heart" and B be "the card is a spade." Are A and B mutually exclusive? Are they independent? Give `P(A and B)`, `P(A) * P(B)`, and `P(A or B)`.

**Answer:** One card has one suit, so the events are mutually exclusive and `P(A and B) = 0`. Each suit is 13/52 = 1/4, so the product is 1/16, which is not 0. They are dependent: a heart rules a spade out. `P(A or B) = 1/4 + 1/4 - 0 = 1/2`. "Cannot happen together" is a reason to add, not a reason to multiply.

```python
p_a = p_b = 13 / 52
print(0, p_a * p_b, p_a + p_b)  # 0 0.0625 0.5
print(p_a * p_b == 0)           # False, so not independent
```

## Say the assumption before the average

A campus shuttle departs every 10 minutes on a fixed schedule. You arrive at a minute chosen uniformly at random and you are not timing your walk to the timetable. What should you say out loud before computing, and what is the average wait under that model?

**Answer:** Say that you are modeling one fixed 10-minute gap, that your arrival is uniform inside it, and that you are not using a random headway. Under those assumptions the wait is uniform from 0 up to 10 minutes and the average is 5. Also say what you are not claiming: if the gap between shuttles itself varied, longer gaps would be easier to land in, and the average wait would exceed half the average gap. Naming that boundary is the point of talking first. The number 5 belongs only to the fixed-gap model.

```python
# Continuous uniform arrival over a fixed gap of T minutes: mean wait is T / 2.
gap_minutes = 10
print(gap_minutes / 2)  # 5.0
```

## The round scores

A game awards 1 point in round 1, then 2, 4, 7, and 11 in rounds 2 through 5. Find a rule, predict round 6, and check the rule on a round you did not use to invent it.

**Answer:** The jumps are +1, +2, +3, +4. Round `n` adds `n - 1` to the previous total, so the score is `1 + (0 + 1 + ... + n - 1) = 1 + n*(n - 1)/2`. Round 6 is 11 + 5 = 16. Checking round 4, which sits inside the given list but is fixed by the closed form rather than by "add the next difference" from a neighbor you already used: `1 + 4*3/2 = 7`, which matches. The first differences growing by 1 is the signature of a quadratic, the same shape as the triangular numbers.

```python
def score(n: int) -> int:
    return 1 + n * (n - 1) // 2

print([score(n) for n in range(1, 7)])  # [1, 2, 4, 7, 11, 16]
print(score(4) == 7 and score(6) == 16)  # True
```

## Nine heavier crates

Nine crates look identical. Exactly one is heavier, and a balance scale tells you which side is heavier or that they match. What is the smallest number of weighings that guarantees you find the heavy crate, and how do you split?

**Answer:** Two weighings. A scale has three outcomes, and `3^2 = 9`, so two weighings can distinguish 9 possibilities and one weighing cannot (`3^1 = 3`). Weigh three against three. The heavy crate is on the side that goes down, or in the three you set aside if the scale balances. Then weigh two of those three suspects against each other: the heavier one is the answer, or the third crate is heavier if they balance. Every path takes two weighings, so the worst case is the best case.

```python
import math

def worst_case_weighings(crates: int) -> int:
    """Ternary search: each weighing has 3 outcomes."""
    return math.ceil(math.log(crates, 3))

print(worst_case_weighings(9), 3**2 >= 9, 3**1 >= 9)  # 2 True False
```

## Twenty doors

A prize is behind exactly one of 20 doors. Each question you may ask has a yes or no answer. What is the minimum number of questions that guarantees you find the door, even if the answers are adversarial? How should each question split the remaining doors?

**Answer:** Five. A yes/no question has two outcomes, and `2^4 = 16` is less than 20 while `2^5 = 32` covers 20. Fewer than five questions cannot name every door in the worst case. Each question should split the doors that are still possible as evenly as it can, for example 10 and 10, then 5 and 5, and so on, with the last uneven splits absorbing the extra doors. The worst-case count is the depth of that splitting, which meets the bound.

```python
import math

doors = 20
print(math.ceil(math.log2(doors)))       # 5
print(2**4 >= doors, 2**5 >= doors)       # False True
```

## Bug hunt: the square-root fence

This primality test accepts 4, 9, and 25. Why, and what is the smallest change that rejects them without checking past the square root?

```python
import math

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, int(math.sqrt(n))):
        if n % d == 0:
            return False
    return True
```

**Answer:** `range` stops before its end, so a factor equal to `floor(sqrt(n))` is never tested. For 4, 9, and 25 that omitted factor is the square root itself, and no smaller divisor exists, so the function returns true. `int(math.sqrt(n))` has a second problem on large perfect squares, where the float can land just below the integer. Use `math.isqrt(n) + 1` as the exclusive stop. Also return false for `n < 2` before the loop, which this version already does; the fencepost is the remaining bug.

```python
import math

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, math.isqrt(n) + 1):
        if n % d == 0:
            return False
    return True

print([is_prime(n) for n in (1, 4, 9, 25, 49, 47)])
# [False, False, False, False, False, True]
```

## Euclid by hand

Compute `gcd(1071, 462)` with Euclid's algorithm. Write every remainder, not just the final divisor.

**Answer:** 1071 = 2 * 462 + 147, so replace the pair with (462, 147). 462 = 3 * 147 + 21, so the pair becomes (147, 21). 147 = 7 * 21 + 0, so the remainder is 0 and the divisor is 21. Each remainder is the next divisor. Factoring would also find 21 = 3 * 7, and it does more work.

```python
def gcd_trace(a: int, b: int) -> list[int]:
    steps = []
    while b:
        steps.append(a % b)
        a, b = b, a % b
    return steps

print(gcd_trace(1071, 462))  # [147, 21, 0]
```

## Divide before you multiply

What is `lcm(18, 24)`? Show an evaluation order whose largest intermediate value is the answer itself, and say why `18 * 24 / gcd` is the riskier spelling of the same identity.

**Answer:** `gcd(24, 18) = 6`, because 24 = 1 * 18 + 6 and 18 = 3 * 6 + 0. Then `lcm = 18 / 6 * 24 = 3 * 24 = 72`. The identity is `lcm * gcd = |a * b|`, so dividing first is exact for integers: 18 is divisible by the gcd. The product-first spelling computes 432 and then divides by 6. Same result, and in a fixed-width language that 432 can overflow when the divide-first form would not.

```python
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b

print(gcd(18, 24), lcm(18, 24))  # 6 72
print(18 * 24 // 6)              # 72, after a larger product
```

## Reduce, then multiply

Compute `(98 * 97) mod 17` without multiplying 98 by 97 first. Which rule lets you reduce each factor?

**Answer:** `(a * b) mod m = ((a mod m) * (b mod m)) mod m`. 98 / 17 is 5 * 17 = 85, remainder 13. 97 - 85 = 12. Then 13 * 12 = 156, and 156 - 9 * 17 = 156 - 153 = 3. So the product is 3 mod 17. Reducing does not change the congruence class; it keeps the multiply small. You still need a final reduction, because 13 * 12 is larger than 17.

```python
print(((98 % 17) * (97 % 17)) % 17)  # 3
print((98 * 97) % 17)                # 3
```

## Square up to the thirteenth power

Compute `5^13 mod 100` by successive squaring. Which powers do you actually square, and which of those squares get multiplied into the result?

**Answer:** 13 in binary is 1101, so 13 = 8 + 4 + 1. The squares mod 100 are `5^1 ≡ 5`, `5^2 ≡ 25`, `5^4 ≡ 25`, `5^8 ≡ 25`. The bits that are set are 1, 4, and 8, so the result is `5 * 25 * 25 = 3125 ≡ 25 (mod 100)`. From `5^2` upward every square ends in 25, which is why the higher powers stay at 25. That is six modular multiplications in the iterative form (three squares and three accumulations, depending how you count the first), against 12 multiplications in the naive loop. The exponent's bit length is the cost.

```python
def mod_pow(base: int, exp: int, mod: int) -> int:
    result = 1
    base %= mod
    while exp:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result

print(mod_pow(5, 13, 100))  # 25
print(pow(5, 13, 100))      # 25
```

## The midpoint that wraps

`lo = 2000000000` and `hi = 2000000010` both fit in a signed 32-bit integer. What value does a wrapping 32-bit `(lo + hi) / 2` produce, and what should you write instead?

**Answer:** The mathematical sum is 4000000010. Signed 32-bit range ends at 2147483647, and the sum mod 2^32 is 4000000010 - 4294967296 = -294967286. Dividing that by 2 yields -147483643, which is not between the endpoints. Use `lo + (hi - lo) / 2`. Here `hi - lo` is 10, half of that is 5, and the midpoint is 2000000005. The subtraction stays in range whenever `lo` and `hi` are nonnegative and in range, because the difference is at most `hi`.

```python
def add_i32(a: int, b: int) -> int:
    raw = (a + b) & 0xFFFFFFFF
    return raw - 0x100000000 if raw >= 0x80000000 else raw

lo, hi = 2_000_000_000, 2_000_000_010
print(add_i32(lo, hi) // 2)      # -147483643
print(lo + (hi - lo) // 2)       # 2000000005
```

## Three wrong labels

Three closed bins hold bolts, nuts, and a mixture of both, one bin each. Every label is wrong: the bin labeled BOLTS does not hold only bolts, the bin labeled NUTS does not hold only nuts, and the bin labeled MIXED is not mixed. You may take one item from one bin. Which bin do you sample, and how do you relabel all three from that single draw?

**Answer:** Sample the bin labeled MIXED. It is mislabeled, so it is a pure bin. Suppose the item is a bolt. That bin is BOLTS, and you relabel it. The bin labeled NUTS cannot be nuts, and it also cannot be bolts, because you just found those. So the bin labeled NUTS is MIXED. The remaining bin, labeled BOLTS, is NUTS. If the draw had been a nut, swap the two pure labels and the same chain fixes the mixed bin. Sampling a bin labeled BOLTS or NUTS cannot do this in one draw: that bin might be mixed, and one item from a mixture does not tell you which pure bin is which.

```python
def relabel(draw_from_mixed_label: str) -> dict[str, str]:
    """Return the true contents of each labeled bin after one draw."""
    if draw_from_mixed_label == "bolt":
        return {"MIXED": "BOLTS", "NUTS": "MIXED", "BOLTS": "NUTS"}
    if draw_from_mixed_label == "nut":
        return {"MIXED": "NUTS", "BOLTS": "MIXED", "NUTS": "BOLTS"}
    raise ValueError("the mixed label is not mixed")

print(relabel("bolt"))
```
