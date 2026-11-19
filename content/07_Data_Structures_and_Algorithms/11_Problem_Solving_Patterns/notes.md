# Problem-Solving Patterns

Solving an unfamiliar problem is a skill with two halves. The **process** is the same every time: listen, draw an example, state a brute force, optimize, walk through, implement, and test. The **pattern catalog** is a set of reusable strategies (frequency maps, two pointers, sliding windows, binary search on the answer, and so on) that the optimize step reaches for once you recognize the shape of the problem.

## Key Points

- Treat every detail in the statement as a hint, and ask what an unused detail would unlock.
- Draw a large, specific example that is not a special case.
- State a correct brute force with its complexity before optimizing.
- Optimize by looking for bottlenecks, unnecessary work, and duplicated work (BUD).
- When stuck, solve an instance by hand and turn what you did into an algorithm.
- Relax a constraint, solve the simpler problem, then add the constraint back.
- Build the answer for n from the answers for smaller n.
- Run through the data structures you know and match their strengths to the operations needed.
- The best conceivable runtime is a lower bound; once you reach it, stop optimizing time.
- Walk through the plan before coding, and write modular code that mirrors it.
- Test by reading the code, checking hot spots, then running small and edge cases.
- Map triggers to patterns: counts to a frequency map, sorted pairs to two pointers, contiguous ranges to a sliding window, "smallest value that works" to binary search on the answer, "list every option" to backtracking, grids to BFS or DFS, and "next greater" to a monotonic stack.

## Example

```python
"""One problem, three process steps: brute force, remove duplicated work, test against the brute force.

Task: the largest sum of any k consecutive readings.
"""
import random


def best_window_brute(nums: list[int], k: int) -> int:
    # Brute force: re-sum every window. O(N * k), and adjacent windows share k - 1 values.
    return max(sum(nums[i:i + k]) for i in range(len(nums) - k + 1))


def best_window(nums: list[int], k: int) -> int:
    # Sliding window removes the duplicated work: O(N), which matches the BCR
    # because every reading has to be looked at once.
    window = best = sum(nums[:k])
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best


print(best_window([5, -2, 7, 1, -4, 6, 3], 3))  # 10

# Test step: edge cases first, then random inputs checked against the brute force.
assert best_window([4], 1) == 4
assert best_window([-3, -1, -2], 2) == -3
for _ in range(500):
    nums = [random.randint(-9, 9) for _ in range(random.randint(1, 12))]
    k = random.randint(1, len(nums))
    assert best_window(nums, k) == best_window_brute(nums, k)
print("random tests passed")  # random tests passed
```

## More practice

Work the original exercises on the **Drills** tab: read each prompt, commit to an answer, then open the card to check it. For background reading, open CTCI section VII on the private reader under `#walking-through-a-problem`, with `#optimize-solve-technique-1-look-for-bud` through `#optimize-solve-technique-5-data-structure-brainstorm` and `#best-conceivable-runtime-bcr`. Do not copy book text or solutions into these study files.
