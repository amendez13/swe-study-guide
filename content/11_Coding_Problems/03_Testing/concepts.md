## Decide what must not break

A testing discussion starts from behavior, not from a target coverage number. Name the promises the caller relies on: a function returns this value, a write is rejected when the input is invalid, a retry does not double-charge. Those promises are the tests. Everything else is optional until a bug or a requirement promotes it.

## Unit tests pin one behavior

A unit test calls one piece of logic with inputs you chose and checks one outcome. It does not start a database, a network, or a clock you do not control. The value is speed and blame: when it fails, the defect is in that piece. Keep the assertion specific. "Does not throw" is a weak description of a promise about a number.

```python
def late_fee(days_late: int) -> int:
    return 0 if days_late <= 0 else min(days_late * 25, 500)

assert late_fee(0) == 0
assert late_fee(3) == 75
assert late_fee(100) == 500
```

## Integration tests cross a boundary

An integration test is justified when the risk lives in the seam: SQL that does not match the schema, a client that misreads a status code, two modules that agree in isolation and disagree on a null. These tests are fewer and slower. Use them for the boundary, and leave the branching logic to unit tests so a schema typo does not masquerade as an arithmetic bug.

## Arrange, act, assert

Structure every test the same way. Arrange the inputs and the collaborators. Act by calling the one behavior under test. Assert the outcome you care about, and do not hide a second behavior in the same assertion. Shared setup belongs in a helper when several tests need the same world; it does not belong in the assertion.

## Test the edges

The interesting inputs are the ones just inside and just outside a rule: zero, one, the maximum, an empty collection, a duplicate, a value that used to be valid. Happy-path data hides off-by-one mistakes. For each boundary, say which promise it protects, so the test is not an arbitrary extra number.

## Doubles stand in for collaborators

A test double replaces a collaborator so the test can force the situation it needs. A stub returns a canned value. A fake is a lighter working version, such as an in-memory store. A mock records the calls so you can assert that a notification was sent. Prefer a stub or a fake when you care about the result, and a mock when the call itself is the behavior. Do not mock the unit you are testing.

## A failing test is a specification

Write the test that expresses the bug or the new rule, watch it fail for the reason you expect, then make it pass. A test that passes immediately did not pin the change. In an interview, describe this loop out loud: the behavior, the input that exposes it, the assertion, and what a failure would mean. That is more useful than naming a framework.
