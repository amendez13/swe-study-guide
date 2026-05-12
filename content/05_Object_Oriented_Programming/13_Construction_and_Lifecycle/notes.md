# Construction and Lifecycle

Construction is where validity begins. Lifecycle is what happens to the object after that: who owns it, how long it lives, and what rules govern its creation, mutation, and cleanup.

## Key Points

- **Construction should yield a usable object** — callers should not have to perform secret setup steps afterward.
- **Require real inputs** — constructors should demand the data the object genuinely needs.
- **Defaults must be meaningful** — only default values that represent valid states.
- **Start invariants early** — invalid objects should be blocked as early as possible.
- **Lifecycle ownership matters** — object relationships often imply creation and cleanup responsibilities.
- **Factories can help** — named constructors make complex creation more legible.
- **Avoid surprising side effects** — heavy I/O in constructors makes creation harder to reason about.
- **Have a clear lifetime story** — the code should make ownership and disposal understandable.

## Example

```python
class PercentageDiscount:
    def __init__(self, percent: float) -> None:
        if not 0 <= percent <= 1:
            raise ValueError("percent must be between 0 and 1")
        self.percent = percent
```

The constructor prevents invalid discount objects from existing at all. That is better than allowing bad objects into the system and trying to defend against them later.
