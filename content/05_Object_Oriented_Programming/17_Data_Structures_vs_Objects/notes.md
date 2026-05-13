# Data Structures vs Objects

Not every class is a good object, and not every problem wants a behavior-rich model. The useful design question is whether the concept mainly transports data or whether it owns real rules and state transitions.

## Key Points

- **Objects combine data and behavior** — they own rules about their own state.
- **Data structures mostly expose data** — callers decide what to do with the values.
- **Anemic models are a warning sign** — a class with only fields may be a record wearing OOP syntax.
- **Rich objects own their rules** — calculations and transitions belong with the concept that owns them.
- **Data structures are strong at boundaries** — payloads, rows, messages, and config often fit better as plain data.
- **Objects are strong where rules accumulate** — invariants and lifecycle pressure often justify behavior-rich design.
- **Both styles can coexist** — most systems need both.
- **Ask where the rule should live** — that usually points to the better model.

## Example

```python
class Cart:
    def __init__(self) -> None:
        self.items = []

    def add_item(self, product_id: str, quantity: int) -> None:
        self.items.append((product_id, quantity))

    def total_items(self) -> int:
        return sum(quantity for _, quantity in self.items)
```

`Cart` is more than a record because it owns behavior that clearly belongs to the cart concept. A plain transport object for API input would be a different design choice with a different purpose.
