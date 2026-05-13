# Testing and Evolution

The long-term value of OOP design shows up under change. Well-shaped objects are easier to test, easier to refactor, and easier to adapt when requirements move. Weak boundaries make all of those things more expensive.

## Key Points

- **Good design lowers test cost** — focused responsibilities and narrow contracts are easier to validate.
- **Test public behavior** — assert outcomes, transitions, and errors rather than private implementation details.
- **Simple contracts help fakes** — abstractions make isolated testing easier.
- **State transitions deserve tests** — especially for lifecycle-heavy objects.
- **Strong boundaries support refactoring** — smaller public surfaces make internal changes safer.
- **Requirements will evolve** — design quality is measured under change, not in static diagrams.
- **Deep hierarchies can age badly** — inheritance-heavy designs often become harder to reshape.
- **Aim for adaptability** — the goal is not perfect first design, but sustainable evolution.

## Example

```python
class Task:
    def __init__(self) -> None:
        self.status = "todo"

    def start(self) -> None:
        if self.status != "todo":
            raise ValueError("only todo tasks can start")
        self.status = "in_progress"
```

A useful test for this object is not whether it calls some internal helper. It is whether `start()` moves a `todo` task to `in_progress` and rejects invalid transitions. That is behavior the rest of the system actually depends on.
