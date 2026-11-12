# Two Pointers — Drills

Original drills for the three ways of moving two indexes: inward, reader and writer, and staged. Each answer has an approach, a cost, and Python. The lists are exercise numbers, not measured data. None of these repeats the squares drill or the kayak drill.

## Pairs the scan never checks

The sorted exercise list is `[1, 4, 6, 9, 12]`, and the target is 15. An inward scan returns one pair. Which index pairs does it actually add, which index pairs does it never look at, and why is skipping them safe?

**Answer:** The scan adds `(0, 4)` as `1 + 12 = 13`, then `(1, 4)` as `4 + 12 = 16`, then `(1, 3)` as `4 + 9 = 13`, then `(2, 3)` as `6 + 9 = 15`. It returns indexes `(2, 3)`. The six pairs it never adds are `(0, 1)`, `(0, 2)`, `(0, 3)`, `(1, 2)`, `(2, 4)`, and `(3, 4)`. After `1 + 12` comes up short, index 0 is finished, because 12 is its largest possible partner. After `4 + 12` comes up high, index 4 is finished, because 4 is its smallest possible partner. After `4 + 9` comes up short, index 1 is finished the same way. A target with no pair, such as 2 on this same exercise list, returns `None`. `(0, 0)` would be the same index twice, and `left < right` never selects it. The [Two pointers: which pairs get skipped?](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) drill stops after the first move. This drill lists every pair the rest of the scan never adds. The [Two-pointer technique](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) card is the general discard. Time is O(n). Extra memory is O(1) besides the explanation you print.

```python
def trace(values: list[int], target: int) -> tuple[tuple[int, int] | None, list[tuple[int, int, int]], list[tuple[int, int]]]:
    compared: list[tuple[int, int, int]] = []
    left, right = 0, len(values) - 1
    found: tuple[int, int] | None = None
    while left < right:
        total = values[left] + values[right]
        compared.append((left, right, total))
        if total == target:
            found = (left, right)
            break
        if total < target:
            left += 1
        else:
            right -= 1
    all_pairs = [(i, j) for i in range(len(values)) for j in range(i + 1, len(values))]
    seen = {(i, j) for i, j, _total in compared}
    skipped = [pair for pair in all_pairs if pair not in seen]
    return found, compared, skipped


found, compared, skipped = trace([1, 4, 6, 9, 12], 15)
print(found)
print(compared)
print(skipped)
print(trace([1, 4, 6, 9, 12], 2)[0])
# (2, 3)
# [(0, 4, 13), (1, 4, 16), (1, 3, 13), (2, 3, 15)]
# [(0, 1), (0, 2), (0, 3), (1, 2), (2, 4), (3, 4)]
# None
```

## A skip loop that runs off the end

This check is supposed to ignore characters outside ASCII letters and digits. On the exercise string `"!!!"` it raises `IndexError`. Why, and what does the repaired check return for `"!!!"` and for `"ab!"`?

```python
def is_ascii_alnum(ch: str) -> bool:
    return ("0" <= ch <= "9") or ("A" <= ch <= "Z") or ("a" <= ch <= "z")


def broken(text: str) -> bool:
    left, right = 0, len(text) - 1
    while left < right:
        while not is_ascii_alnum(text[left]):
            left += 1
        while not is_ascii_alnum(text[right]):
            right -= 1
        if text[left].lower() != text[right].lower():
            return False
        left += 1
        right -= 1
    return True
```

**Answer:** The inner loops do not test `left < right`. On `"!!!"` the left index walks to 3 and reads past the string. The outer test cannot save it, because the crash happens inside the skip. Both inner loops need the same bound as the outer loop. With that bound, `"!!!"` is a palindrome, because no kept characters disagree, and `"ab!"` is not, because `a` and `b` disagree. The cost stays O(n) time and O(1) extra memory. The palindrome card on this topic is the full rule, including case folding and the ASCII question.

