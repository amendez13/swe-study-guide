# Bit Manipulation — Drills

Original mini-drills for reading binary, two's complement, shifts, single-bit and multi-bit masks, and classic bit tricks. Each card is one exercise: read the prompt and snippet, commit to an answer, then check it. Each Answer has a short Python solution that runs on its own. No copyrighted book text.

## Read the byte

Without a calculator, convert the byte `1011 0110` to decimal and to hex. Then write decimal 77 as an 8-bit binary string.

**Answer:** Add the place values where the bit is 1: 128 + 32 + 16 + 4 + 2 = 182. For hex, read each group of four bits as one digit: `1011` is B and `0110` is 6, so `0xB6`. For 77, peel off the largest powers of two: 64 + 8 + 4 + 1, which sets bits 6, 3, 2, and 0, giving `01001101`.

```python
b = 0b1011_0110
print(sum(1 << i for i in range(8) if b >> i & 1))  # 182
print(hex(b))                                       # 0xb6
print(f"{77:08b}")                                  # 01001101
```

## Add two bytes by hand

Add `0110 1101` and `0011 0111` column by column. Which bit positions produce a carry out, and what is the 8-bit sum?

**Answer:** Working from bit 0: 1+1 = 0 carry 1; 0+1+1 = 0 carry 1; 1+1+1 = 1 carry 1; 1+0+1 = 0 carry 1; 0+1+1 = 0 carry 1; 1+1+1 = 1 carry 1; 1+0+1 = 0 carry 1; 0+0+1 = 1. Positions 0 through 6 all carry out, and the sum is `1010 0100` (109 + 55 = 164). The carries into each column are exactly the bits where `(a + b) ^ a ^ b` is 1, which is a quick way to check your work.

```python
a, b = 0b0110_1101, 0b0011_0111
s = a + b
print(f"{s:08b}", s)                  # 10100100 164
carry_in = s ^ a ^ b                  # bit k set = a carry arrived at column k
print([k - 1 for k in range(1, 9) if carry_in >> k & 1])  # [0, 1, 2, 3, 4, 5, 6]
```

## Negative in 8 bits

What is the 8-bit two's complement pattern for -20? And what signed value does the byte `1111 0000` hold?

**Answer:** Start from +20 = `0001 0100`, flip every bit to get `1110 1011`, and add 1: `1110 1100`. For the reverse, the MSB is set so the value is negative; its weight is -128, and the remaining bits add 64 + 32 + 16 = 112, so -128 + 112 = -16. Another check: the pattern of `-k` is `256 - k`, and 256 - 20 = 236 = `1110 1100`.

```python
print(f"{-20 & 0xFF:08b}")              # 11101100
p = 0b1111_0000
print(p - 256 if p & 0x80 else p)       # -16
print(256 - 20 == 0b1110_1100)          # True
```

## Overflow wraparound

A sensor stores temperature deltas in a signed 8-bit field. It adds 100 and 50. What value does the field hold, and how can code detect that the add overflowed?

**Answer:** 150 does not fit in -128..127. The low 8 bits of 150 are `1001 0110`, which reads as 150 - 256 = -106. Signed overflow happens exactly when both inputs have the same sign and the result's sign differs; with the sign bit that test is `(a ^ r) & (b ^ r) & 0x80`.

```python
def add_i8(a: int, b: int) -> tuple[int, bool]:
    r = (a + b) & 0xFF
    overflow = bool((a ^ r) & (b ^ r) & 0x80)
    return (r - 256 if r & 0x80 else r), overflow

print(add_i8(100, 50))   # (-106, True)
print(add_i8(100, -50))  # (50, False)
print(add_i8(-100, -50)) # (106, True)
```

## Shift a negative

Treat -20 as an 8-bit value. What bits do you get after shifting right by 2 with an arithmetic shift, and with a logical shift? Which one equals -20 // 4?

**Answer:** -20 is `1110 1100`. An arithmetic shift copies the sign bit in from the left: `1111 1011`, which is -5, matching floor division. A logical shift fills with zeros: `0011 1011`, which is 59 because the value is now read as unsigned. In Python, `>>` is arithmetic, so mask to 8 bits before shifting to get the logical result.

```python
x = -20
arith = (x >> 2) & 0xFF
logical = (x & 0xFF) >> 2
print(f"{arith:08b}", x >> 2, x // 4)   # 11111011 -5 -5
print(f"{logical:08b}", logical)         # 00111011 59
```

## Bug hunt: get bit

