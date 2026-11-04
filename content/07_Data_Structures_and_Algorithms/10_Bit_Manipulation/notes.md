# Bit Manipulation

Bit manipulation operates directly on the binary representation of integers, using bitwise operators to inspect, set, clear, and transform individual bits. These techniques produce some of the fastest and most space-efficient solutions in computing, and they appear frequently in interviews, systems programming, embedded development, and performance-critical code paths. The core skill is translating between the problem's intent and the underlying binary structure.

## Key Points

- **Binary representation** — bit `i` is worth `2^i`; `bin()`, `int(s, 2)`, and `f"{n:08b}"` convert; one hex digit is four bits.
- **Binary arithmetic by hand** — add right to left with carries (`1+1 = 10`); subtract by adding the two's complement; `n - 1` flips the lowest 1 and the zeros below it.
- **Two's complement** — the MSB weighs `-2^(N-1)`; negate with flip-and-add-1; the N-bit pattern of `-k` is `2^N - k`; 8-bit range is -128..127.
- **Bitwise AND, OR, XOR, NOT** — AND reads or clears, OR sets, XOR toggles and cancels; Python's `~x` is `-x - 1`.
- **Left and right shift** — `x << k` multiplies by `2^k`, `x >> k` floor-divides by `2^k`; `1 << i` builds a single-bit mask.
- **Arithmetic vs logical right shift** — arithmetic copies the sign bit, logical fills zeros (`>>>` in Java/JS); Python's `>>` is arithmetic, so mask to N bits first for logical.
- **Get bit** — `(n >> i) & 1`; never compare `n & (1 << i)` to 1.
- **Set bit** — `n | (1 << i)`; idempotent.
- **Clear bit** — `n & ~(1 << i)`; XOR is not a clear.
- **Toggle bit** — `n ^ (1 << i)`; toggling twice restores the value.
- **Update bit** — clear first, then OR in `v << i`: `(n & ~(1 << i)) | (v << i)`.
- **Clear bits MSB through i** — `n & ((1 << i) - 1)` keeps the low `i` bits; equals `n % 2^i` for `n >= 0`.
- **Clear bits i through 0** — `n & (-1 << (i + 1))`; rounds down to a multiple of `2^(i+1)` (alignment).
- **Bit-range update** — build a field mask, clear with `& ~mask`, OR in `(value << lo) & mask`.
- **Isolate lowest set bit** — `n & -n`; its `bit_length() - 1` is the trailing-zero count; Fenwick trees step with `i & -i`.
- **Turn off lowest set bit** — `n & (n - 1)`; loop it to visit or count set bits; `n | (n + 1)` turns on the lowest 0.
- **Power-of-two tests** — `n > 0 and n & (n - 1) == 0`; next power of two is `1 << (n - 1).bit_length()`.
- **Counting set bits** — Kernighan's loop runs once per 1 bit; `int.bit_count()`; table `c[i] = c[i >> 1] + (i & 1)`.
- **Parity** — XOR of all bits; fold `x ^= x >> 16, 8, 4, 2, 1` for O(log width).
- **XOR properties** — `x ^ x = 0`, `x ^ 0 = x`, order-free; pairs cancel; XOR swap fails on the same location.
- **Sign bit and branchless abs** — `mask = x >> 31`, `abs = (x ^ mask) - mask`; `x ^ y < 0` means opposite signs; the 32-bit minimum has no positive abs.
- **Flags and bitmask subsets** — `|` union, `&` intersection, `a & ~b` difference; `enum.Flag` for names; count `0..2^n - 1` for all subsets, `sub = (sub - 1) & mask` for submasks.

## Example

```python
"""
Combined demonstration: binary conversion, get/set/clear bit,
power-of-two check, popcount, XOR unique finder, swap without temp.
"""


# --- Binary conversion ---
def decimal_to_binary(n: int, width: int = 8) -> str:
    """Convert a non-negative integer to a zero-padded binary string."""
    return f"{n:0{width}b}"

print(decimal_to_binary(42))        # 00101010
print(int("00101010", 2))           # 42


# --- Bit operations: get, set, clear ---
def get_bit(n: int, i: int) -> bool:
    return (n >> i) & 1 == 1

def set_bit(n: int, i: int) -> int:
    return n | (1 << i)

def clear_bit(n: int, i: int) -> int:
    return n & ~(1 << i)

n = 0b01011010  # 90
print(f"get bit 4: {get_bit(n, 4)}")       # True
print(f"set bit 0: {set_bit(n, 0):08b}")   # 01011011
print(f"clear bit 3: {clear_bit(n, 3):08b}")  # 01010010


# --- Power of two check ---
def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0

print(f"16 is power of 2: {is_power_of_two(16)}")  # True
print(f"18 is power of 2: {is_power_of_two(18)}")  # False


# --- Count set bits (Brian Kernighan) ---
def count_set_bits(n: int) -> int:
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count

print(f"set bits in 255: {count_set_bits(255)}")  # 8
print(f"set bits in 180: {count_set_bits(180)}")  # 4


# --- Find single non-duplicate via XOR ---
def find_unique(nums: list[int]) -> int:
    result = 0
    for num in nums:
        result ^= num
    return result

print(f"unique in [4,1,2,1,2]: {find_unique([4, 1, 2, 1, 2])}")  # 4


# --- Swap without temporary variable ---
def swap_no_temp(a: int, b: int) -> tuple[int, int]:
    a ^= b
    b ^= a
    a ^= b
    return a, b

x, y = swap_no_temp(10, 25)
print(f"swap(10, 25) = ({x}, {y})")  # (25, 10)
```

Every function above runs in O(1) or O(k) time where k is the number of set bits, and uses O(1) extra space. The get/set/clear operations are the fundamental building blocks, the power-of-two check and popcount use the `n & (n-1)` trick, and the unique finder exploits XOR self-cancellation. These patterns cover the core of what interviews and systems code demand from bit manipulation.

## More practice

Work the original exercises on the **Drills** tab: read each prompt, commit to an answer, then open the card to check it. For background reading, open CTCI Chapter 5 on the private reader under `#chapter-5-bit-manipulation`, with `#bit-manipulation-by-hand`, `#bit-facts-and-tricks`, `#twos-complement-and-negative-numbers`, `#arithmetic-vs-logical-right-shift`, and `#common-bit-tasks-getting-and-setting`. Do not copy book text or solutions into these study files.