```python
def is_ascii_alnum(ch: str) -> bool:
    return ("0" <= ch <= "9") or ("A" <= ch <= "Z") or ("a" <= ch <= "z")


def broken(text: str) -> bool:
    left, right = 0, len(text) - 1
    while left < right:
        while not is_ascii_alnum(text[left]):
            left += 1
        while not is_ascii_alnum(text[right]):
            right -= 1
        if text[left].lower() != text[right].lower():
            return False
        left += 1
        right -= 1
    return True


def repaired(text: str) -> bool:
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


try:
    broken("!!!")
    broken_result = "no error"
except IndexError:
    broken_result = "IndexError"
print(broken_result, repaired("!!!"), repaired("ab!"))
# IndexError True False
```

## Collapse a sorted log in place

A sorted exercise log is `[2, 2, 2, 5, 8, 8]`. Drop repeated readings in place and return the new length. What is that length, what does the kept prefix hold, and what does the rest of the list still contain?

**Answer:** The length is 3 and the prefix is `[2, 5, 8]`. The writer starts at 1, because the first reading is always kept. The reader copies a value only when it differs from the last kept one. The tail is stale: the full list is `[2, 5, 8, 5, 8, 8]`, and only the prefix of the returned length is the answer. That leftover is the same kind of tail as the [Write pointer: what is left behind?](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) drill. The [In-place array manipulation](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) card is the pattern. An empty log returns 0. A one-element log returns 1 and leaves that element in place. Time is O(n). Extra memory is O(1). A new list of unique values is fine when the caller did not ask for in place.

```python
def collapse_sorted(values: list[int]) -> int:
    if not values:
        return 0
    write = 1
    for read in range(1, len(values)):
        if values[read] != values[write - 1]:
            values[write] = values[read]
            write += 1
    return write


data = [2, 2, 2, 5, 8, 8]
length = collapse_sorted(data)
print(length, data[:length], data)
print(collapse_sorted([]))
print(collapse_sorted([7]))
# 3 [2, 5, 8] [2, 5, 8, 5, 8, 8]
# 0
# 1
```

## Closest pair sum

The sorted exercise list is `[1, 3, 5, 8, 12]`. Which two values have a sum closest to 18, and which pair do you keep when the target is 16 and two sums are equally close?

**Answer:** For 18 the pair is 5 and 12, summing to 17. For 16 both `3 + 12 = 15` and `5 + 12 = 17` are one away from the target. Keep the first pair whose absolute difference is strictly smaller than the best so far, so 15 stays and 17 does not replace it. The scan is the inward pair search with a best-so-far. A sum under the target still moves the left index, and a sum over the target still moves the right index, because that is the move that can get closer. An exact hit can stop. The list has to be sorted. Negatives use the same moves, because the proof is the sorted order. On the exercise list `[-5, -1, 2, 4]` with target 0, the scan keeps `(-5, 4, -1)`. Fewer than two values has no pair, so the function returns `None`. A one-element list is the case that would otherwise pair a value with itself. Time is O(n) on a sorted list, or O(n log n) if you had to sort first. Extra memory is O(1) after the sort. A double loop finds the same pair and is the check on a short list. Python's sum grows. A fixed-width sum can wrap, which is the overflow note on the pair-sum card.

```python
def closest_pair(values: list[int], target: int) -> tuple[int, int, int] | None:
    if len(values) < 2:
        return None
    left, right = 0, len(values) - 1
    best = (values[left], values[right], values[left] + values[right])
    best_diff = abs(best[2] - target)
    while left < right:
        total = values[left] + values[right]
        diff = abs(total - target)
        if diff < best_diff:
            best_diff = diff
            best = (values[left], values[right], total)
        if total < target:
            left += 1
        elif total > target:
            right -= 1
        else:
            break
    return best


print(closest_pair([1, 3, 5, 8, 12], 18))
print(closest_pair([1, 3, 5, 8, 12], 16))
print(closest_pair([5], 10), closest_pair([], 0))
print(closest_pair([-5, -1, 2, 4], 0))
# (5, 12, 17)
# (3, 12, 15)
# None None
# (-5, 4, -1)
```