This helper should say whether bit `i` is set. It works for bit 0 but reports False for every other set bit. Why?

```python
def is_set(n: int, i: int) -> bool:
    return n & (1 << i) == 1
```

**Answer:** `n & (1 << i)` is either 0 or the mask `1 << i` itself, so it can only equal 1 when `i` is 0. Compare against 0 instead, or shift the bit down to position 0 first so the result really is 0 or 1.

```python
def is_set(n: int, i: int) -> bool:
    return (n >> i) & 1 == 1

n = 0b1010
print([is_set(n, i) for i in range(4)])  # [False, True, False, True]
```

## Bug hunt: clear that sets

A feature-flag service turns flags off with this function. Support reports that "turning off" a flag that was already off turns it on. Find and fix the bug.

```python
def disable(flags: int, bit: int) -> int:
    return flags ^ (1 << bit)
```

**Answer:** XOR toggles, so it inverts the bit whatever its current state, and an off flag becomes on. Clearing needs AND with the inverted mask: every bit is ANDed with 1 (kept) except the target, which is ANDed with 0. The fixed version is idempotent, so calling it twice is safe.

```python
def disable(flags: int, bit: int) -> int:
    return flags & ~(1 << bit)

f = 0b0101
print(f"{disable(f, 1):04b}")              # 0101
print(f"{disable(f, 2):04b}")              # 0001
print(f"{disable(disable(f, 2), 2):04b}")  # 0001
```

## Unix permission bits

A file has mode `0o754`. Using only bitwise operators, decide whether the group may write, then grant group write and revoke "others read". Print the final mode in octal.

**Answer:** Each octal digit is three bits `rwx` for owner, group, others. Group write is bit 4 (value `0o020`), others read is bit 2 (`0o004`). `0o754` has group digit 5 = `r-x`, so group write is off. Set it with OR and clear others read with AND NOT, giving `0o770`.

```python
GROUP_W, OTHER_R = 0o020, 0o004
mode = 0o754
print(bool(mode & GROUP_W))       # False
mode |= GROUP_W
mode &= ~OTHER_R
print(oct(mode))                  # 0o770
```

## Unpack an RGB color

A color is packed as `0xRRGGBB` in one integer. Write `get_green(c)` and `set_blue(c, b)` using shifts and masks, and test them on `0x3A7FC2`.

**Answer:** Green is the middle byte, bits 8..15: shift right by 8 and keep the low 8 bits with `& 0xFF`. Blue is the low byte: clear it with `& ~0xFF` (or `& 0xFFFF00`), then OR in the new value masked to 8 bits so a bad input cannot spill into green.

```python
def get_green(c: int) -> int:
    return (c >> 8) & 0xFF

def set_blue(c: int, b: int) -> int:
    return (c & 0xFFFF00) | (b & 0xFF)

c = 0x3A7FC2
print(get_green(c))                 # 127
print(hex(set_blue(c, 0x10)))       # 0x3a7f10
print(hex(set_blue(c, 0x1FF)))      # 0x3a7fff
```

## Round to a multiple of 8

An allocator needs every block size to be a multiple of 8. Without `%` or `//`, round 77 down and 77 up to the nearest multiple of 8. Also compute 77 mod 8.

**Answer:** 8 is `2^3`, so the low three bits hold the remainder. `n & 7` is the remainder (5). Clearing those bits, `n & ~7`, rounds down to 72. To round up, add 7 first and then clear: `(n + 7) & ~7` is 80, and an exact multiple stays where it is.

```python
n = 77
print(n & 7)              # 5
print(n & ~7)             # 72
print((n + 7) & ~7)       # 80
print((64 + 7) & ~7)      # 64
```

## Next power of two

A hash table grows its capacity to a power of two. Given a requested size `n >= 1`, return the smallest power of two that is at least `n`. What do you get for 1, 5, 16, and 17?

**Answer:** `n - 1` has its highest set bit just below the target unless `n` is already a power of two, so `1 << (n - 1).bit_length()` lands on the answer. Subtracting 1 first is what keeps exact powers like 16 from doubling. In fixed-width code without `bit_length`, smear the high bit right (`x |= x >> 1`, `>> 2`, `>> 4`, ...) and add 1.

```python
def next_pow2(n: int) -> int:
    return 1 << (n - 1).bit_length()

def next_pow2_smear(n: int) -> int:
    x = n - 1
    for s in (1, 2, 4, 8, 16):
        x |= x >> s
    return x + 1

print([next_pow2(n) for n in (1, 5, 16, 17)])        # [1, 8, 16, 32]
print([next_pow2_smear(n) for n in (1, 5, 16, 17)])  # [1, 8, 16, 32]
```

