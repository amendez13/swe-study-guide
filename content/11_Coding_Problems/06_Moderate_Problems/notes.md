# Moderate Problems

This topic is an outline for approaching a moderate coding problem: restate the limits, put a correct brute force on the table, name the bookkeeping that removes repeated work, and check the faster idea against the slow one. The cards are a study skeleton. They intentionally do not list published problems or their solutions.

## Key Points

- **A moderate problem has one insight** — a structure or an ordering that makes the obvious loop cheap.
- **Restate and constrain** — input, output, size, duplicates, and empty cases, before code.
- **Try the brute force on a small input** — it is both a starting score and a specification.
- **Name the bookkeeping** — the lookup you wish you had, then the structure that provides it.
- **Shrink what you search** — say which region you discard and why that is safe.
- **Check the answer against the brute force** — same tiny input, then the edges from the restatement.
- **Practice by category** — record the trigger that suggested the structure, not the title of a problem.

## Example

```python
def first_repeat_brute(nums: list[int]) -> int | None:
    for i, value in enumerate(nums):
        if value in nums[:i]:
            return value
    return None

def first_repeat(nums: list[int]) -> int | None:
    seen: set[int] = set()
    for value in nums:
        if value in seen:
            return value
        seen.add(value)
    return None

sample = [4, 1, 7, 1, 4]
assert first_repeat_brute(sample) == first_repeat(sample) == 1
assert first_repeat([]) is None
```

The brute force rescans the prefix. The bookkeeping is "have I seen this value already?", which a set answers in expected constant time. The assertion is the check the outline asks for. A later pass can add categories of triggers; it should not turn into a solution archive.
