# Problem-Solving Patterns

Problem-solving patterns are reusable algorithmic strategies that recur across hundreds of data structure and algorithm problems. Rather than memorizing individual solutions, learning these patterns lets you recognize the shape of a problem and apply a known strategy. Each pattern has a trigger -- a signal in the problem statement that tells you which approach to reach for -- and a mechanical template you can adapt to the specific constraints.

## Key Points

- **Frequency counting solves comparison-by-content problems** -- Build a hash map of element counts in O(N) to check anagrams, detect duplicates, find majority elements, or verify permutations without sorting.
- **Two pointers reduce pair searches from O(N^2) to O(N)** -- On sorted input, one pointer advances from the left and one from the right; each step eliminates a class of candidates, so every element is visited at most once.
- **Sliding window avoids redundant subarray recomputation** -- Maintain a running aggregate over a contiguous window; when the window slides by one, add the entering element and remove the leaving element instead of recalculating from scratch.
- **Divide and conquer splits a problem into independent subproblems** -- Recursively solve each half and combine results; time depends on the recurrence (Master Theorem), with merge sort at O(N log N) and binary search at O(log N).
- **Greedy works when local optima compose into global optima** -- Make the best immediate choice and never reconsider; interval scheduling (sort by end time, always pick the earliest-finishing activity) is the textbook example.
- **Backtracking is exhaustive search with pruning** -- Build solutions incrementally, abandon branches that violate constraints early, and undo each choice before trying the next; generates permutations, combinations, and constraint-satisfaction solutions.
- **BFS and DFS are general problem-solving frameworks** -- BFS for shortest path and level-order processing, DFS for connectivity, cycle detection, and exhaustive traversal; on grids, treat cells as nodes and adjacency as edges.
- **Binary search on the answer space finds optimal thresholds** -- When a feasibility check is monotonic (all values below a threshold fail, all above succeed), binary search finds the boundary in O(log M) feasibility checks.
- **Monotonic stacks solve next-greater/next-smaller in O(N)** -- Maintain a stack in sorted order; each element is pushed and popped at most once, giving amortized O(1) per element despite inner-loop pops.
- **Bit vectors compress boolean arrays by 8x** -- Use individual bits as flags via bitwise operations to track seen elements, detect duplicates, or implement compact visited sets in memory-constrained scenarios.

## Example

```python
"""
Demonstration of six core problem-solving patterns applied to
concrete problems. Each function is self-contained and runnable.
"""
from collections import Counter, deque
import math


# --- 1. Frequency Counting: Anagram Check ---

def is_anagram(s: str, t: str) -> bool:
    """Return True if t is an anagram of s. O(N) time, O(K) space."""
    return len(s) == len(t) and Counter(s) == Counter(t)


# --- 2. Two Pointers: Pair Sum in Sorted Array ---

def two_sum_sorted(nums: list[int], target: int) -> tuple[int, int] | None:
    """Find indices of two numbers summing to target. O(N) time."""
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


# --- 3. Sliding Window: Maximum Sum Subarray of Size K ---

def max_sum_subarray(nums: list[int], k: int) -> int:
    """Return max sum of any contiguous subarray of size k. O(N) time."""
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best


# --- 4. Backtracking: Generate Permutations ---

def permutations(nums: list[int]) -> list[list[int]]:
    """Generate all permutations of nums. O(N! * N) time."""
    result: list[list[int]] = []

    def backtrack(path: list[int], remaining: set[int]) -> None:
        if not remaining:
            result.append(path[:])
            return
        for num in sorted(remaining):
            path.append(num)
            backtrack(path, remaining - {num})
            path.pop()

    backtrack([], set(nums))
    return result


# --- 5. BFS: Island Counting ---

def count_islands(grid: list[list[str]]) -> int:
    """Count connected components of '1's in a 2D grid. O(R*C) time."""
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    islands = 0

    def bfs(r: int, c: int) -> None:
        queue = deque([(r, c)])
        visited[r][c] = True
        while queue:
            cr, cc = queue.popleft()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = cr + dr, cc + dc
                if (0 <= nr < rows and 0 <= nc < cols
                        and not visited[nr][nc] and grid[nr][nc] == "1"):
                    visited[nr][nc] = True
                    queue.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and not visited[r][c]:
                bfs(r, c)
                islands += 1
    return islands


# --- 6. Monotonic Stack: Next Greater Element ---

def next_greater_element(nums: list[int]) -> list[int]:
    """For each element, find the next greater to its right. O(N) time."""
    n = len(nums)
    result = [-1] * n
    stack: list[int] = []
    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:
            result[stack.pop()] = nums[i]
        stack.append(i)
    return result


if __name__ == "__main__":
    # Frequency counting
    print("anagram:", is_anagram("listen", "silent"))
    # anagram: True

    # Two pointers
    print("pair:", two_sum_sorted([1, 3, 5, 7, 9, 11], 10))
    # pair: (0, 4) -> 1 + 9

    # Sliding window
    print("max_sum:", max_sum_subarray([2, 1, 5, 1, 3, 2], 3))
    # max_sum: 9

    # Backtracking
    print("perms:", permutations([1, 2, 3]))
    # perms: [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]

    # BFS island counting
    grid = [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "1"],
    ]
    print("islands:", count_islands(grid))
    # islands: 3

    # Monotonic stack
    print("next_greater:", next_greater_element([2, 1, 2, 4, 3]))
    # next_greater: [4, 2, 4, -1, -1]
```

Each pattern targets a specific problem shape: frequency counting for comparison-by-content, two pointers for sorted pair searches, sliding window for contiguous subarray aggregates, backtracking for exhaustive enumeration with pruning, BFS for grid connectivity, and monotonic stack for next-greater queries. Recognizing the trigger in the problem statement is the skill that transfers across hundreds of individual problems.
