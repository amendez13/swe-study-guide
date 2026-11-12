## Binary search over a search space

Binary search finds a boundary in an ordered set of candidates. It checks one candidate in the middle and discards the side that cannot hold the answer.

The candidates are not always the cells of a sorted array. They are whatever you can order so that the answer lies entirely to one side of a failed check. A printed dictionary is the familiar picture: the words are in order, you open near the middle, and the word you see tells you which half can still hold the one you want. Three tools do the same job on data a program actually stores.

`git bisect` finds a commit that introduced a bug. The git documentation describes the command as a binary search. You name a bad commit and a good commit from before the bug. On a line of history that good commit is an ancestor of the bad one. Git checks out a commit between those ends, and you mark that commit good or bad. On a straight line of history the remaining range halves. History is a graph. The candidates are the commits reachable from the bad commit, by following parent links, that are not reachable from the good commit. A merge has more than one parent, so that set is not always one line. The progress line in the documentation's own example reports 675 revisions left and roughly 10 steps. Python's `bisect` module is the array form of the same idea. `bisect_left` returns the index where a value would be inserted into an already sorted list so that the list stays sorted, to the left of any equal values. It never asks whether the value is present. It only needs the list to be ordered. PostgreSQL's `_bt_binsrch`, in `src/backend/access/nbtree/nbtsearch.c`, binary-searches the sorted keys on one B-tree page. The walk from the root to a leaf is a separate descent, one child per level. The page search is the binary search. The page numbers below are an exercise, not a measured index.

```python
import bisect

pages = [11, 14, 19, 27, 33]
print(bisect.bisect_left(pages, 19), bisect.bisect_left(pages, 20), bisect.bisect_left(pages, 10))
print(bisect.bisect_left(pages, 33), bisect.bisect_left([], 4))
# 2 3 0
# 4 0
```

