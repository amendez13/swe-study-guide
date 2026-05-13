# State, Behavior, and Responsibility

This topic is where OOP starts to become useful instead of decorative. Once you have classes and instances, the real design work is deciding what state an object owns, what behavior is allowed to change that state, and what single job the class is supposed to perform.

## Key Points

- **State** — the current data an object holds, such as balance, status, or items.
- **Behavior** — the methods that read or change that state.
- **Invariants** — rules that must remain true if the object is valid.
- **State transitions** — for status-like objects, legal changes should be explicit and enforced by named methods.
- **Queries vs commands** — some methods answer questions; others change state. Mixing them carelessly makes objects harder to reason about.
- **Responsibility** — a class should have one coherent job that explains why it exists.
- **One reason to change** — if unrelated changes all force edits to the same class, it is probably carrying too many responsibilities.
- **Mixed-concern classes** — classes that combine domain logic, persistence, formatting, and orchestration become fragile quickly.
- **Put behavior with the rule owner** — the object that owns the state should usually own the logic that protects it.

## Example

```python
class Order:
    def __init__(self, total: float) -> None:
        self.total = total
        self.status = "draft"

    def apply_discount(self, percent: float) -> None:
        if not 0 <= percent <= 1:
            raise ValueError("discount must be between 0 and 1")
        if self.status != "draft":
            raise ValueError("only draft orders can be discounted")
        self.total = self.total * (1 - percent)

    def mark_paid(self) -> None:
        if self.status != "draft":
            raise ValueError("only draft orders can be paid")
        self.status = "paid"
```

`Order` owns both the state (`total`, `status`) and the rules around that state. The caller does not set `status` directly or recompute totals elsewhere. That is the design goal here: let the object that owns the data also own the rules that keep it valid.
