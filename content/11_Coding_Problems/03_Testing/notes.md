# Testing

Testing in an interview is a way of listing the promises you would pin, the inputs that represent them, and the layer that should run the check. The same list works on a key cabinet and on a fee function. Tools come after the cases. When the prompt is a symptom instead of a spec, the job changes: reproduce, narrow the layer, then add the test that would have caught it.

## Key Points

- **What the interviewer is looking for** — cases and reasons. A framework name is not the answer.
- **Testing a real-world object** — happy path, invalid input, "already done," and two actors at once. The categories move to code unchanged.
- **Manual vs automated** — explore by hand once. Automate the check you will re-run and whose expected result you can write down.
- **Black-box vs white-box** — black-box comes from the promise. White-box adds paths you only notice by reading. Assert what the caller sees.
- **Testing a function** — arrange, call once, assert one promise. Ordinary input, a boundary, and a refusal.
- **Unit, integration, and end-to-end** — one piece, a real seam, or a path a person takes. Put the bug in the layer that can name it.
- **The test pyramid** — many function tests, fewer seam tests, a few end-to-end tests. An upside-down pyramid is slow and vague.
- **Equivalence classes** — inputs the promise treats alike. One representative per class, not three copies of the same idea.
- **Boundary values** — the last input of one class and the first of the next. Off-by-one hides in the middle of a class.
- **Edge and error cases** — legal extremes versus inputs the contract refuses. Assert the refusal, not a stack-trace sentence.
- **Stubs, fakes, and mocks** — a canned value, a working stand-in, or a recorder of calls. Mock when the call is the bug.
- **Property-based testing** — a rule for many inputs, such as "never above the cap" or "clipping twice equals clipping once."
- **Flaky tests and determinism** — inject the clock, seed randomness, sort, and isolate state. A retry hides the cause.
- **Load and security basics** — a workload and a pass line for load. For security, unauthorized and hostile inputs are refused.
- **Troubleshooting questions** — a symptom is a claim. Ask who, where the number appears, and whether you can name one example.
- **A troubleshooting sequence** — expected behavior, reproduction, layer, the boundary the symptom points at, then a small fix and a test.

## Example

```python
"""Member locker fee: free through 2 hours, then 75 cents/hour, cap 1500.
Guests pay 100 cents/hour from the start, same cap. Negative hours are refused.
"""


def locker_fee(hours: int, member: bool) -> int:
    if hours < 0:
        raise ValueError("hours")
    raw = max(0, hours - 2) * 75 if member else hours * 100
    return min(raw, 1500)


# Ordinary, both sides of the free window, the cap, and a refusal.
assert locker_fee(5, member=True) == 225
assert locker_fee(2, member=True) == 0
assert locker_fee(3, member=True) == 75
assert locker_fee(22, member=True) == 1500
assert locker_fee(23, member=True) == 1500
assert locker_fee(15, member=False) == 1500

for hours in range(0, 40):
    fee = locker_fee(hours, member=True)
    assert 0 <= fee <= 1500
    assert fee <= locker_fee(hours, member=False)
```

The assertions are the black-box list: one ordinary member hour, the boundary pair at 2 and 3, the cap pair at 22 and 23, a guest on the cap, then two properties checked across a range. Hour 5 alone stays green if the cap is missing. Hour 23 does not.

## More practice

Work the original exercises on the **Drills** tab. They ask for a case list, a missing boundary, the right double, a property, and a symptom to narrow. Each answer includes a short Python check.
