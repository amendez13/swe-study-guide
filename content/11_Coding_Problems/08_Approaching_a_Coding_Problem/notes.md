# Approaching a Coding Problem

Every pattern topic in this section assumes you already know which pattern to reach for. This topic is the step before that: how coding interviews are run and scored, a six-step script for a 45-minute round, the clarifying questions and input limits that decide the algorithm, how to state a brute force and restate the cost of what you coded, how to test and talk out loud, what to say when stuck, and a map that routes a problem statement to the pattern topics from [Two Pointers](#11_Coding_Problems/09_Two_Pointers) to [Math and Geometry](#11_Coding_Problems/27_Math_and_Geometry). The general problem-solving method (examples, BUD, best conceivable runtime) is taught on [Problem Solving Patterns](#07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns) and is linked rather than repeated.

## Key Points

- **Coding interview formats** — online assessments (hidden tests, no hints), screens (one problem plus talk), take-homes (read like a pull request), final loops (consistency); ask which one you face.
- **What interviewers score** — problem solving, communication, collaboration, clean code, optimisation, adapting, testing; red flags are silence, rigidity, ignored constraints, and no testing.
- **The six-step answer** — clarify, design from a brute force, estimate, code cleanly, restate the cost, test; about 16 of 45 minutes before typing.
- **Clarifying questions that change the algorithm** — sorted, negatives, duplicates, empty input, in place, output order, size of n; say why you ask.
- **Constraints set the target complexity** — n ≤ 10 → n!, ≤ 20 → 2ⁿ, ≤ 500 → n³, ≤ 5,000 → n², ≤ 10⁶ → n log n; rules of thumb, not laws.
- **Brute force, then name the waste** — one sentence with the cost, then the work the inner loop repeats; the waste names the pattern.
- **Restate the complexity after coding** — hidden sorts, `in` on lists, slices, recursion stack; say "excluding the output" when it applies.
- **Ask before built-ins and in-place changes** — use `sorted`, `Counter`, `heapq` with their costs; ask when the built-in is the question or the input would change.
- **Testing out loud** — trace one ordinary case through the real code, then edges (empty, one, two, all equal), then boundaries (0, max, k = n).
- **Talking through the problem** — narrate decisions, check in at forks, ask for thinking time, use precise words (subarray vs subsequence).
- **Getting unstuck** — say what failed and why, shrink the input, drop a constraint, walk the pattern map, ask a specific question.
- **The pattern recognition map** — statement signals routed to the nineteen pattern topics, with union-find and topological order inside Graphs.
- **When two patterns fit** — ask the tiebreak question, follow the topic's decision card, or test the faster idea against a brute force.
- **Practising pattern recognition** — name the pattern in a minute before coding, spaced re-solves without notes, timed runs, a mistake log of missed signals.

## Example

```python
def plan_for(n: int, contiguous_sum: bool, negatives: bool) -> str:
    if n <= 20:
        return "every subset: backtracking or bitmasks"
    if contiguous_sum:
        return "prefix sums + hash map" if negatives else "sliding window"
    return "sort or hash map, then one pass"


print(plan_for(15, True, True))
print(plan_for(100_000, True, False), "|", plan_for(100_000, True, True))
print(plan_for(100_000, False, False))
# every subset: backtracking or bitmasks
# sliding window | prefix sums + hash map
# sort or hash map, then one pass
```

The function turns two clarifying answers and one constraint into a first plan. A tiny n makes exhaustive search the intended answer, and the plan stops there. For a large n with a contiguous-sum question, the negative-values answer decides between an O(n) window and an O(n) prefix-sum map, and anything else starts from a sort or a hash map. It is a sketch of the habit, not a real router: the point is that the plan comes from the answers, before any code is written.

## More practice

Work the original exercises on the **Drills** tab. Each one names the move, the cost, and a Python check.
