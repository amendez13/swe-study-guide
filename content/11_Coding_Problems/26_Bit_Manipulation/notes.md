# Bit Manipulation

Bit manipulation problems work on the binary form of integers: count the 1-bits of every number up to n, find the one value without a partner, swap neighbouring bits, or treat an integer as a set of flags. The operators and single-bit recipes are taught on [Bit Manipulation](#07_Data_Structures_and_Algorithms/10_Bit_Manipulation), the subset search is on [Backtracking](#11_Coding_Problems/22_Backtracking), and table-building is on [Dynamic Programming](#11_Coding_Problems/23_Dynamic_Programming). This topic is the problem set: spotting a bit problem, the six operators, masks, the lowest set bit, XOR cancellation, fixed width in Python, bitmasks as sets, counting set bits, building answers from smaller numbers, and three worked problems. The two decisions are which identity makes the problem collapse (pairs cancel, subtracting 1 flips the lowest bit, masks select positions) and whether Python's unbounded integers need a 32-bit mask.

## Key Points

- **Spotting a bit manipulation problem** — O(1) space with pairs, "32-bit unsigned", no `+`, flags, powers of two, subsets of up to about 20 items.
- **The six operators** — AND, OR, XOR, NOT, shifts; `a ^ 0 == a`, `a ^ a == 0`; `~x == -x - 1` and `>>` floors in Python; parenthesize.
- **Masks: test, set, clear, toggle** — `x & (1 << i)`, `x | (1 << i)`, `x & ~(1 << i)`, `x ^ (1 << i)`; `(1 << k) - 1` keeps the low k bits.
- **The lowest set bit** — `x & (x - 1)` removes it, `x & -x` isolates it; power of two is `x > 0 and x & (x - 1) == 0`.
- **XOR cancellation** — values seen an even number of times cancel; O(n) time, O(1) space; breaks for triples.
- **Fixed width in Python** — mask with `0xFFFFFFFF` every step, convert to signed only at the end.
- **Bitmasks as small sets** — union `|`, intersection `&`, every subset by counting 0..2ⁿ − 1; O(n · 2ⁿ).
- **Counting set bits** — shift loop O(bits), `x &= x - 1` loop O(set bits), `int.bit_count()` built in.
- **Building answers from smaller numbers** — `f(x) = f(x >> 1) + (x & 1)` or `f(x & (x - 1)) + 1`; one table pass.
- **Set-bit counts from 0 to n** — O(n) table, n + 1 entries, check against `bit_count`.
- **The one unpaired value** — XOR everything; O(n) time, O(1) space; state the "exactly twice" assumption.
- **Swap odd and even bits** — `((n & 0x55555555) << 1) | ((n & 0xAAAAAAAA) >> 1)`; O(1).
- **Bits or another tool** — bits for binary data, small sets, and pair-cancelling; hash maps for arbitrary counts.

## Example

```python
def best_disjoint_pair(words: list[str]) -> tuple[int, tuple[str, str] | None]:
    masks = []
    for word in words:
        mask = 0
        for ch in word:
            mask |= 1 << (ord(ch) - ord("a"))
        masks.append(mask)
    best, pair = 0, None
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            if masks[i] & masks[j] == 0 and len(words[i]) * len(words[j]) > best:
                best, pair = len(words[i]) * len(words[j]), (words[i], words[j])
    return best, pair


print(best_disjoint_pair(["cloud", "spark", "kiwi", "byte", "mango", "fish"]))
print(best_disjoint_pair(["ab", "ba"]), best_disjoint_pair([]))
# (25, ('cloud', 'spark'))
# (0, None) (0, None)
```

Two product names may share a label only if they have no letter in common, and the label scores the product of their lengths. Each word becomes a 26-bit mask with bit k set when the k-th letter appears, built once in O(total letters). Two words share no letter exactly when their masks AND to 0, so each pair check is O(1) instead of a set intersection, and the whole search is O(L + n²). The words are exercise values.

## More practice

Work the original exercises on the **Drills** tab. Each one names the approach, the cost, and a Python check.