## Three readings closest to a target

The exercise readings are `[4, -1, 2, 7]`. Choose three of them whose sum is as close as possible to 6. What sum do you return?

**Answer:** 5, from `-1 + 2 + 4`. Sort first, then fix one reading and run the inward closest-pair scan on the suffix, keeping the best sum. This is the triplet card's shape with a different goal: a closest sum, not every unique zero triplet, so duplicate skips are unnecessary. Sorting is O(n log n) time and O(n) extra memory for `sorted`. The scans are O(n^2). An exact hit can return immediately. Fewer than three readings returns `None`. A triple loop is the check. The positive-fixed-value stop belongs to a zero target, so this scan keeps going while values remain.

```python
def three_closest(values: list[int], target: int) -> int | None:
    if len(values) < 3:
        return None
    ordered = sorted(values)
    best = ordered[0] + ordered[1] + ordered[2]
    for i in range(len(ordered)):
        left, right = i + 1, len(ordered) - 1
        while left < right:
            total = ordered[i] + ordered[left] + ordered[right]
            if abs(total - target) < abs(best - target):
                best = total
            if total < target:
                left += 1
            elif total > target:
                right -= 1
            else:
                return total
    return best


print(three_closest([4, -1, 2, 7], 6))
print(three_closest([1, 2], 0))
# 5
# None
```

## Reverse the vowels only

Reverse the vowels in the exercise string `"studio"`. Treat `a`, `e`, `i`, `o`, `u` and their capitals as vowels. Leave `y` in place. What does `"rhythm"` become, and what does `"Ae"` become?

**Answer:** `"studio"` becomes `"stodiu"`: the vowels were `u`, `i`, `o`, and they reverse to `o`, `i`, `u` while the consonants stay put. `"rhythm"` has no vowel under this rule, so it stays `"rhythm"`. `"Ae"` swaps the two ends and becomes `"eA"`, with the capitals staying on the characters that moved. The scan is inward, and each end skips non-vowels with the same `left < right` bound the punctuation check needs. An empty string and a single vowel stay as they are. Time is O(n). A Python string is immutable, so the extra memory is the character list, O(n). Swapping consonants, or treating `y` as a vowel, answers a different rule.

```python
def reverse_vowels(text: str) -> str:
    vowels = set("aeiouAEIOU")
    chars = list(text)
    left, right = 0, len(chars) - 1
    while left < right:
        while left < right and chars[left] not in vowels:
            left += 1
        while left < right and chars[right] not in vowels:
            right -= 1
        if left < right:
            chars[left], chars[right] = chars[right], chars[left]
            left += 1
            right -= 1
    return "".join(chars)


print(reverse_vowels("studio"), reverse_vowels("rhythm"), reverse_vowels("Ae"))
print([reverse_vowels(""), reverse_vowels("y"), reverse_vowels("a")])
# stodiu rhythm eA
# ['', 'y', 'a']
```

## Fill spare slots from the back

The first exercise list is `[1, 4, 7, 0, 0, 0]`. Its real prefix has length 3. The second sorted list is `[2, 5, 8]`. Merge them into the first list's spare slots. A second check is `[4, 5, 6, 0, 0]` with prefix length 3 and extra values `[1, 2]`.

**Answer:** The results are `[1, 2, 4, 5, 7, 8]` and `[1, 2, 4, 5, 6]`. Write from the last spare slot backward. Each step copies the larger of the two values that have not been placed yet. Starting at the front would overwrite a prefix value before it is read. When the extra list runs out, the leftover prefix is already in the right place, so the loop can stop. An empty extra list leaves the prefix in place. A prefix length of 0 writes the extra list from the back. Time is O(m + n). Extra memory is O(1). The slot count has to be the sum of the two lengths; a short destination writes off the end. Both inputs have to be sorted. The [Merging two sorted lists](../../07_Data_Structures_and_Algorithms/03_Linked_Lists/) card is the same advance-the-smaller-side idea on nodes, with a sentinel instead of spare slots.

