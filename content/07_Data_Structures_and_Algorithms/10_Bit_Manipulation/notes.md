# Bit Manipulation

Bit manipulation operates directly on the binary representation of integers, using bitwise operators to inspect, set, clear, and transform individual bits. These techniques produce some of the fastest and most space-efficient solutions in computing, and they appear frequently in interviews, systems programming, embedded development, and performance-critical code paths. The core skill is translating between the problem's intent and the underlying binary structure.

## Key Points

- **Integers are sequences of bits where each position is a power of 2** — The rightmost bit (bit 0) is 2^0, and each position to the left doubles the value; `bin()` and `int(s, 2)` convert between decimal and binary in Python.
- **Two's complement represents signed integers with a negative MSB weight** — For N bits, the MSB carries -2^(N-1); negation is bitwise NOT plus one; 8-bit range is -128 to +127.
- **AND masks and checks, OR sets, XOR toggles, NOT inverts** — `n & mask` isolates bits, `n | mask` turns bits on, `n ^ mask` flips bits, and `~n` inverts all bits.
- **Left shift multiplies by 2^k, right shift divides by 2^k** — `x << k` is `x * 2^k`; Python's `>>` is arithmetic (sign-preserving); `1 << i` creates a mask for bit position `i`.
- **getBit, setBit, clearBit compose every bit-level task** — `(n >> i) & 1` reads bit `i`, `n | (1 << i)` sets it, and `n & ~(1 << i)` clears it.
- **n & (n-1) clears the lowest set bit** — If the result is 0 and n > 0, then n is a power of two; this is the basis of Brian Kernighan's popcount algorithm.
- **n & (-n) isolates the lowest set bit** — Returns a value with only the lowest 1-bit of n turned on, useful in Fenwick trees and bitmask enumeration.
- **XOR cancels duplicates: x ^ x = 0, x ^ 0 = x** — XOR all elements to find the single unique value in an array of pairs; also enables swap without a temporary variable.
- **Brian Kernighan's algorithm counts set bits in O(k) time** — Repeatedly apply `n &= (n - 1)` to clear one set bit per iteration; the loop runs exactly k times where k is the popcount.
- **Bitmasks enumerate subsets: iterate 0 to 2^n - 1** — Each integer encodes which elements are included; bit i is set means item i is in the subset.

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