19 sits at index 2. 20 is absent and would be inserted at index 3, between 19 and 27. 10 would be inserted at the front. 33 would be inserted at the end, which is index 4, one past the last page. An empty list inserts at 0. The [Binary search](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card is the iterative loop on a sorted array. This topic is the search space, the loop that keeps a boundary inside it, and the problems that are still that loop when the "array" is a range of answers.

You reach for it when the statement gives you order, or a yes/no check that flips once. The words are sorted, non-decreasing, the first index, the last index, the insertion point, the smallest value that still works, and the largest value that still works. A numeric range that is far too wide to scan, with a check you can run on one candidate, is the same signal. An unsorted array with no other structure is a linear scan. Sorting it so you can binary-search one query costs more than the scan. A predicate that flips more than once does not have a single boundary, so discarding a side throws away answers. The problems below use five shapes of that boundary. A sorted array asks for an insertion index or for the two ends of a run. A numeric range asks for the last blade that still yields enough wood, or for the first version that is bad. A rotated array is only partly sorted: one side of the midpoint still is. Two sorted arrays ask for a cut that exposes the median without a merge. A matrix is either one row-major sequence, or only sorted along each row and each column.

Each step that halves the remaining interval spends a constant amount of work to throw away about half of the candidates, so the number of steps is logarithmic in the size of the space. The iterative loop uses a constant amount of extra memory. A recursive version uses a stack proportional to the number of steps. The [Binary search](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card prefers the loop for that reason. The cost of one check is not always constant. A check that scans an array of length n, over a numeric range of size m, makes the whole search O(n log m).

**Trade-offs.** The logarithmic search needs random access to the candidates and a boundary you can defend. A linear scan needs neither, and it is the reference you run on a short input. A hash set finds an exact value in expected constant time and does not need the values to be sorted. It does not answer an insertion index, a first or last occurrence, or the smallest feasible number. Sorting once pays off when many queries hit the same array. One query does not repay that sort.

**Interview.** Say what the candidates are before you name the loop. If they are indexes, say which indexes are legal answers, including the one past the end when the problem asks for an insertion point. If they are numbers, say the lowest and highest candidates and why a feasible number stays feasible when you move in one direction. Give the cost as the number of checks times the cost of one check. Offer the linear scan as the thing you would compare against on a list of four elements.

**Recap.** Binary search discards half of an ordered candidate set after one comparison. The candidates can be array indexes, the commits reachable from a bad commit and not from a good one, or the integers in a range whose feasibility flips once. `bisect_left`, `git bisect`, and PostgreSQL's page search are that idea in a library, a history walk, and a B-tree page. The loop is logarithmic in the size of the space and uses constant extra memory when it is written with indexes rather than recursion.

## Four decisions that define the loop

Every binary search in this topic is four decisions: which candidates are still possible, which side of the midpoint is discarded, when the loop stops, and which candidate is returned.

The [Binary search](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card writes one of those loops for an exact value in a sorted array. The bugs in the family come from mixing the four decisions. A loop that includes the midpoint on the way back has to stop on a different condition from a loop that throws the midpoint away. The page numbers below are the exercise list from the previous card.

For an exact value, the four decisions are these. The search space is the closed interval of indexes `[left, right]`, starting at `0` and `n - 1`. Both updates exclude the midpoint, because a mismatch means that index is not the answer: the left edge becomes `mid + 1`, or the right edge becomes `mid - 1`. The loop stops when `left > right`, which is the test `while left <= right`. The return is the index where the values matched, or `-1` when the interval is empty. The invariant is one sentence: if the target occurs, its index is inside `[left, right]`. An empty interval means it does not occur.

```python
def find_exact(values: list[int], target: int) -> int:
    """Index of target in a sorted list, or -1. Closed interval, midpoint excluded."""
    left, right = 0, len(values) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if values[mid] == target:
            return mid
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


print(find_exact([11, 14, 19, 27, 33], 19))
print(find_exact([11, 14, 19, 27, 33], 27))
print(find_exact([11, 14, 19, 27, 33], 20))
print(find_exact([11, 14, 19, 27, 33], 11), find_exact([11, 14, 19, 27, 33], 33))
print(find_exact([], 19), find_exact([14], 14), find_exact([14], 15))
# 2
# 3
# -1
# 0 4
# -1 0 -1
```

On `[11, 14, 19, 27, 33]`, the first midpoint is index 2 and the value is 19, so that target returns immediately. A target of 27 is larger than 19, so the left edge moves to 3. The next midpoint is 3, and 27 matches. A target of 20 takes the same first step, then 27 is too large, the right edge moves to 2, and `left` is 3. The interval is empty, so the result is -1. The ends match at indexes 0 and 4. An empty list never enters the loop, because the right edge starts at -1. A one-element list either matches that element or empties the interval in one step.

The midpoint formula and the two boundary loops are the next two cards. They change the search space and the exit test. They do not change the habit of writing the four decisions down before the loop. The [Bug hunt: binary search never ends](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) drill is the case where one branch assigns an edge to `mid` and the midpoint is already that edge, so the interval does not shrink.

**Trade-offs.** The closed interval is the right shape when a match returns immediately and both misses exclude the midpoint. It cannot represent "one past the end" while `right` starts at `n - 1`, so an insertion index wants a different space. A half-open interval `[left, right)` stops on `left == right` and can use `n` as a legal answer. Mixing `while left <= right` with an update that sets an edge to `mid` is the infinite loop. Mixing `while left < right` with an update that excludes `mid` on both sides can skip the last candidate.

**Interview.** State the four decisions out loud before you write the `while`. Point at the invariant on a two-element list. Say what an empty list does, because the right edge starts at -1 and the body must not read it. If the interviewer changes the question from "where is it" to "where would it go," change the search space before you change the comparisons.

**Recap.** An exact search uses a closed interval from the first index through the last, excludes the midpoint on every miss, stops when the interval is empty, and returns the matching index or -1. The invariant is that a present target still sits inside `[left, right]`. A different question keeps the same four slots and fills them in differently. The loop is logarithmic and uses constant extra memory.

## The midpoint, overflow, and the upper midpoint

The midpoint of two indexes has to fall strictly inside the open interval, and the arithmetic that computes it has to fit in the integer type you are using.

The usual school formula adds the two ends and divides by two. In Python the add is exact, because `int` grows. In a language with fixed-width integers the add can overflow while both ends still fit. The [Overflow awareness](../01_Math_and_Logic_Puzzles/) card and the [Overflow-safe arithmetic](../06_Moderate_Problems/) card use the endpoints 2000000000 and 2000000010 for that demonstration. The endpoints here are a different exercise pair, 1500000000 and 1500000020. Both fit in a signed 32-bit integer, whose largest value is 2147483647. Their sum is 3000000020, which does not. Java wraps a signed `int` add in two's complement, and that wrapped sum is -1294967276. Dividing the wrapped value by 2 yields -647483638, which is not between the endpoints. In C and C++ the same add is undefined behavior, so those languages do not promise this wrap. `left + (right - left) // 2` subtracts first. The difference is 20, half of that is 10, and the midpoint is 1500000010. For nonnegative endpoints that themselves fit, the difference fits, and adding half of it back fits too. PostgreSQL's `_bt_binsrch` writes the midpoint as `low + (high - low) / 2`.

There is a second midpoint. `(right - left) // 2` rounds down, so on a two-index interval it returns the left index. That is the lower midpoint. The upper midpoint is `left + (right - left + 1) // 2`, which returns the right index of that same pair. You need the upper one when the update sets `left = mid`. A lower midpoint that is already `left`, followed by `left = mid`, does not shrink the interval, and the loop never ends. The [Bug hunt: binary search never ends](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) drill is that stick on a lower-bound search that assigns `lo = mid`. The pair of ends below is an exercise pair of indexes, not the overflow pair.

```python
def wrap_i32(left: int, right: int) -> int:
    raw = (left + right) & 0xFFFFFFFF
    return raw - 0x100000000 if raw >= 0x80000000 else raw


def stuck_last(values: list[int], target: int) -> int | None:
    """Lower midpoint and left = mid. Returns None when the interval stops shrinking."""
    left, right = 0, len(values) - 1
    for _ in range(4):
        if left >= right:
            return left
        mid = left + (right - left) // 2
        if values[mid] <= target:
            if mid == left:
                return None
            left = mid
        else:
            right = mid - 1
    return None


def last_at_most(values: list[int], target: int) -> int:
    """Last index whose value is <= target, or -1. Upper midpoint."""
    left, right = -1, len(values) - 1
    while left < right:
        mid = left + (right - left + 1) // 2
        if values[mid] <= target:
            left = mid
        else:
            right = mid - 1
    return left


left, right = 1_500_000_000, 1_500_000_020
print(wrap_i32(left, right), wrap_i32(left, right) // 2)
print(left + (right - left) // 2)
print(8 + (9 - 8) // 2, 8 + (9 - 8 + 1) // 2)
print(stuck_last([4, 9], 4), last_at_most([4, 9], 4))
print(last_at_most([4, 9], 3), last_at_most([4, 9], 9), last_at_most([], 1))
# -1294967276 -647483638
# 1500000010
# 8 9
# None 0
# -1 1 -1
```

The ends 8 and 9 show the bias by itself. The lower midpoint is 8. The upper midpoint is 9. On the exercise list `[4, 9]`, the last value that is at most 4 is index 0. The lower-midpoint loop sets `mid` to 0, sees that 4 is feasible, and would assign `left = 0`, which is where `left` already sits. The capped function returns `None` instead of spinning. The upper-midpoint loop moves, and it returns 0. A target of 3 is below both values, so the answer is -1. A target of 9 includes the last index. An empty list has no index and returns -1.

The `+ 1` in the upper midpoint can overflow in a fixed-width type when `right` is the largest value of that type and `left` is 0, because `right - left + 1` is one past `right`. Array indexes with a nonnegative `left` do not reach that case: the right index is at most one less than the length, and the length fits. The last-index loop in this card starts `left` at -1, so `right - left + 1` is two past the last index. A length equal to the top of a signed 32-bit integer makes that sum overflow even though every real index still fits. Deriving the last index as one before the first strictly greater value keeps both edges nonnegative. A version number that is allowed to be 2147483647, which is the top of LeetCode 278, First Bad Version, is a different overflow. The first-true loop on that problem uses the lower midpoint, `left + (right - left) // 2`, and moves `right` onto `mid`. That form does not add the extra one. The half-open end `n + 1` still does not fit in a signed 32-bit integer when `n` is that top value. The next card keeps `right` at `n` for that reason.

**Trade-offs.** The lower midpoint is the default, and it is safe whenever the branch that keeps the left side excludes `mid` by setting `left = mid + 1`. The upper midpoint is one extra addition, and it is required when the branch that keeps the left side sets `left = mid`. Using the upper midpoint with `right = mid` can skip a candidate or stick, depending on the exit test. Python hides the overflow. The expression you would write in Java is still the one to say out loud.

**Interview.** Write `left + (right - left) // 2` and say why the add of the two ends is the dangerous one. Then say which update your loop uses. If the update is `left = mid`, switch to the upper midpoint before you run a two-element example. Name the two-element case as the one you will trace, because that is where the bias becomes a single index.

**Recap.** `left + (right - left) // 2` stays inside a signed 32-bit range when the endpoints are nonnegative and in range. Adding the endpoints first can wrap, and the wrapped midpoint of 1500000000 and 1500000020 is negative. The lower midpoint of two adjacent indexes is the left one, and `left = mid` then fails to shrink. The upper midpoint is the right one, and it is the midpoint to use when a feasible `mid` becomes the new left edge.

## Lower bound and upper bound

A lower bound is the first index whose value is greater than or equal to the target. An upper bound, in the same sense as `bisect_right` and the [Lower and upper bound](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card, is the first index whose value is strictly greater than the target.

The exact-match loop returns some matching index and stops. A run of equal values has many matching indexes, and the caller often wants the ends of that run. The two bounds answer that without a second scan. `bisect_left` is the lower bound. Its documented partition is: every value before the returned index is strictly less than the target, and every value from that index on is greater than or equal to the target. `bisect_right` is the upper bound: every value before the index is less than or equal to the target, and every value from the index on is strictly greater. When the target is absent, the two indexes are equal, and that shared index is where the target would be inserted. When the target occurs, the lower bound is its first index and the upper bound is one past its last index. Their difference is the count. The last index whose value is less than or equal to the target is `bisect_right(target) - 1`, or -1 when that difference would read before the start.

Both bounds use a half-open interval `[left, right)` and the lower midpoint. The lower-bound invariant is: the answer lies in `[left, right)`, every index below `left` is strictly too small, and every index at or after `right` is large enough. It starts as `[0, n)`. The index `n` is a legal answer, and it means the target is greater than every value. PostgreSQL's `_bt_binsrch` states the same shape for a forward search on one page: slots before `low` compare below the scan key, and slots at or after `high` compare at or above it. The loop below is that invariant on an exercise list. It does not return early on an equal value. An equal value may still be the answer, so the right edge moves onto `mid` and keeps it in the interval.

```python
import bisect


def lower_bound(values: list[int], target: int) -> int:
    """First index with values[i] >= target, or len(values) if every value is smaller."""
    left, right = 0, len(values)
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left


def first_greater(values: list[int], target: int) -> int:
    """First index with values[i] > target, or len(values) if every value is smaller or equal."""
    left, right = 0, len(values)
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] <= target:
            left = mid + 1
        else:
            right = mid
    return left


def last_at_most(values: list[int], target: int) -> int:
    """Last index with values[i] <= target, or -1. This is first_greater(target) - 1."""
    left, right = -1, len(values) - 1
    while left < right:
        mid = left + (right - left + 1) // 2
        if values[mid] <= target:
            left = mid
        else:
            right = mid - 1
    return left


data = [5, 7, 7, 7, 9, 12]
print(lower_bound(data, 7), bisect.bisect_left(data, 7))
print(first_greater(data, 7), bisect.bisect_right(data, 7))
print(last_at_most(data, 7))
print(lower_bound(data, 8), last_at_most(data, 8))
print(lower_bound(data, 4), last_at_most(data, 4))
print(lower_bound(data, 13), last_at_most(data, 13))
# 1 1
# 4 4
# 3
# 4 3
# 0 -1
# 6 5
```

The first 7 is index 1, and the first value strictly above 7 is the 9 at index 4. The last 7 is index 3, one before that upper bound. The search for the lower bound sees a 7 at index 3 on its first step and does not return it. That 7 might not be the first one, so the right edge moves to 3 and the search continues. A target of 8 is absent, between 7 and 9. The lower bound is 4 and the last value at most 8 is the 7 at index 3. A target of 4 is below every value: the lower bound is 0, and there is no index at most 4. A target of 13 is above every value: the lower bound is 6, which is `len(data)`, and the last index at most 13 is 5.

The last-index loop is the one that needs the upper midpoint. Its interval is closed and includes -1, so "nothing is small enough" is a real answer. On the step where the remaining indexes are 2 and 3, the lower midpoint would be 2. The value there is 7, which is feasible, and `left = 2` would not move. The upper midpoint is 3, the value is 7, and `left` advances to the answer. `first_greater(data, 7) - 1` is the same index, and it is built from the lower-midpoint loop. Either form is fine. They must not be mixed inside one loop.

**Trade-offs.** Two logarithmic bounds replace a linear scan of a run. The scan is simpler and is the right check on a short list. A hash map counts a value in expected linear time over the whole array and does not need sorted order. It does not give you the first index. The half-open lower bound and the closed last-index loop are the same answer written from opposite ends. Keeping one of them as the template, and deriving the other by a subtraction, leaves fewer places to stick.

**Interview.** Say which bound you mean with an inequality, not only the name. "Upper bound" is the first index greater than the target on the [Lower and upper bound](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card and in `bisect_right`. A loop that returns the last index at most the target is that index minus one, and it is a different loop. Trace a run of three equal values and show that an equal midpoint is kept. Then trace a target below the first value and a target above the last.

**Recap.** `lower_bound` is the first index greater than or equal to the target, and `first_greater` is the first index strictly greater. Both use a half-open interval that starts at `[0, n)` and a lower midpoint. The last index at most the target is `first_greater - 1`, and the direct loop for that index uses an upper midpoint because it sets `left = mid`. `bisect_left` and `bisect_right` match the two half-open searches. An absent target makes the two bounds equal.

## A monotone predicate, searched for the boundary

Binary search on the answer searches a range of candidate numbers, not an array. The check is a yes/no predicate that is false on one side of a threshold and true on the other.

The [Binary search on the answer](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card and the [Binary search on answer](../../07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/) card are that recipe. This card is the direction of the flip and the loop that matches it. `git bisect` is the same predicate on a line of commits: a version is good, or it is bad, and once a version is bad every later version is bad, assuming the bug stays in the history you marked. The versions below are exercise numbers.

The first-true loop uses the half-open lower-bound shape. The invariant is that the first true candidate lies in `[left, right)`. A true midpoint might be the first one, so `right` moves onto `mid` and keeps it. A false midpoint is too small, so `left` becomes `mid + 1` and excludes it. The lower midpoint is safe, because the exclude branch steps past `mid` and the keep branch sets `right` to a midpoint that is strictly below `right`. The loop stops when `left == right`. If the predicate is true from some threshold through the end of the range, that meeting point is the threshold. If it never becomes true, the meeting point is the exclusive end you started with.

```python
def first_bad(n: int, bad_at: int) -> tuple[int, int]:
    """Smallest version in 1..n that is bad, and how many times the predicate ran."""
    calls = 0

    def is_bad(version: int) -> bool:
        nonlocal calls
        calls += 1
        return version >= bad_at

    left, right = 1, n + 1
    while left < right:
        mid = left + (right - left) // 2
        if is_bad(mid):
            right = mid
        else:
            left = mid + 1
    return left, calls


def first_bad_fits(n: int, bad_at: int) -> int:
    """Same answer with right starting at n, so n + 1 is never formed."""
    left, right = 1, n
    while left < right:
        mid = left + (right - left) // 2
        if mid >= bad_at:
            right = mid
        else:
            left = mid + 1
    return left


print(first_bad(16, 11))
print(first_bad(16, 1), first_bad(16, 16))
print(first_bad_fits(16, 11), first_bad_fits(16, 1), first_bad_fits(16, 16), first_bad_fits(1, 1))
# (11, 4)
# (1, 5) (16, 4)
# 11 1 16 1
```

Versions 1 through 16 are the space, and version 11 is the first bad one, so `is_bad` is false through 10 and true from 11 on. The first midpoint is 9, which is good, so the left edge becomes 10. The next midpoint is 13, which is bad, so the right edge becomes 13. Then 11 is bad and the right edge becomes 11. Then 10 is good and the left edge becomes 11. The edges meet at 11 after 4 calls. A bug that starts at version 1 takes 5 calls. A bug that starts at version 16 takes 4. The count depends on the answer. It stays logarithmic either way. `first_bad_fits` uses the same decisions with `right` starting at `n`, and it prints 11, 1, 16, and 1.

The opposite flip, true on the small side and false on the large side, wants the last true value. You can search for the first false with the loop above and subtract one. You can also keep `mid` by setting `left = mid`, and then the midpoint has to be the upper one or the last two candidates stick. The blade-height card is that last-true search. The feasible side has to be a single suffix or a single prefix. A predicate that is true, then false, then true again will happily discard an answer. The linear check of every candidate is how you notice.

LeetCode 278, First Bad Version, is this first-true search. There is at least one bad version, `n` can be 2147483647, and the only test you are given is the predicate. The midpoint note on the previous card is why that `n` matters in a 32-bit language: the lower midpoint does not add the extra one. The half-open end `n + 1` is a separate overflow. It does not fit in a signed 32-bit integer when `n` is 2147483647. `first_bad_fits` keeps `right` at `n` and stops when the edges meet, so the bound itself fits. It would also return `n` if every version were good, which is why it depends on the promise that a bad version exists. This function's `n` is an exercise bound, and the predicate reads a known threshold so the example can be checked. A real `isBadVersion` would be the call you are counting.

**Trade-offs.** The search costs the log of the numeric range times one predicate call, and it uses constant extra memory. Scanning the range is honest when the range is tiny and wasteful when the range is a billion. Caching a predicate that is expensive is worth it only when the same candidate is checked twice, which this loop does not do. The first-true loop and the last-true loop are the same algorithm facing opposite directions. Picking the wrong end returns a value one step off the answer, and the predicate still looks monotone.

**Interview.** Define the predicate before the range. Say which way it flips, and say the candidate you return: the first true, or the last true. Name the loop that matches that choice, including the midpoint bias. Give a one-element range and a range where the answer is the first candidate and the last candidate. If you cannot say why a larger candidate stays feasible, do not offer the search.

**Recap.** A predicate that flips once turns a range of numbers into a search space. The first true value uses the half-open lower-bound loop and a lower midpoint. The last true value is the first false minus one, or a loop that sets `left = mid` and therefore uses the upper midpoint. On versions 1 through 16 with the first bad version at 11, the loop returns 11 after 4 predicate calls. LeetCode 278 is this search, and its `n` can be the top of a signed 32-bit integer. The Python interval ends at `n + 1`. The 32-bit loop keeps `right` at `n`, because a bad version is guaranteed and `n + 1` does not fit.

## The index where a value would be inserted (LeetCode-style: Search Insert Position)

Given a sorted list of distinct numbers and a target, return the index of the target if it occurs, and otherwise return the index where it would be inserted so the list stays sorted.

That index is the lower bound: the first index whose value is greater than or equal to the target. The search space is `[0, n]`, not `[0, n - 1]`. The index `n` is a legal answer. It is the slot after the last value, and a search that cannot land there reports the last index when the target is greater than every value. The values below are exercise numbers. `bisect_left` is the same function in the standard library.

```python
import bisect


def insert_index(values: list[int], target: int) -> int:
    left, right = 0, len(values)
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left


pages = [2, 6, 10, 14, 18]
print(insert_index(pages, 10))
print(insert_index(pages, 7))
print(insert_index(pages, 1), insert_index(pages, 20))
print(insert_index([], 3), insert_index([4], 4), insert_index([4], 5))
print(bisect.bisect_left(pages, 7))
# 2
# 2
# 0 5
# 0 0 1
# 2
```

10 occurs at index 2, so the insertion index and the found index are the same while the values stay distinct. 7 is absent. The first midpoint is index 2, value 10, which is large enough, so the right edge moves to 2. The next midpoint is index 1, value 6, which is too small, so the left edge moves to 2. The edges meet at 2, in front of 10. 1 belongs at the front. 20 belongs at index 5, one past 18. An empty list returns 0. A single 4 returns 0 when the target is 4 and 1 when the target is 5. `bisect_left` agrees on 7.

The loop is O(log n) time and O(1) extra memory. A linear scan from the left finds the same index in O(n). Returning -1 when the target is absent answers a different question, the exact-match card. Initializing `right` to `n - 1` and stopping when the edges meet can still be right for a target that belongs inside the list. It cannot return `n`. The drill on that bug uses a different list.

LeetCode 35, Search Insert Position, is this index. The list contains distinct values in ascending order, the length is from 1 through 10^4, and each value and the target are from -10^4 through 10^4. This function also accepts an empty list, and on a list that happened to contain duplicates it would return the first equal index. The published problem has neither.

**Trade-offs.** The half-open lower bound is one loop and it covers a hit, a miss, and an insertion at either end. Finding any hit and then walking left to the insertion point is a linear walk hiding inside a logarithmic search. The exact-match loop is the wrong return value for a miss. `bisect_left` is the library call when the interview allows it, and the loop is what you write when it does not.

**Interview.** Say "first index greater than or equal to the target" and say that `n` is included. Trace a target larger than the last value down to the return of `n`. Mention that distinct values make a hit return the only matching index. Ask what an empty list should return before you special-case it. The contract above starts at length 1.

**Recap.** The insertion index is the lower bound on a half-open interval `[0, n)`. A present distinct target returns its index. An absent target returns the slot that keeps the list sorted, including the slot after the last value. The search is logarithmic and uses constant extra memory. LeetCode 35 promises distinct values and a length of at least 1. This function also returns 0 for an empty list.

## The first and last index of a value (LeetCode-style: Find First and Last Position of Element in Sorted Array)

Given a non-decreasing list, return the first and last indexes of a target. When the target is absent, return `[-1, -1]`.

One exact-match hit is not enough. The matching values form one contiguous run, because the list is sorted, and the answer is the two ends of that run. A linear scan from the hit out to both ends is O(n) when the whole list equals the target. Two bounds stay logarithmic. The first index is the lower bound. If that slot is past the end, or the value there is not the target, the target is absent. The last index is the upper bound minus one, the first index whose value is strictly greater than the target, stepped back by one. The list below is an exercise list.

```python
def lower_bound(values: list[int], target: int) -> int:
    left, right = 0, len(values)
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left


def first_greater(values: list[int], target: int) -> int:
    left, right = 0, len(values)
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] <= target:
            left = mid + 1
        else:
            right = mid
    return left


def first_last(values: list[int], target: int) -> list[int]:
    left = lower_bound(values, target)
    if left == len(values) or values[left] != target:
        return [-1, -1]
    return [left, first_greater(values, target) - 1]


print(first_last([4, 6, 6, 6, 8, 10], 6))
print(first_last([4, 6, 6, 6, 8, 10], 5))
print(first_last([4, 6, 6, 6, 8, 10], 4), first_last([4, 6, 6, 6, 8, 10], 10))
print(first_last([], 6), first_last([6], 6), first_last([6, 6, 6], 6))
# [1, 3]
# [-1, -1]
# [0, 0] [5, 5]
# [-1, -1] [0, 0] [0, 2]
```

The run of 6 starts at index 1 and ends at index 3. 5 is absent, between 4 and 6, so the lower bound and the first strictly greater index both land on index 1, and the value there is not 5. The single 4 at the front and the single 10 at the end are runs of length one. An empty list has no run. A single 6 is the run `[0, 0]`. Three equal values fill the whole list, `[0, 2]`. The length of a run is the last index minus the first, plus one. The run of 6 is `3 - 1 + 1`, which is 3. The full list is `2 - 0 + 1`, which is also 3. The [Lower and upper bound](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card is this pair. The count drill on that topic uses a different list of totals.

Each bound is O(log n), so the function is O(log n) time and O(1) extra memory. The absent check has to look at `values[left]` only after `left` is known to be an index. When the lower bound is `n`, the target is above every value and there is nothing to read.

LeetCode 34, Find First and Last Position of Element in Sorted Array, returns this pair. The list is non-decreasing, the length is from 0 through 10^5, and each value and the target are from -10^9 through 10^9. An empty list is inside that contract and returns `[-1, -1]`. The required time is logarithmic. A scan outward from one hit fails that bound on a list of equal values.

**Trade-offs.** Two binary searches are a small constant times `log n`, and they stay logarithmic on an all-equal list. One search plus a linear expansion is easier to write and is O(n) in that case. The direct last-index loop with an upper midpoint can replace `first_greater - 1`. Using it and then also subtracting one shifts the end of the run.

**Interview.** Say "two bounds" in the first sentence, and say what you compare at the lower bound before you index it. Trace a run of three equal values and an absent target that sits between two neighbors. A one-element hit, a one-element miss, and an empty list are the three traces that catch the off-by-one. The published length starts at 0, so the empty list is part of the contract.

**Recap.** The first index of a target is the lower bound, and the last index is one before the first strictly greater value. If the lower bound is off the list or holds a different value, the result is `[-1, -1]`. The work is two logarithmic searches and constant extra memory. LeetCode 34 allows an empty list and a run that fills the list. Expanding from one hit is linear on that run.

## The highest blade that still yields the wood

You are given the heights of standing trunks and a required amount of wood. A horizontal blade at height H cuts every trunk taller than H, and the wood you keep is the sum of `max(height - H, 0)`. Return the highest integer H that still yields at least the required amount.

A lower blade never yields less wood, because each trunk contributes the same length or a longer one. The predicate "this blade yields enough" is therefore true from the ground up through some height, and false above that height. The answer is the last true height, not the first. The [Binary search on the answer](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card is the first-true loop. This problem faces the other way. The heights and the requirement below are exercise numbers. They are not a survey of a real stand of trees.

The search space is the integer heights from 0 through the tallest trunk. A blade at the tallest trunk yields nothing. A blade above that yields nothing either, so it is the same cut. A requirement of 0 is already met by doing nothing, and the highest blade in range is the tallest trunk. A requirement greater than the sum of the heights is impossible even at height 0, and the function returns -1. An empty stand returns -1.

```python
def wood_above(heights: list[int], blade: int) -> int:
    return sum(max(height - blade, 0) for height in heights)


def highest_blade(heights: list[int], need: int) -> int:
    if not heights:
        return -1
    if need <= 0:
        return max(heights)
    if wood_above(heights, 0) < need:
        return -1
    left, right = 0, max(heights)
    while left < right:
        mid = left + (right - left + 1) // 2
        if wood_above(heights, mid) >= need:
            left = mid
        else:
            right = mid - 1
    return left


def wrap_i32(left: int, right: int) -> int:
    raw = (left + right) & 0xFFFFFFFF
    return raw - 0x100000000 if raw >= 0x80000000 else raw


def stuck_blade(heights: list[int], need: int) -> tuple[int, int, int, str] | int:
    """Lower midpoint with left = mid. Returns the pair that stops shrinking."""
    left, right = 0, max(heights)
    for _ in range(8):
        if left >= right:
            return left
        mid = left + (right - left) // 2
        if wood_above(heights, mid) >= need:
            if mid == left:
                return (left, right, mid, "stuck")
            left = mid
        else:
            right = mid - 1
    return (left, right, -1, "cap")


print(highest_blade([8, 12, 6, 15], 10))
print(wood_above([8, 12, 6, 15], 8), wood_above([8, 12, 6, 15], 9))
print(highest_blade([8, 12, 6, 15], 0), highest_blade([8, 12, 6, 15], 42), highest_blade([], 1))
print(stuck_blade([4, 9], 5), highest_blade([4, 9], 5))
print(wrap_i32(1_800_000_000, 1_800_000_000))
# 8
# 11 9
# 15 -1 -1
# (4, 5, 4, 'stuck') 4
# -694967296
```

The trunks are 8, 12, 6, and 15. Their sum is 41. A blade at 8 yields `(0 + 4 + 0 + 7)`, which is 11, still enough for 10. A blade at 9 yields 9, which is short. The loop starts on `[0, 15]` and uses the upper midpoint because a feasible blade sets `left = mid`. The first midpoint is 8, and 11 is enough, so the left edge becomes 8. The next midpoint is 12, and the wood is 3, so the right edge becomes 11. Then 10 yields 7 and the right edge becomes 9. Then 9 yields 9 and the right edge becomes 8. The edges meet at 8. A requirement of 0 returns the tallest trunk, 15. A requirement of 42 is more than 41 and returns -1. No trunks returns -1.

The lower midpoint on a last-true search sticks. On trunks `[4, 9]` and a requirement of 5, the true region ends at 4, because a blade at 4 yields exactly 5 and a blade at 5 yields 4. Once the interval is `[4, 5]`, the lower midpoint is 4, the check succeeds, and `left = 4` does not move. The capped run reports that pair. The upper-midpoint function returns 4.

Each check scans every trunk. There are M + 1 candidate heights, from 0 through the tallest trunk M, so the checks cost O(n log (M + 1)). Finding the tallest trunk is another linear pass, including when every height is 0 and the search range has one candidate. The extra memory is O(1). In Python the sum is exact. Two exercise heights of 1800000000 add to 3600000000. As a signed 32-bit add, that wraps to -694967296. A check that saw the wrapped total would treat a cut that yields plenty of wood as a negative yield and reject it. The [Overflow-safe arithmetic](../06_Moderate_Problems/) card is the same class of bug on a midpoint. Here the dangerous add is inside the predicate.

LeetCode 875, Koko Eating Bananas, is the same last-or-first feasible integer with a different predicate: the slowest integer speed that finishes every pile within a fixed number of hours. It is not this wood total. There is no LeetCode problem whose check is the sum of the lengths above a blade. Scanning every blade from the tallest trunk downward is O(n · M) and is the reference on a short range.

**Trade-offs.** The binary search is worth it when the tallest trunk is large and the scan of the trunks is the cheap part. When every height is small, walking the blades is fine and easier to test. Searching for the first blade that fails, then subtracting one, uses the lower-midpoint template from the predicate card and returns the same height. The direction is the whole bug: the first height that yields enough wood is 0 whenever 0 works, and the problem asks for the highest.

**Interview.** Say the monotone sentence first: a lower blade yields at least as much wood. Then say you want the last true height, so the midpoint is biased upward. Walk one feasible midpoint and one infeasible midpoint on a four-trunk example. Ask what to return when even the ground is short of the requirement. Mention the sum overflowing in a fixed-width language before you mention the midpoint, because the predicate is where this problem adds the large numbers.

**Recap.** The wood above a blade only shrinks as the blade rises, so the highest blade that still meets a quota is a last-true binary search. The range is 0 through the tallest trunk, the midpoint is biased upward, and each check is a linear scan. The checks cost O(n log (M + 1)), and finding the tallest trunk is a linear pass on top of that. The extra memory is constant. A requirement of 0 returns the tallest trunk. A requirement above the total, or an empty stand, returns -1. The lower midpoint sticks on the last two heights. LeetCode 875 searches a speed with a different check.

## A target in a rotated sorted array (LeetCode-style: Search in Rotated Sorted Array)

A sorted array of distinct values was cut at an unknown index and the left piece was moved to the right. Return the index of a target, or -1 when it is absent.

The whole array is no longer sorted. At every midpoint, one of the two sides still is, because there is only one cut and the values are distinct. Compare the left end with the midpoint. When `values[left] <= values[mid]`, the left side, including both of those indexes, is sorted. The target belongs there when it sits in that closed-open range, `values[left] <= target < values[mid]`. Otherwise it belongs on the right. When the left side is not the sorted one, the right side is, and the target belongs there when `values[mid] < target <= values[right]`. The [Rotated sorted array](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card is this argument. The array below is a different exercise rotation. A paper dictionary that has been cut and restacked, with the back half in front of the front half, is the same shape on a shelf.

```python
def search_rotated(values: list[int], target: int) -> int:
    left, right = 0, len(values) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if values[mid] == target:
            return mid
        if values[left] <= values[mid]:
            if values[left] <= target < values[mid]:
                right = mid - 1
            else:
                left = mid + 1
        elif values[mid] < target <= values[right]:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def search_rotated_strict(values: list[int], target: int) -> int:
    """Same loop with < instead of <= on the left end. Can miss a two-element rotation."""
    left, right = 0, len(values) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if values[mid] == target:
            return mid
        if values[left] < values[mid]:
            if values[left] <= target < values[mid]:
                right = mid - 1
            else:
                left = mid + 1
        elif values[mid] < target <= values[right]:
            left = mid + 1
        else:
            right = mid - 1
    return -1


print(search_rotated([9, 12, 15, 2, 5, 8], 5))
print(search_rotated([9, 12, 15, 2, 5, 8], 9), search_rotated([9, 12, 15, 2, 5, 8], 8))
print(search_rotated([9, 12, 15, 2, 5, 8], 7))
print(search_rotated([3, 1], 1), search_rotated_strict([3, 1], 1))
print(search_rotated([2, 3, 2, 2, 2], 3))
print(search_rotated([], 1), search_rotated([7], 7), search_rotated([7], 8))
# 4
# 0 5
# -1
# 1 -1
# -1
# -1 0 -1
```

`[9, 12, 15, 2, 5, 8]` is `[2, 5, 8, 9, 12, 15]` cut so that 9 is in front. 5 sits at index 4, on the sorted right side. 9 is the first cell. 8 is the last cell. 7 is absent. The comparison has to be `<=`. On `[3, 1]` the only midpoint of the full interval is index 0, and `values[left]` and `values[mid]` are the same cell. `3 <= 3` is true, so the left side is a one-element sorted range, the target 1 is not inside it, and the search steps right onto 1. A strict `<` says the left side is not sorted, the right-side test `3 < 1 <= 1` fails, and the search steps left off the array. It returns -1 for a value that is present.

Equal values break the "one side is sorted" test even with `<=`. `[2, 3, 2, 2, 2]` is a rotation of `[2, 2, 2, 2, 3]`. The target 3 is at index 1. The first midpoint is index 2, both ends of the left side are 2, and `2 <= 2` calls that side sorted. The side is `[2, 3, 2]`, which is not sorted, and the search walks right into the trailing 2s and returns -1. LeetCode 81, Search in Rotated Sorted Array II, allows repeated values and asks whether the logarithmic bound survives. It does not. The worst case is linear, because each equal end can force you to shrink by one index instead of by half. A linear scan is the honest fallback, and it is what catches this miss.

The distinct-value search is O(log n) time and O(1) extra memory. Every index is excluded once the side test discards it, and a match returns immediately. An empty list returns -1 without reading. A one-element list returns that index or -1.

LeetCode 33, Search in Rotated Sorted Array, is this search for distinct values. The length is from 1 through 5000, and each value and the target are from -10^4 through 10^4. The stated pivot is `1 <= k < n`: a left rotation that moves the prefix before `k` onto the end. The problem also says the array is only possibly rotated, so the unrotated array is in the contract, and this loop handles it. This function also returns -1 for an empty list, which that length excludes. The duplicate miss above is outside that contract and inside LeetCode 81.

**Trade-offs.** The side test keeps the logarithmic bound on distinct values and is wrong as soon as a duplicate can sit on both sides of the cut. A linear scan handles duplicates, empty lists, and distinct values in one loop, in O(n). Finding the minimum first, which splits the array into two sorted pieces, and then binary-searching the piece that could hold the target, is also logarithmic on distinct values and uses two loops instead of one. The [Rotated sorted array](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card notes the same duplicate fallback.

**Interview.** Say "one side of the midpoint is sorted" and write `<=`, then give `[3, 1]` as the reason the equality is there. Trace a target on the left piece and a target on the right piece of a six-element rotation. Name duplicates as the follow-up that drops the bound to linear, and show one array where the distinct loop misses. An unrotated array, a one-element array, and an absent target belong in the same trace.

**Recap.** On a rotated array of distinct values, one side of every midpoint is sorted, and the target is kept only when it falls inside that side. The left-side test is `values[left] <= values[mid]`, because the midpoint can be the left index. The search is logarithmic and uses constant extra memory. A strict `<` misses 1 in `[3, 1]`. Repeated values can make both ends equal on a side that is not sorted, and `[2, 3, 2, 2, 2]` then misses 3. LeetCode 33 requires distinct values. LeetCode 81 allows duplicates and gives up the logarithmic worst case.

## The median of two sorted arrays (LeetCode-style: Median of Two Sorted Arrays)

Return the median of the sequence you would get by merging two sorted arrays. Do it without building the merged sequence.

The median is the middle value when the total length is odd, and the average of the two middle values when the total length is even. Merging with two pointers is O(m + n) time and O(m + n) memory, and the [Merging sorted sequences](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) card is that merge. The middle is all this problem needs. Binary search the cut in the shorter array so that the left half of the merge contains half of the elements, rounded up, and every value on the left is less than or equal to every value on the right.

Put `a` on the shorter side, with length `m`, and `b` on the longer side, with length `n`. A cut `i` takes the first `i` values of `a` onto the left. The left half must hold `(m + n + 1) // 2` values, so `b` contributes `j = half - i` values. The cut is legal when the last left value of each array is less than or equal to the first right value of the other. An empty side of a cut has no value. The comparison uses negative infinity on an empty left side and positive infinity on an empty right side, which is the same idea as a neighbor that does not exist. If `a`'s left value is greater than `b`'s right value, the cut in `a` is too far right. Otherwise it is too far left. The arrays below are exercise arrays.

```python
def median_sorted(left_run: list[int], right_run: list[int]) -> float:
    if len(left_run) > len(right_run):
        left_run, right_run = right_run, left_run
    short, long = left_run, right_run
    m, n = len(short), len(long)
    if m + n == 0:
        raise ValueError("both arrays are empty")
    half = (m + n + 1) // 2
    lo, hi = 0, m
    while lo <= hi:
        i = lo + (hi - lo) // 2
        j = half - i
        a_left = short[i - 1] if i else float("-inf")
        a_right = short[i] if i < m else float("inf")
        b_left = long[j - 1] if j else float("-inf")
        b_right = long[j] if j < n else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2:
                return float(max(a_left, b_left))
            return (max(a_left, b_left) + min(a_right, b_right)) / 2
        if a_left > b_right:
            hi = i - 1
        else:
            lo = i + 1
    raise ValueError("inputs were not sorted")


print(median_sorted([2, 6, 10], [3, 7]))
print(median_sorted([2, 9], [4, 12]))
print(median_sorted([], [4, 8, 9]), median_sorted([5], []))
print(median_sorted([1, 2], [1, 2]))
print((3 + 2 + 1) // 2, (3 + 2 + 1) // 2 - 0, len([2, 6]))
# 6.0
# 6.5
# 8.0 5.0
# 1.5
# 3 3 2
```

`[2, 6, 10]` and `[3, 7]` merge to `[2, 3, 6, 7, 10]`. The length is 5, so the median is 6. The shorter array is `[3, 7]`. The left half must hold 3 values. The first midpoint takes 1 value from the short array, so the long array contributes 2. The left values are 3 and 6. The right values are 7 and 10. 3 is at most 10, and 6 is at most 7, so the cut is legal. The odd-length median is the larger left value, 6. `[2, 9]` and `[4, 12]` merge to `[2, 4, 9, 12]`, and the two middle values average to 6.5. An empty array beside `[4, 8, 9]` leaves the median of that array, 8. A single 5 beside an empty array is 5. Two copies of `[1, 2]` merge to `[1, 1, 2, 2]`, and the average of the middle pair is 1.5. The swap is part of the correctness of this loop. The left half holds `(m + n + 1) // 2` values. For the exercise arrays `[1, 4, 8]` and `[2, 6]` that number is 3. A cut of 0 on the longer array sets the partner index to 3, and the shorter array only has indexes 0 and 1. The printed row is the left-half size 3, the partner index 3, and the shorter length 2. The swap searches `[2, 6]`. Its cuts leave the partner inside `[1, 4, 8]`. A search that stays on the longer array has to limit the cut to indexes with a legal partner, and that limited search costs the log of the longer length. This function swaps instead.

The time is O(log(min(m, n))) and the extra memory is O(1), apart from the infinity sentinels, which are two constants. The merged baseline is O(m + n). In Python the average is exact for these integers. In a fixed-width language, adding the two middle values before dividing can overflow. Half the difference, added back to the smaller one, stays in range for the same reason the midpoint does.

LeetCode 4, Median of Two Sorted Arrays, asks for this median and states an O(log(m + n)) bound, which the shorter-array search satisfies. Each length is from 0 through 1000, the total length is from 1 through 2000, and the values are from -10^6 through 10^6. Either array may be empty. Both empty is outside that contract, and this function raises `ValueError` for it. The published samples use a different pair of arrays. The odd result here is the float 6.0, which matches a numeric median rather than an index.

**Trade-offs.** The cut search is the logarithmic answer and it is easy to get the empty side wrong. The merge is the baseline a reviewer can recompute by hand, and it is the right code when the arrays are short or the caller needs the merged sequence anyway. A limited search of the longer array wastes comparisons and still passes a logarithmic requirement written as `log(m + n)`. Quickselect on the concatenation is expected linear time and does not use the fact that each array is already sorted.

**Interview.** Say "cut the shorter array" first. Draw the left half's size, including the `+ 1` that puts the odd median on the left. Then name the two comparisons, and say what infinity stands in for. Walk one odd total and one even total. An empty array beside a non-empty array is the case that forces the sentinel. State the merge as the O(m + n) baseline before you claim the log.

**Recap.** The median of two sorted arrays is the middle of the merge, found by binary-searching a cut in the shorter array. The left half holds `(m + n + 1) // 2` values, and the cut is legal when each left edge is at most the other array's right edge. An empty side of the cut compares as infinity. The search is O(log(min(m, n))) time and constant extra memory. LeetCode 4 allows either array to be empty and requires a logarithmic bound. The merge is the linear baseline.

## A matrix sorted in row-major order (LeetCode-style: Search a 2D Matrix)

Each row of the matrix is sorted, and the first value of each row is greater than the last value of the row above. Decide whether a target occurs.

Those two promises make the row-major order one sorted sequence. NumPy stores a matrix in C order by default, one full row after the previous row, so the cell at flat index `i` in a matrix with `cols` columns is row `i // cols` and column `i % cols`. Binary search the flat indexes from 0 through `rows * cols - 1` and read the cell through that mapping. The width in the division is the column count, not the row count. The matrix below is an exercise matrix.

```python
def search_matrix(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    rows, cols = len(matrix), len(matrix[0])
    left, right = 0, rows * cols - 1
    while left <= right:
        mid = left + (right - left) // 2
        value = matrix[mid // cols][mid % cols]
        if value == target:
            return True
        if value < target:
            left = mid + 1
        else:
            right = mid - 1
    return False


def search_matrix_stride(matrix: list[list[int]], target: int, stride: int) -> bool | str:
    rows, cols = len(matrix), len(matrix[0])
    left, right = 0, rows * cols - 1
    while left <= right:
        mid = left + (right - left) // 2
        row, col = divmod(mid, stride)
        if row >= rows or col >= cols:
            return "off"
        value = matrix[row][col]
        if value == target:
            return True
        if value < target:
            left = mid + 1
        else:
            right = mid - 1
    return False


matrix = [
    [2, 4, 6, 8],
    [10, 12, 14, 16],
    [18, 20, 22, 24],
]
print(search_matrix(matrix, 16), search_matrix(matrix, 15))
print(search_matrix(matrix, 2), search_matrix(matrix, 24))
print(search_matrix_stride(matrix, 16, 3))
print(search_matrix_stride(matrix, 24, 3))
print(divmod(7, 4), divmod(7, 3))
# True False
# True True
# False
# off
# (1, 3) (2, 1)
```

16 is present. Its flat index is 7, because the first row holds indexes 0 through 3 and the second row holds 4 through 7. `7 // 4` is row 1 and `7 % 4` is column 3. 15 is absent, between 14 and 16. 2 is the first cell. 24 is the last. Using the row count, 3, as the stride searches a different order. That search reports 16 as absent. The formula itself maps index 7 through a stride of 3 to row 2, column 1, which holds 20, not 16. The same stride maps flat indexes 9, 10, and 11 onto row 3, and this matrix only has rows 0, 1, and 2. Searching for 24 walks onto one of those indexes, and the guarded read returns `"off"` instead of raising `IndexError`.

The search is O(log(rows * cols)) time and O(1) extra memory. There are `rows * cols` cells, and each step throws away half of the remaining flat indexes.

A matrix can be sorted along every row and every column without being sorted in row-major order. A multiplication table is that object: each row increases, each column increases, and the next row starts again near the small values. The exercise matrix below has the same shape. Flattening it and binary-searching the flat list misses 8, which is present at row 1, column 2. The flat list is `[1, 4, 7, 2, 5, 8, 3, 6, 9]`. The first midpoint is index 4, value 5. 5 is less than 8, so the left edge moves to 5. Index 5 holds 8, and it is still inside the interval. The next midpoint is index 6, value 3, which is also less than 8, so the left edge moves to 7 and index 5 is discarded. The 8 sat to the left of a smaller value. The remaining midpoints are index 7, value 6, and index 8, value 9. The list is not sorted, so a smaller midpoint does not mean the target is to its right.

The repair for that weaker promise is a staircase walk, not a binary search. Start at the top-right cell. A cell larger than the target cannot hide the target below it, because the column is sorted, so step left. A cell smaller than the target cannot hide the target to its left, because the row is sorted, so step down. Each step discards a row or a column. The walk is O(rows + cols). On this matrix the top-right cell is 7, which is smaller than 8, so the walk steps down onto 8.

```python
def flatten_search(matrix: list[list[int]], target: int) -> int:
    flat = [value for row in matrix for value in row]
    left, right = 0, len(flat) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if flat[mid] == target:
            return mid
        if flat[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def staircase(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    row, col = 0, len(matrix[0]) - 1
    while row < len(matrix) and col >= 0:
        value = matrix[row][col]
        if value == target:
            return True
        if value > target:
            col -= 1
        else:
            row += 1
    return False


stairs = [
    [1, 4, 7],
    [2, 5, 8],
    [3, 6, 9],
]
print(flatten_search(stairs, 8), staircase(stairs, 8), staircase(stairs, 10))
# -1 True False
```

LeetCode 74, Search a 2D Matrix, is the row-major search. Both dimensions are from 1 through 100, and each value and the target are from -10^4 through 10^4. Each row is sorted non-decreasing, and the first value of a row is greater than the last value of the row above. This function also returns false for an empty matrix, which is outside that contract. LeetCode 240, Search a 2D Matrix II, is the row-and-column promise only. The staircase is the linear walk for that problem. A flattened binary search does not implement it.

**Trade-offs.** The flat binary search is logarithmic in the number of cells and needs the global order. The staircase is linear in the sum of the dimensions and survives when each row starts below the end of the row above. A scan of every cell is the reference for both. Mixing up the stride is a silent wrong answer on a rectangle and an `IndexError` when the computed row or column falls off the matrix.

**Interview.** Say which promise you heard. "The next row starts after the previous row ends" is the flat search, and the stride is the column count. "Rows and columns are each sorted" is the staircase. Trace index 7 on a 3 by 4 matrix through both strides. On the staircase, say why a too-large top-right cell lets you discard the column.

**Recap.** A matrix whose rows are sorted, and whose next row starts strictly above the previous row's end, is one sorted sequence in row-major order. Flat index `i` is row `i // cols` and column `i % cols`, and the search is logarithmic in the number of cells. Using the row count as the stride reports 16 absent on the exercise matrix and maps index 7 to a different cell. When only rows and columns are sorted, the flattened list is not sorted, the flat search misses 8, and a top-right staircase walk finds it in O(rows + cols). LeetCode 74 is the flat search. LeetCode 240 is the staircase.

## Any index that is a local peak (LeetCode-style: Find Peak Element)

Return any index whose value is strictly greater than both of its neighbors. A neighbor that would fall off the array counts as smaller than every value, so an endpoint can be a peak, and a one-element array is a peak.

The array does not have to be sorted. Adjacent values are distinct, which is what makes "greater than the neighbor" a direction rather than a tie. If the midpoint is strictly less than the next value, the slope rises to the right. A peak exists on that side: walking uphill reaches a value whose next neighbor is smaller, or it reaches the end, whose outside neighbor counts as smaller. The search keeps the right side, including the next index, and discards the midpoint. If the midpoint is greater than the next value, a peak exists at the midpoint or to its left. The maximum of that side is a peak, because the values differ from their neighbors and the right edge of this side steps down. The search keeps the midpoint and discards the right side. The lower midpoint is the one this loop needs, because the rising branch sets `left = mid + 1` and the falling branch sets `right = mid`. The elevations below are exercise numbers.

```python
def find_peak(values: list[int]) -> int:
    left, right = 0, len(values) - 1
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] < values[mid + 1]:
            left = mid + 1
        else:
            right = mid
    return left


print(find_peak([2, 6, 8, 5, 1]))
print(find_peak([7, 4, 3]), find_peak([1, 4, 9]), find_peak([1]))
print(find_peak([1, 3]), find_peak([5, 2]))
print(find_peak([1, 3, 2, 4, 1]))
# 2
# 0 2 0
# 1 0
# 3
```

On `[2, 6, 8, 5, 1]` the first midpoint is index 2, value 8, and the next value is 5. The slope falls, so the right edge becomes 2 and indexes 3 and 4 are discarded. A peak remains inside `[0, 2]`: the 8 is still there. The next midpoint is index 1, value 6, and the next value is 8. The slope rises, so the left edge becomes 2. Index 2 is the only one left, and 8 is greater than 6 and greater than 5. A strictly decreasing list peaks at the first index. A strictly increasing list peaks at the last index. One element peaks at 0. Two elements peak on the larger one, index 1 for `[1, 3]` and index 0 for `[5, 2]`. `[1, 3, 2, 4, 1]` has peaks at indexes 1 and 3. The loop returns 3. Any peak satisfies the contract.

Comparing the midpoint with `mid - 1` reads off the front when `mid` is 0. This loop never does that. It compares with `mid + 1`, and `left < right` keeps `mid` from being the last index, so `mid + 1` is always a real cell. The time is O(log n) and the extra memory is O(1). A linear scan that returns the first index greater than its right neighbor is also correct, and it is O(n). It is the reference that checks the returned index is a peak, including at the ends.

LeetCode 162, Find Peak Element, returns any peak index. The length is from 1 through 1000, adjacent values differ, values fit in a signed 32-bit integer, and the neighbors off the ends are treated as negative infinity. The required time is logarithmic. An empty array is outside that contract. This function assumes the adjacent values differ. On a plateau, `values[mid] < values[mid + 1]` is false, so the loop would step left and could settle on an equal neighbor, which is not a strict peak.

**Trade-offs.** The slope search is logarithmic and returns one peak, not every peak. The linear scan finds the same kind of index and is easier to prove on a whiteboard. Asking for the global maximum is a different problem. The global maximum is a peak, and finding it is a linear scan even with the distinct-neighbor promise. The binary search does not locate it in particular.

**Interview.** Say the outside neighbor counts as smaller, so an endpoint qualifies. Then say the rule: a rise keeps the right side, a fall keeps the midpoint and the left side. Trace `[2, 6, 8, 5, 1]` and name the indexes you discard. A one-element array, a strictly increasing array, and a strictly decreasing array are the three edges. Mention that two peaks make either index legal, and that equal neighbors are outside the contract.

**Recap.** A local peak is a value greater than both neighbors, and the ends are compared with an imaginary smaller neighbor. If the midpoint is below the next value, a peak remains to the right. Otherwise a peak remains at the midpoint or to the left. The loop uses a lower midpoint, runs in logarithmic time, and uses constant extra memory. It returns one valid peak when several exist. LeetCode 162 requires distinct neighbors and a length of at least 1.

## A pick whose chance follows the weight (LeetCode-style: Random Pick with Weight)

Build a picker that returns index `i` with probability proportional to `weights[i]`, and that can answer many picks after one setup.

A linear scan on every pick walks the weights until the running total passes the draw. That is O(n) per pick. The weights do not change between picks, so the setup can build the prefix totals once. The prefix array is sorted, because the weights are nonnegative and a prefix only grows. A draw is then a lower bound on that prefix. The [Prefix sums](../06_Moderate_Problems/) card is the array. This card is the draw and the binary search. The weights below are exercise weights.

CPython 3.12's `random.choices` does the same job with a different boundary. It builds the cumulative weights, converts the total to a float, and draws `random() * total`, a float in `[0, total)`. It then calls `bisect` on that cumulative list with the right edge set to `n - 1`, so the search slice excludes the last cumulative entry and a draw past the earlier entries lands on the last index instead of off the list. A non-positive total raises `ValueError`. The integer version here avoids the float. Draw an integer uniformly from 1 through the total, inclusive, and return the first prefix that is greater than or equal to that draw.

```python
class WeightedPicker:
    def __init__(self, weights: list[int]) -> None:
        self.prefix: list[int] = []
        total = 0
        for weight in weights:
            total += weight
            self.prefix.append(total)
        self.total = total

    def index_for(self, draw: int) -> int:
        """First prefix >= draw. draw is in 1..total when the total is positive."""
        left, right = 0, len(self.prefix)
        while left < right:
            mid = left + (right - left) // 2
            if self.prefix[mid] < draw:
                left = mid + 1
            else:
                right = mid
        return left


picker = WeightedPicker([4, 1, 5])
print(picker.prefix)
print([picker.index_for(draw) for draw in range(1, 11)])
print([picker.index_for(draw) for draw in range(0, 10)])
print(WeightedPicker([4, 0, 1]).index_for(5), WeightedPicker([0, 0]).total)
# [4, 5, 10]
# [0, 0, 0, 0, 1, 2, 2, 2, 2, 2]
# [0, 0, 0, 0, 0, 1, 2, 2, 2, 2]
# 2 0
```

The prefix of `[4, 1, 5]` is `[4, 5, 10]`. Draws 1 through 4 land on index 0, draw 5 lands on index 1, and draws 6 through 10 land on index 2. That is 4, 1, and 5 outcomes out of 10, matching the weights. Drawing from 0 through 9 and using the same "first prefix greater than or equal to the draw" comparison shifts the buckets. Draw 0 has no positive prefix beneath it, so it lands on index 0, and draw 9 still lands on index 2. The ten outcomes are then 5, 1, and 4. The first weight stole the outcome that belonged to the last weight. A zero weight does not advance the prefix. On `[4, 0, 1]` the prefix is `[4, 4, 5]`, and draw 5 lands on index 2, so the zero in the middle is never chosen. A total of 0 is not a range of draws. The constructor records 0, and the caller has to refuse the pick. `random.choices` raises on that total.

The constructor is O(n) time and O(n) extra memory. Each pick is O(log n) time and O(1) extra memory. An alias table is the other setup: linear time to build, then a constant-time draw. It is the better tool when the number of picks is large enough that the log factor dominates, and it is more machinery than this problem needs. A float draw times the total can round onto a boundary or onto a value the last prefix does not cover. The integer range 1 through the total, paired with the lower bound, gives each weight exactly its own count of draws.

LeetCode 528, Random Pick with Weight, is this picker. The length is from 1 through 10^4, each weight is from 1 through 10^5, and `pickIndex` is called at most 10^4 times. Every weight is positive, so a zero weight and a total of 0 are outside that contract. The published examples use a different weight list, and because the pick is random the checker accepts any sequence with the right frequencies. The lists printed here are the deterministic map of every integer draw, not one random sample.

**Trade-offs.** Prefix sums plus a lower bound are easy to test, because every draw from 1 through the total has one expected index. The linear scan per pick is the reference that checks those indexes, and it is the right implementation for a handful of picks. The alias table wins on the pick cost and loses on how much setup you have to explain. The library's float draw is a different boundary, capped so the index stays on the list. Copying `random() * total` into the integer lower bound is the off-by-one above.

**Interview.** Build the prefix on the board and mark the range of draws for each index before you write the search. Say the draw is the inclusive range 1 through the total, and the search is the first prefix greater than or equal to the draw. Show the 0-through-total-minus-one map as the bug, with the stolen count. A zero weight and a zero total are the contract questions. LeetCode 528 excludes both by requiring positive weights.

**Recap.** Prefix totals turn a weighted pick into a lower bound on a sorted array. An integer draw from 1 through the total hits index `i` for exactly `weights[i]` values of the draw. Drawing from 0 through the total minus one, with the same comparison, moves one outcome from the last weight onto the first. Setup is linear. Each pick is logarithmic. A zero weight is skipped. A zero total is not a draw. LeetCode 528 uses positive weights only. CPython 3.12's `random.choices` uses a float draw and a capped `bisect` instead of this integer range.

## What to run before you trust the loop

A binary search is finished when its four decisions survive the short inputs that make an interval one or two candidates wide, and when a linear scan agrees with it on those inputs.

The loops in this topic fail by returning an adjacent index, by refusing to shrink, or by discarding the side that holds the answer. A long random list hides all three, because most steps have a wide interval and the midpoint sits comfortably inside it. The inputs that expose them are small on purpose. Run an empty list wherever the contract allows one. Run one element, both as a hit and as a miss. Run two elements, including the order that makes the midpoint equal the left index. Run a list whose values are all equal. Run a target below the first value, a target above the last value, and a target that sits between two neighbors. Run a target at each end. For a rotated array, run every cut of one short sorted list, including the cut that leaves the list in order. Compare a bound with `bisect_left` or `bisect_right` on the same list. The page list and the rotation below are exercise inputs.

```python
import bisect


def lower_bound(values: list[int], target: int) -> int:
    left, right = 0, len(values)
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left


def last_at_most(values: list[int], target: int) -> int:
    left, right = -1, len(values) - 1
    while left < right:
        mid = left + (right - left + 1) // 2
        if values[mid] <= target:
            left = mid
        else:
            right = mid - 1
    return left


def search_rotated(values: list[int], target: int) -> int:
    left, right = 0, len(values) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if values[mid] == target:
            return mid
        if values[left] <= values[mid]:
            if values[left] <= target < values[mid]:
                right = mid - 1
            else:
                left = mid + 1
        elif values[mid] < target <= values[right]:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def find_min_rotated(values: list[int]) -> int:
    left, right = 0, len(values) - 1
    while left < right:
        mid = left + (right - left) // 2
        if values[mid] > values[right]:
            left = mid + 1
        else:
            right = mid
    return values[left]


def mismatches() -> int:
    bad = 0
    groups = [[], [4], [4, 9], [4, 4, 4], [1, 4, 4, 9]]
    targets = [-1, 0, 1, 4, 5, 9, 10]
    for values in groups:
        for target in targets:
            if lower_bound(values, target) != bisect.bisect_left(values, target):
                bad += 1
            if last_at_most(values, target) != bisect.bisect_right(values, target) - 1:
                bad += 1
    base = [10, 20, 30, 40]
    for shift in range(len(base)):
        rotated = base[shift:] + base[:shift]
        for target in base + [0, 25, 50]:
            found = search_rotated(rotated, target)
            if target in rotated:
                bad += found < 0 or rotated[found] != target
            else:
                bad += found != -1
            bad += find_min_rotated(rotated) != min(base)
    return bad


print(mismatches())
print(lower_bound([], 4), lower_bound([4], 4), lower_bound([4], 5))
print(lower_bound([1, 4, 4, 9], 0), lower_bound([1, 4, 4, 9], 5), lower_bound([1, 4, 4, 9], 10))
print(last_at_most([4, 4, 4], 4), search_rotated([30, 10, 20], 10), find_min_rotated([30, 10, 20]))
# 0
# 0 0 1
# 0 3 4
# 2 1 10
```

The checker compares the lower bound with `bisect_left` and the last-at-most index with `bisect_right - 1` on an empty list, a one-element list, a two-element list, an all-equal list, and a list with a duplicated middle. The targets sit below the data, on a value, between values, and above the data. It then cuts `[10, 20, 30, 40]` at every offset, searches every element plus three absent targets, and checks the minimum against `min`. A miss is counted before the result is used as an index. An index of -1 would otherwise read the last cell, so a missed target that sits there would look like a hit. Zero mismatches is the result of that set. The printed rows are the edges by hand. An empty list and a hit on `[4]` both return 0, and a miss above the only element returns 1. On `[1, 4, 4, 9]`, a target below the list returns 0, a target between 4 and 9 returns 3, and a target above the list returns 4. The last 4 in `[4, 4, 4]` is index 2. `[30, 10, 20]` is `[10, 20, 30]` cut so the minimum sits in the middle. 10 is at index 1, and the minimum is 10.

The same idea applies to a predicate. Check the smallest candidate, the largest candidate, and the first candidate where the predicate flips. Check a range of one value. Compare the result with a linear scan of the range whenever the range is small enough to scan. A rotated search with duplicate values needs that linear scan as the oracle, because the distinct-value loop is not the oracle once equals are allowed. The [Bug hunt: binary search never ends](../../07_Data_Structures_and_Algorithms/09_Sorting_and_Searching/) drill is the loop that never reaches these answers. A cap on the number of steps turns that hang into a failing check.

**Trade-offs.** A dozen hand-written edges catch the off-by-one and miss the bug that needs a wider interval or a particular duplicate pattern. A few hundred random lists, checked against `bisect` or a linear scan, catch those, and they do not replace the two-element trace you can explain. Property tests are only as good as the oracle. Using the search as its own oracle feels green and proves nothing.

**Interview.** Say the edge list before the interviewer asks. Empty, where the contract allows it. One element, hit and miss. Two elements. All equal. Absent below, above, and between. Both ends. Every cut of a four-element rotation if the array is rotated. Then offer the linear scan as the comparison, and `bisect` when the question is a bound. A loop you have not run on two elements is a guess.

**Recap.** Trust the loop after it agrees with a linear scan or with `bisect` on an empty list, a one-element list, a two-element list, an all-equal list, and targets that are absent below, between, and above the data. A rotated array needs every cut of one short sorted input, including the unrotated cut. The exercise checker above reports 0 mismatches on that set. A step cap turns an infinite loop into a failed check instead of a hang.
