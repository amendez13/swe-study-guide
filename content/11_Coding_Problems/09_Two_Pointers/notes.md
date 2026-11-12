# Two Pointers

Two pointers are two indexes that move under a rule. On a sorted or symmetric sequence, one comparison can drop a whole group of pairs. On a compaction, a reader and a writer share one pass and keep order. A staged scan finds a break first, then acts on what that scan proved. These notes are the moves and the checks. They are not a catalog of published problems.

## Key Points

- **Two pointers: what a second index buys** — an index plus a rule that says which index moves. Inward, reader and writer, and staged are the three shapes. A window and a cycle scan are neighboring patterns.
- **Inward traversal** — start at the two ends of a sorted or symmetric sequence. Move the end that cannot hold the answer. `left < right` keeps one index from pairing with itself.
- **Reader and writer on one pass** — the reader sees every slot, the writer stores what stays, and the prefix before the writer is final. Order follows the reader.
- **Staged traversal** — the first scan finds the break. The second scan uses what the first scan proved. Next arrangement is find the pivot, then swap and reverse.
- **Pair Sum in a Sorted Array (LeetCode-style: Two Sum II)** — a short sum moves the left index, a large sum moves the right index. Any one pair, or an empty result, using 0-based indexes. LeetCode 167 is 1-based and promises one pair. Negatives are legal because the array is sorted. Linear time, constant extra memory. Python's sum grows; a fixed-width sum can wrap.
- **Zero-Sum Triplets (LeetCode-style: 3Sum)** — sort, fix one value, inward-scan the complement, skip adjacent duplicates. Quadratic time. The sort is the extra list. Stop when the fixed value is positive and the target is zero.
- **Palindrome Check That Skips Punctuation (LeetCode-style: Valid Palindrome)** — skip rejected characters from both ends inside the loop. The inner loops need `left < right`. Ask about case and about ASCII versus Unicode.
- **Largest Container (LeetCode-style: Container With Most Water)** — width times the shorter height, for non-negative heights. Move the shorter side. Empty and one line are 0. One rectangle, not trapped rain over every index. A fixed-width product can wrap.
- **Shift Zeros to the End (LeetCode-style: Move Zeroes)** — swap each nonzero into the writer slot. An inward swap gathers the zeros and scrambles the rest.
- **Next Lexicographical Sequence (LeetCode-style: Next Permutation)** — rightmost ascent, rightmost strictly larger successor, reverse the suffix. No ascent means reverse the whole string. LeetCode 31 mutates an int array in place. A Python string pays for a list copy. The order is character-code order.
- **Skipping duplicates after a sort** — copies are neighbors, so uniqueness is a neighbor test. A set of tuples also deduplicates and hides the cost. The same reduction extends past three values.
- **Two pointers, a hash map, or brute force** — sorted and tight memory favors two pointers. An unsorted complement with original indexes favors a hash map. The nested loop is the baseline you name first.

## Example

```python
def pair_sum_sorted(values: list[int], target: int) -> tuple[int, int] | tuple[()]:
    left, right = 0, len(values) - 1
    while left < right:
        total = values[left] + values[right]
        if total == target:
            return (left, right)
        if total < target:
            left += 1
        else:
            right -= 1
    return ()


def shift_zeros(values: list[int]) -> list[int]:
    write = 0
    for read, value in enumerate(values):
        if value != 0:
            values[write], values[read] = values[read], values[write]
            write += 1
    return values


def is_ascii_alnum(ch: str) -> bool:
    return ("0" <= ch <= "9") or ("A" <= ch <= "Z") or ("a" <= ch <= "z")


def is_palindrome(text: str) -> bool:
    left, right = 0, len(text) - 1
    while left < right:
        while left < right and not is_ascii_alnum(text[left]):
            left += 1
        while left < right and not is_ascii_alnum(text[right]):
            right -= 1
        if left < right and text[left].lower() != text[right].lower():
            return False
        left += 1
        right -= 1
    return True


print(pair_sum_sorted([1, 3, 4, 7, 9, 12], 11))
print(shift_zeros([4, 0, 0, 2, 0, 5]))
print(is_palindrome("7, level, 7"), is_palindrome("ab!"))
# (2, 3)
# [4, 2, 5, 0, 0, 0]
# True False
```

The pair scan uses the sorted ends. The zero shift is a writer that keeps nonzero order. The phrase check skips punctuation from both ends and folds case. The lists and the phrase are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the move, the cost, and a Python check. None of them is a published problem from a book list.