## Walk a Fenwick index

In a Fenwick tree, a prefix-sum query at index `i` repeatedly does `i -= i & -i` until `i` is 0. List the indices visited for `i = 13`, and explain why the loop runs at most `log2(i) + 1` times.

**Answer:** `i & -i` isolates the lowest set bit, so each step clears exactly one 1 bit. 13 is `1101`: 13 → 12 (`1100`) → 8 (`1000`) → 0. The loop runs once per set bit, and a number below `2^k` has at most `k` set bits, so it is O(log n).

```python
def query_path(i: int) -> list[int]:
    path = []
    while i:
        path.append(i)
        i -= i & -i
    return path

print(query_path(13))     # [13, 12, 8]
print(query_path(16))     # [16]
print(len(query_path(15)), (15).bit_count())  # 4 4
```

## Parity of a word

A serial link appends a parity bit so each frame has an even number of 1s. Compute the parity bit for the 32-bit word `0xDEADBEEF` in O(log 32) operations, without looping over all 32 bits.

**Answer:** Fold the word onto itself with XOR: `x ^= x >> 16` combines the halves, then 8, 4, 2, and 1. Each fold preserves the XOR of all bits in the low part, so at the end bit 0 is the XOR of all 32 bits. `0xDEADBEEF` has 24 ones, an even count, so the parity bit is 0.

```python
def parity32(x: int) -> int:
    for s in (16, 8, 4, 2, 1):
        x ^= x >> s
    return x & 1

w = 0xDEADBEEF
print(w.bit_count(), parity32(w))   # 24 0
print(parity32(0b111))              # 1
```

## Two singles in a crowd

In a list, every value appears exactly twice except two different values that appear once each. Find both in O(n) time and O(1) extra space. Example: `[4, 9, 2, 4, 7, 2]`.

**Answer:** XOR of the whole list cancels the pairs and leaves `a ^ b`, which is nonzero because `a != b`. Any set bit of `a ^ b` is a position where `a` and `b` differ; take the lowest with `x & -x`. Split the list by that bit: each group XORs down to one of the singles, because every pair lands in the same group and cancels.

```python
from functools import reduce
from operator import xor

def two_singles(nums: list[int]) -> tuple[int, int]:
    both = reduce(xor, nums)
    bit = both & -both
    a = reduce(xor, (x for x in nums if x & bit), 0)
    return tuple(sorted((a, a ^ both)))

print(two_singles([4, 9, 2, 4, 7, 2]))  # (7, 9)
print(two_singles([1, 1, 0, 5]))        # (0, 5)
```

## Branchless abs

Compute the absolute value of a 32-bit signed integer without `if`, `abs`, or a comparison. What does your function return for -2147483648, and why?

**Answer:** `x >> 31` is 0 for non-negative values and -1 (all ones) for negatives. XOR with that mask flips the bits of a negative number, and subtracting the mask adds 1, which is exactly two's complement negation; for non-negative numbers both steps do nothing. The minimum 32-bit value has no positive counterpart in 32 bits, so the result wraps back to -2147483648.

```python
def abs_i32(x: int) -> int:
    m = x >> 31
    r = ((x ^ m) - m) & 0xFFFF_FFFF
    return r - (1 << 32) if r >> 31 else r

print(abs_i32(-42), abs_i32(42), abs_i32(0))  # 42 42 0
print(abs_i32(-2**31))                        # -2147483648
```

## Shared free days

Each person's free days are a 7-bit mask (bit 0 = Monday ... bit 6 = Sunday). Ana is free `0b1100101`, Ben `0b1010111`, and Cy `0b1110100`. Which days are all three free, how many are there, and what is the earliest one?

**Answer:** AND the masks to intersect the sets: `0b1000100`, which is bits 2 and 6, Wednesday and Sunday. The count is the popcount (2), and the earliest day is the lowest set bit, found with `m & -m` and converted to an index with `bit_length() - 1`. Union would be `|`, and "free for Ana but not Ben" would be `ana & ~ben`.

```python
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ana, ben, cy = 0b1100101, 0b1010111, 0b1110100
common = ana & ben & cy
print(f"{common:07b}", common.bit_count())               # 1000100 2
print(DAYS[(common & -common).bit_length() - 1])         # Wed
print([DAYS[i] for i in range(7) if common >> i & 1])    # ['Wed', 'Sun']
```
