## One insight and its cost

A moderate problem has a direct solution and one structural shortcut. The shortcut is a count, an order, a window, or a formula that removes a repeated scan. You are not assembling several inventions. If the idea needs three independent tricks, it belongs with the hard problems, or you have not found the one insight yet.

Say the cost of the obvious loop, then the cost after the insight. A double loop over a few thousand items can be fine. The same loop at ten million items is the thing you replace. State the limit before you pick the tool. These cards are the tools. They are not a list of published problems.

```text
Obvious loop: O(n^2), too slow at the stated n
Insight: one pass and a map, O(n)
Edge: empty input, one element, the boundary value
```

## Bit tests and masks

A bit is a flag. Bit `i` of a badge mask means wing `i` is open. `mask & (1 << i)` tests it. `mask |= 1 << i` sets it. `mask &= ~(1 << i)` clears it. `mask & -mask` isolates the lowest set bit, which is the smallest wing number you can answer without a loop over the high bits. Use this when the input is a set of small integers packed into a word, or when the problem asks for a parity, a single differing flag, or the lowest open wing.

Do not reach for bits when the values do not fit in a word or when a set would be clearer. Say the width. Python integers grow, so a mask that was "32 flags" needs an explicit `& ((1 << 32) - 1)` if the problem promised 32 bits. The bit-manipulation topic in the data-structures section is the longer reference. Here the question is only whether a mask is the insight.

```python
def lowest_wing(mask: int) -> int:
    bit = mask & -mask
    return bit.bit_length() - 1

print(lowest_wing(0b10100))  # 2, the lowest set bit
```

## Swap without a temporary

Two variables can be exchanged with a tuple, `(a, b) = (b, a)`, which is the Python you should write. The interview version without a third name is XOR: `a ^= b; b ^= a; a ^= b`. It works because XOR is its own inverse, and only when `a` and `b` are different locations. Applied to one slot, `xs[i] ^= xs[i]` clears the slot to 0.

Use the tuple in real code. Use XOR when the prompt forbids a temporary and the two indexes might differ. Guard `i == j` before an in-place XOR swap of two slots. Addition and subtraction can swap too (`a = a + b; b = a - b; a = a - b`) and overflow in a fixed-width integer. XOR does not overflow. Neither belongs in code a teammate must read unless the constraint is real.

```python
def xor_swap(a: int, b: int) -> tuple[int, int]:
    a ^= b
    b ^= a
    a ^= b
    return a, b

print(xor_swap(3, 7))  # (7, 3)
```

## Overflow-safe arithmetic

A fixed-width integer wraps. The sum of two large indexes can overflow before you divide it by two, so the midpoint of a range becomes negative and the search walks off the array. Write `lo + (hi - lo) // 2`. The difference fits when both ends fit and `lo` is not above `hi`. The same habit applies to a product: reduce modulo `m` after each multiply, or divide out a shared factor before multiplying, instead of building a huge intermediate and hoping.

Python hides this because `int` grows. Say so, and write the expression you would use in Java when the prompt says 32-bit. A result that must fit in a 32-bit signed range is a post-condition you test with a value near `2**31 - 1`, not only with small samples. The math topic covers the midpoint in more detail. Here it is one of the edges a moderate problem hides in the constraints.

```python
def midpoint(lo: int, hi: int) -> int:
    return lo + (hi - lo) // 2

print(midpoint(2_000_000_000, 2_000_000_010))  # 2000000005
```

## Count with a map

A hash map answers "how many times has this key appeared" in expected constant time. One pass fills the map. A second look, or the same pass, answers the question: which rope length appears more than once, which jar is missing, which character count is odd. The insight is the lookup. The loop is ordinary.

Expected time is O(n). Worst-case time is O(n^2) if every key collides. Say "expected" unless you use a tree map, which is O(n log n) and ordered. A fixed array is better than a map when the key is a small integer, such as a digit 0 through 9. Do not sort a million items to count frequencies. Sorting is the tool when you next need order.

```python
def repeated(lengths: list[int]) -> list[int]:
    seen: dict[int, int] = {}
    for length in lengths:
        seen[length] = seen.get(length, 0) + 1
    return sorted(length for length, count in seen.items() if count > 1)

print(repeated([4, 2, 4, 3, 2, 2]))  # [2, 4]
```

