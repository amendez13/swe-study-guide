# Greedy

Greedy problems ask for the most, the fewest, or whether something is reachable, and they can be solved by taking the locally best choice at every step and never undoing it. The idea is introduced on [Greedy choice](#07_Data_Structures_and_Algorithms/11_Problem_Solving_Patterns/concepts/greedy-choice), the earliest-end rule is worked on [Intervals](#11_Coding_Problems/17_Intervals), and the cases where greedy fails are handled by [Dynamic Programming](#11_Coding_Problems/23_Dynamic_Programming). This topic is the problem set: spotting greedy, the two properties it needs, the exchange and stays-ahead proofs, fractional versus whole knapsack, coin systems, the common sort keys, cheapest-pair merging, jumping to the end, gas stations around a loop, candies by rating, and how to test a greedy rule in an interview. The two decisions are which local choice to commit to and why that choice is safe.

## Key Points

- **Spotting a greedy problem** — most, fewest, or reachable, plus one choice that obviously dominates; usually a sort and one scan.
- **Greedy choice and optimal substructure** — some optimal answer starts with the greedy choice, and the rest is a smaller copy of the problem.
- **The exchange argument** — swap an optimal answer's first different choice for the greedy one without making it worse; shortest job first.
- **The stays-ahead argument** — after every step greedy has made at least as much progress as any other plan; refuel at the farthest station in reach.
- **Fractional and 0/1 knapsack** — best value per kilogram is optimal when items can be cut, wrong when they are whole.
- **Greedy or dynamic programming** — largest coin first works only for canonical coin systems; check against the DP below the sum of the two largest coins.
- **Common greedy moves** — sort by end, deadline, or length; track the farthest reach; pair extremes; two passes; a heap for the next best.
- **Merging the cheapest pair first** — join the two smallest with a min-heap, O(n log n); the same rule builds Huffman codes.
- **Jump to the end** — keep the leftmost index that reaches the end, or the farthest reach so far; O(n) time and O(1) space.
- **Gas stations around a loop** — no start if total gas is short; otherwise restart after every negative tank, O(n).
- **Candies by rating** — left pass for rises, right pass with `max` for falls; equal ratings constrain nothing.
- **Greedy in an interview** — state the rule, hunt for a small counterexample, give the proof idea, and stress-test against brute force.

## Example

```python
def fewest_taps(reach: list[int], length: int) -> int:
    farthest_from = [0] * (length + 1)
    for spot, radius in enumerate(reach):
        left = max(0, spot - radius)
        farthest_from[left] = max(farthest_from[left], min(length, spot + radius))
    taps, covered, best = 0, 0, 0
    for x in range(length):
        best = max(best, farthest_from[x])
        if x == covered:
            if best <= x:
                return -1
            taps += 1
            covered = best
    return taps


print(fewest_taps([3, 0, 0, 0, 0, 2], 5), fewest_taps([1, 0, 0, 2, 0, 0], 5))
print(fewest_taps([0, 0, 0], 2), fewest_taps([], 0))
# 2 2
# -1 0
```

A garden runs from 0 to `length`, and a tap at position i waters from `i - reach[i]` to `i + reach[i]`. Record, for each left edge, the farthest point any tap starting there covers, then sweep like the fewest-jumps scan: when the sweep reaches the end of the watered stretch, open the tap that reaches farthest. Committing to the farthest reach stays ahead of any other choice, for O(length + taps) time and O(length) space. The reaches are exercise values.

## More practice

Work the original exercises on the **Drills** tab. Each one names the greedy rule, why it is safe, the cost, and a Python check.
