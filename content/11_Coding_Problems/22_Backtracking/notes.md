# Backtracking

Backtracking problems ask for every arrangement, every group, or one placement that satisfies a set of rules, on inputs small enough that an exponential search is acceptable. The general skeleton is on the Data Structures [Problem Solving Patterns](#07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns) topic, and the comparison with memoised recursion is on [Recursion and Dynamic Programming](#07_Data_Structures_and_Algorithms/08_Recursion_and_Dynamic_Programming). This topic is the problem set: spotting the pattern, drawing the search tree, the choose-explore-undo loop, the three shapes, pruning, cost estimates, permutations, subsets, n queens, target sums, keypad strings, repeated values, a small Sudoku, and when to count with DP instead. The two decisions are what one level of the tree decides and which choices are legal at a node.

## Key Points

- **Spotting a backtracking problem** — "list all", "generate every", or "find a placement" on a small input. If only a count or a best value is wanted, check DP first.
- **The state space tree** — root is the empty answer, edges are decisions, leaves are answers or dead ends. Sketch two levels before coding.
- **Choose, explore, undo** — stop check, loop over legal choices, change state, recurse, restore every change. Record `path[:]`, never `path`.
- **Permutations, subsets, and combinations** — any unused element per level for orderings; loop from a start index for groups; recurse with `i` to allow reuse.
- **Pruning and constraint bookkeeping** — sort and `break` on a bound; keep sets and counters so each legality check is O(1).
- **Estimating the cost** — about b^d nodes times the O(d) copy per answer: O(n · n!), O(n · 2^n), O(k · C(n, k)), O(n · 4^n).
- **All permutations** — a `used` array and a path; n! leaves, O(n · n!) time, O(n) extra space.
- **All subsets** — include or skip each index; 2^n leaves. Iterative and bitmask versions cost the same.
- **Placing n queens** — one queen per row; sets for columns, `r - c`, and `r + c`. O(n!) time, O(n) space.
- **Combinations that reach a target** — start index prevents reorderings, recurse with `i` for reuse, sort and break on overshoot. Zeros never terminate.
- **Phone keypad letter strings** — one level per digit, three or four letters each. Return `[]` for empty input and join at the leaf.
- **Repeated values: sort and skip** — skip an equal sibling with `i > start`; for orderings, skip when the equal previous value is unused.
- **Filling a small Sudoku** — try legal digits per blank, stop at the first full grid. Fill the most constrained cell first.
- **Backtracking or dynamic programming** — list, generate, or print means backtracking; count, min, max, or "possible" with a small state means DP.

## Example

```python
def topping_groups(items: list[str], k: int) -> list[str]:
    out: list[str] = []
    path: list[str] = []

    def go(start: int) -> None:
        if len(path) == k:
            out.append(" + ".join(path))
            return
        for i in range(start, len(items)):
            path.append(items[i])
            go(i + 1)
            path.pop()

    go(0)
    return out


toppings = ["olive", "pepper", "onion", "basil"]
print(topping_groups(toppings, 2))
print(len(topping_groups(toppings, 3)), topping_groups(toppings, 0))
# ['olive + pepper', 'olive + onion', 'olive + basil', 'pepper + onion', 'pepper + basil', 'onion + basil']
# 4 ['']
```

The `start` index is what makes this a group search rather than an ordering search: each pair appears once, in input order. The path is copied (here by joining) at the leaf, and `pop` restores it for the next choice. Asking for zero items returns one empty group, which is the case to raise before coding. All toppings are exercise names.

## More practice

Work the original exercises on the **Drills** tab. Each one names the rule, the cost, and a Python check.