```python
def merge_from_back(dest: list[int], prefix: int, extra: list[int]) -> list[int]:
    i = prefix - 1
    j = len(extra) - 1
    write = prefix + len(extra) - 1
    while j >= 0:
        if i >= 0 and dest[i] >= extra[j]:
            dest[write] = dest[i]
            i -= 1
        else:
            dest[write] = extra[j]
            j -= 1
        write -= 1
    return dest


print(merge_from_back([1, 4, 7, 0, 0, 0], 3, [2, 5, 8]))
print(merge_from_back([4, 5, 6, 0, 0], 3, [1, 2]))
print(merge_from_back([1, 2, 3], 3, []))
print(merge_from_back([0, 0, 0], 0, [1, 2, 3]))
# [1, 2, 4, 5, 7, 8]
# [1, 2, 4, 5, 6]
# [1, 2, 3]
# [1, 2, 3]
```

## Which move is it

Name the move for each exercise prompt: inward, reader-writer, staged, or hash-map.

1. A price list is sorted. Find two different prices that add to 40.
2. Drop every 0 from a list of meter readings, in place, and keep the other readings in the same order.
3. Rearrange a rack of letters into the next rack in dictionary order.
4. An unsorted list of badge prices. Report whether any two different prices add to 40, and if so, their original indexes.

**Answer:** Inward, reader-writer, staged, hash-map. The sorted pair is the inward discard. The in-place drop is a writer following a reader. The next dictionary order is a pivot scan and then a suffix scan. The unsorted pair, with original indexes, is the [Unsorted pair-sum with a hash set](../../07_Data_Structures_and_Algorithms/02_Arrays_Strings_and_Hash_Tables/) card: sorting would scramble those indexes unless you carry them along, and a hash map does not need to. A contiguous hour-budget is a different neighbor, the [Sliding window](../06_Moderate_Problems/) card, and it is not one of these four prompts.

```python
def choose(prompt: str) -> str:
    moves = {
        "sorted-pair": "inward",
        "drop-zeros": "reader-writer",
        "next-order": "staged",
        "unsorted-pair": "hash-map",
    }
    return moves[prompt]


print(choose("sorted-pair"))
print(choose("drop-zeros"))
print(choose("next-order"))
print(choose("unsorted-pair"))
# inward
# reader-writer
# staged
# hash-map
```

## Moving the taller side

The exercise heights are `[2, 7, 4, 3, 8]`. One scan always abandons the taller side (and the right side when the heights are equal). The other abandons the shorter side. What areas do they return?

**Answer:** Abandoning the taller side returns 8. Abandoning the shorter side returns 21, from the lines of height 7 and 8, three units apart. The taller line may still be the short side of a wider pair, so moving it drops a candidate the area formula has not ruled out. The shorter line cannot do better with a closer partner: the width shrinks and the height cannot rise above that shorter line. Time is O(n) either way. Extra memory is O(1). The wrong rule is still linear, and it is still wrong. Trapping rain water is a different total, water above every index, and this drill does not compute it.

```python
def area_moving_taller(heights: list[int]) -> int:
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        best = max(best, (right - left) * min(heights[left], heights[right]))
        if heights[left] > heights[right]:
            left += 1
        else:
            right -= 1
    return best


def area_moving_shorter(heights: list[int]) -> int:
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        if heights[left] <= heights[right]:
            best = max(best, (right - left) * heights[left])
            left += 1
        else:
            best = max(best, (right - left) * heights[right])
            right -= 1
    return best


print(area_moving_taller([2, 7, 4, 3, 8]), area_moving_shorter([2, 7, 4, 3, 8]))
# 8 21
```
