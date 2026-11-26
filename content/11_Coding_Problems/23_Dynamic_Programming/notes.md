# Dynamic Programming

Dynamic programming problems ask for a count, a minimum, a maximum, or a yes/no answer over a sequence of choices, where a plain recursion would ask the same sub-question many times. The theory (overlapping subproblems, optimal substructure, memoization, tabulation) is on the Data Structures [Recursion and Dynamic Programming](#07_Data_Structures_and_Algorithms/08_Recursion_and_Dynamic_Programming) topic, and the choice between counting and listing is on [Backtracking](#11_Coding_Problems/22_Backtracking). This topic is the problem set: spotting DP, the four-step recipe, top-down and bottom-up, shrinking the table, the common table shapes, stairs, coins, grid paths, non-adjacent houses, common subsequences, palindromes, maximum subarray, knapsack, the largest square, and when greedy or backtracking fits better. The two decisions are what one state means and in which order the table can be filled.

## Key Points

- **Spotting a dynamic programming problem** — count, min, max, or "possible" over a chain of choices, and the recursion tree repeats an argument. Cache it.
- **State, recurrence, and base cases** — define the state in a sentence, recur on the last decision, set the stop values, then name the answer cell and the fill order.
- **Top-down and bottom-up** — memoised recursion is the recurrence plus a cache; a table fills cells after their inputs and avoids the recursion limit.
- **Keeping only the rows you read** — keep one row or two variables when that is all the recurrence reads; loop direction decides old versus new values.
- **Table shapes: one and two dimensions** — prefix or ending-at-i (1D); grid, two-string prefixes, items × capacity, substring ranges (2D).
- **Climbing stairs** — `ways(n) = ways(n - 1) + ways(n - 2)`; O(2^n) plain, O(n) time and O(1) space with two variables.
- **Fewest coins for a target** — `best[t] = 1 + min(best[t - c])`, infinity for unreachable, -1 at the end. Greedy fails for coins 1, 5, 6, 9.
- **Counting grid paths** — `paths[r][c] = above + left`, first row and column are 1; one row gives O(n) space.
- **Robbing houses that are not neighbours** — `best[i] = max(best[i - 1], best[i - 2] + money[i])`; for a circle, run twice without each end.
- **Longest common subsequence** — match goes diagonal plus 1, mismatch takes the larger neighbour; the full table is needed to rebuild the letters.
- **Longest palindromic substring** — table filled by length, or expand around 2n - 1 centres in O(n²) time and O(1) space.
- **Maximum subarray sum** — best run ending here is `max(x, prev + x)`; start from the first value so all-negative input works.
- **0/1 knapsack** — leave the item or pack it; in one row, loop capacity downward or the item is packed twice.
- **Largest square of ones** — `side = 1 + min(top, left, top-left)` for a 1 cell; return the side squared.
- **DP, greedy, or backtracking** — greedy when a local choice is provably safe, DP for counts and best values on a small state, backtracking to list answers.

## Example

```python
def fewest_tickets(prices: dict[int, int], days: int) -> int:
    best = [0] + [float("inf")] * days
    for d in range(1, days + 1):
        for length, price in prices.items():
            best[d] = min(best[d], price + best[max(0, d - length)])
    return int(best[days])


passes = {1: 3, 7: 15, 30: 50}
print(fewest_tickets(passes, 4), fewest_tickets(passes, 6), fewest_tickets(passes, 30))
print(fewest_tickets(passes, 0))
# 12 15 50
# 0
```

The state is "cheapest way to cover the first d days", and the last decision is which pass covers day d. Each pass reaches back its length, clamped at day 0, so a 7-day pass beats six day tickets. Days are filled in increasing order because each entry reads only earlier days, for O(days · passes) time and O(days) space. The prices are exercise values.

## More practice

Work the original exercises on the **Drills** tab. Each one names the recurrence, the cost, and a Python check.