## Two pointers

Two indexes on a sorted sequence can replace a double loop. One starts at the left, one at the right, and a rule moves exactly one of them. Packing kayaks is the shape: the heaviest remaining boat pairs with the lightest if they fit, otherwise the heaviest goes alone. Each step throws away one boat from an end, so the loop is O(n) after the sort.

The sort is the expensive part, O(n log n), and it is worth it because the later decisions are a scan. The technique needs a direction: sorted by size, by time, or by position. Without an order, two pointers do not know which side to discard. Say which pointer moves and why that discard is safe. If both can move on one rule, you will skip a pair.

```python
def trips(weights: list[int], limit: int) -> int:
    ordered = sorted(weights)
    lo, hi = 0, len(ordered) - 1
    boats = 0
    while lo <= hi:
        if ordered[lo] + ordered[hi] <= limit:
            lo += 1
        hi -= 1
        boats += 1
    return boats

print(trips([1, 2, 4, 5], 6))  # 2
```

## Sliding window

A window is a contiguous segment you maintain instead of recomputing. Add the new right end, drop the left ends that break the rule, and the segment between the pointers is the current answer. Watering hours whose total must stay under a liter budget is that shape. Each hour enters once and leaves once, so the scan is O(n).

The window works when the rule is monotone: growing the segment only makes the sum larger, so shrinking from the left restores it. A rule that is not monotone, such as "the segment contains a dip and then a rise," does not let you drop the left side safely. Then the window is the wrong insight. State the monotone reason in the interview before you write the two pointers.

```python
def longest_under(hours: list[int], limit: int) -> int:
    left = 0
    total = 0
    best = 0
    for right, amount in enumerate(hours):
        total += amount
        while total > limit and left <= right:
            total -= hours[left]
            left += 1
        best = max(best, right - left + 1)
    return best

print(longest_under([1, 2, 2, 4, 1, 1], 5))  # 3, the hours 1+2+2
```

## Prefix sums

A prefix array stores the sum of everything up to each index. The sum from `left` through `right` is `prefix[right + 1] - prefix[left]`, in constant time, after O(n) to build the prefixes. Many range questions on one array become two array lookups. One question does not need the array. A loop is clearer. Ten thousand questions do.

The empty prefix at index 0 is 0, so a range that starts at the beginning is just `prefix[right + 1]`. Off-by-one errors live in that index. Build `prefix[i + 1] = prefix[i] + value[i]` and test a range you can add by hand. A prefix of counts, rather than sums, answers "how many jars up to this day." The shape is the same.

```python
def prefix(values: list[int]) -> list[int]:
    sums = [0]
    for value in values:
        sums.append(sums[-1] + value)
    return sums

jars = prefix([2, 0, 3])
print(jars[3] - jars[1])  # days 1 through 2: 0 + 3 = 3
```

## Sort, then scan

Sorting is the insight when the next step wants neighbors. The smallest gap between crate weights is the minimum of `sorted[i + 1] - sorted[i]`, one pass after the sort. Before the sort those neighbors are not next to each other, and a double loop is the honest brute force. After the sort, any closer pair would be a contradiction.

The cost is O(n log n) for the sort plus O(n) for the scan. Say that the scan does not dominate. This is the wrong tool when you need a count of equals and not an order: use a map. It is the right tool when "the nearest other item" or "the next item that breaks a run" is the question. Keep the original indexes if the answer must point back at an unsorted position. Sort pairs of `(value, index)`, not the values alone.

```python
def smallest_gap(weights: list[int]) -> int:
    ordered = sorted(weights)
    return min(b - a for a, b in zip(ordered, ordered[1:]))

print(smallest_gap([8, 1, 5, 3]))  # 2
```

## Merge intervals

Intervals that overlap or touch can become one span. Sort by start, then walk left to right. If the next start is at or before the current end, extend the end. Otherwise the current span is finished and a new one begins. Kiln bookings `(1, 3)`, `(2, 6)`, `(8, 10)`, `(9, 12)` become `(1, 6)` and `(8, 12)`.

The sort is O(n log n). The walk is O(n). Decide whether touching endpoints merge. A booking that ends at 6 and another that starts at 6 share an instant. Say if that counts as overlap. Half-open ranges `[start, end)` make "touching" a clean `<` test and avoid the argument. Empty input is an empty list. One booking is that booking. Unsorted input is why you sort first.

