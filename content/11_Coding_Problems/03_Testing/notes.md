# Testing

This topic is an outline for talking about tests in an interview: which promises matter, which kind of test pins them, and how a single test is shaped. The cards name the distinctions to expand later. They are not a tour of a test framework.

## Key Points

- **Decide what must not break** — tests describe promises a caller relies on, not a coverage quota.
- **Unit tests pin one behavior** — chosen inputs, one outcome, no real database or network.
- **Integration tests cross a boundary** — use them where two sides can disagree, and keep them few.
- **Arrange, act, assert** — build the world, call one behavior, check one result.
- **Test the edges** — zero, one, empty, the limit, and the first illegal value.
- **Doubles stand in for collaborators** — stub a result, fake a dependency, mock only when the call is the behavior.
- **A failing test is a specification** — see the failure you expect, then change the code.

## Example

```python
def apply_discount(cents: int, percent: int) -> int:
    if not 0 <= percent <= 100:
        raise ValueError("percent out of range")
    return cents * (100 - percent) // 100

# Arrange / act / assert, including the boundary just outside the rule.
assert apply_discount(2000, 0) == 2000
assert apply_discount(2000, 100) == 0
try:
    apply_discount(2000, 101)
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

The example is the shape of a unit test. A later pass should add how this function would be checked together with the code that loads the percent from storage, which is the integration case.
