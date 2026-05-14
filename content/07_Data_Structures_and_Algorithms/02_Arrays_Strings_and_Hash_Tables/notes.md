# Arrays, Strings, and Hash Tables

Arrays, strings, and hash tables are the most frequently tested data structures in software engineering interviews and the most frequently used in production code. They share a common foundation: contiguous or indexed storage that gives fast access to individual elements. Mastering the patterns that operate on them (two pointers, frequency counting, hashing) eliminates a large class of problems before you even reach trees and graphs.

## Key Points

- **Fixed-size arrays give O(1) indexed access** - The address of element `i` is computed directly from the base address, but the size must be known at allocation time and cannot grow.
- **Dynamic arrays trade occasional O(N) copies for amortized O(1) append** - Doubling the capacity on resize means the expensive copy happens exponentially less often, keeping the average cost constant.
- **Two pointers turn O(N^2) into O(N)** - By advancing two indices according to a rule (toward each other, at different speeds, or from different ends), you eliminate candidate pairs without nested loops.
- **In-place manipulation avoids extra allocation** - A read pointer scans forward while a write pointer trails behind, keeping only the elements you want; O(1) extra space.
- **Matrices are arrays with coordinate math** - Rotation, zeroing, and traversal reduce to index transformations once you can confidently map `(r, c)` to its new position.
- **Strings are character arrays with immutability constraints** - Most string problems use array techniques, but repeated concatenation in Python or Java is O(N^2); use a list and join instead.
- **Frequency maps solve anagram, uniqueness, and permutation problems** - Count occurrences in a dict or fixed-size array, then compare or decrement.
- **Hash tables provide O(1) average lookup via bucket arrays and hash functions** - Keys must be hashable; collisions are handled by chaining (linked lists per bucket) or open addressing (probing).
- **Chaining vs. open addressing trades simplicity for cache locality** - Both resolve collisions with O(1) average and O(N) worst case, but open addressing keeps data in contiguous memory.
- **Balanced BSTs guarantee O(log N) with ordered iteration** - Use a tree-backed map when you need min, max, range queries, or sorted traversal that a hash table cannot provide.

## Example

```python
"""
Combined demonstration: frequency counting, hash table grouping,
two-pointer pair search, and string building.
"""
from collections import Counter, defaultdict


# 1. Frequency counting — anagram check
def is_anagram(s: str, t: str) -> bool:
    return len(s) == len(t) and Counter(s) == Counter(t)


# 2. Hash table grouping — group anagrams together
def group_anagrams(words: list[str]) -> list[list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for word in words:
        key = "".join(sorted(word))
        groups[key].append(word)
    return list(groups.values())


# 3. Two-pointer — find pair summing to target in sorted array
def two_sum_sorted(nums: list[int], target: int) -> tuple[int, int] | None:
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return (left, right)
        elif total < target:
            left += 1
        else:
            right -= 1
    return None


# 4. String builder — efficient concatenation
def build_csv_row(values: list[str]) -> str:
    parts: list[str] = []
    for v in values:
        parts.append(v)
    return ",".join(parts)


if __name__ == "__main__":
    print("anagram:", is_anagram("listen", "silent"))
    # anagram: True

    print("groups:", group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
    # groups: [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]

    print("pair:", two_sum_sorted([1, 3, 5, 7, 9, 11], 10))
    # pair: (0, 4)  -> values 1 + 9

    print("csv:", build_csv_row(["name", "age", "city"]))
    # csv: name,age,city
```

Each function above runs in O(N) time. The anagram check and grouping use hash-based frequency maps, the pair search exploits sorted order with two pointers, and the CSV builder avoids quadratic string concatenation by collecting parts in a list before joining.