```python
def merge(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    ordered = sorted(spans)
    merged: list[tuple[int, int]] = []
    for start, end in ordered:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged

print(merge([(1, 3), (2, 6), (8, 10), (9, 12)]))  # [(1, 6), (8, 12)]
```

## Simulate a small machine

Some problems are a machine with a few states and a list of events. Write the states and the legal transitions before the loop. A turnstile might be `locked`, `open`, or `alarm`. A badge moves locked to open. A pass moves open to locked. A pass while locked, or a forced gate, moves to alarm. Each event is O(1), and the whole log is O(n).

The insight is the state, not a search. If you cannot name the state in a few words, you are storing the whole history and the simulation will be wrong at the edges. Illegal events need an explicit result, not a fall-through that leaves the old state by accident. Test a log that hits every transition once, including the one that should refuse.

```python
NEXT = {
    ("locked", "badge"): "open",
    ("open", "pass"): "locked",
    ("locked", "pass"): "alarm",
    ("open", "force"): "alarm",
}

def step(state: str, event: str) -> str:
    return NEXT.get((state, event), state)
```

## Digits, not the whole number

When the question is about decimal digits, peel them off with `% 10` and `// 10`. Do not turn the number into a string unless the prompt is really about characters. A badge number has strictly increasing digits when each digit is greater than the one before it. One digit is trivially increasing. Zero is one digit. A number with a repeated digit fails.

Watch the order. Peeling from the right yields digits reversed, so compare each new digit with the previous one you peeled, or collect and reverse once. Leading zeros do not appear in an integer. If the prompt's "code" can have them, the input is a string and this technique is the wrong one. Negative inputs need a sign check before the loop.

```python
def strictly_increasing(number: int) -> bool:
    if number < 0:
        return False
    previous = 10  # larger than any digit, so the first digit passes
    while number:
        digit = number % 10
        if digit >= previous:
            return False
        previous = digit
        number //= 10
    return True

print(strictly_increasing(1359), strictly_increasing(133))  # True False
```

## Modulo and gcd

Two shortcuts show up often enough to name. `(a + b) mod m` and `(a * b) mod m` can be reduced at each step, so a fixed-width product never has to hold `a * b`. A clock position after `steps` hours is `(start + steps) % 12`. Reduce as you go when the sum itself can overflow.

The greatest common divisor is the largest piece you can cut two lengths into with nothing left over. Euclid's rule is `gcd(a, b) = gcd(b, a % b)`, and `gcd(a, 0) = a`. It is O(log min(a, b)). Two spools of 18 and 12 feet cut into 6-foot pieces. They do not cut into 9, because 9 does not divide 12. Reach for gcd when the question is "largest equal size" or "can these lengths tile." Reach for modulo when the question is a wrap, a last digit, or a product that must stay small.

```python
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

print(gcd(18, 12), (8 + 20) % 12)  # 6, clock from 8 by 20 hours is 4
```

## Estimate, then the edges

A moderate problem often hides a size. Say the size out loud before the algorithm. A million 32-bit badge ids are about 4 megabytes, so they fit in memory and a hash map is honest. A billion of them may not, and the insight changes. Powers of two are enough: `2**20` is about a million, `2**10` is about a thousand. You are checking that the plan fits, not producing a capacity plan.

Then list the edges the happy path skips. Empty input. One element. All values equal. The value that sits on the boundary of the rule, such as a window whose sum equals the limit and a window one past it. A gap function on an empty list has no answer. On one crate it has no pair. Write those two down even when the interesting case is a hundred crates. An estimate that the data fits does not answer the empty case.

```python
def badge_bytes(count: int) -> int:
    return count * 4

print(badge_bytes(1_000_000))  # 4000000, about 4 MB
```

## Check the fast path

Keep a slow version for a tiny input, or one you can compute by hand. The window, the prefix, and the merged spans should match it. A mismatch is a bug in the shortcut or an edge the slow version handled and the fast one skipped. Three or four elements are enough. Include the empty input in that check when the function claims to accept it.

The slow version is also what you say first if the shortcut is not ready. A correct O(n^2) answer, with its cost named, beats a fast idea you cannot finish. Mark the fast idea as a plan. Do not hand in half of it as if the tests had passed.
