# Relationships Between Objects

Object-oriented systems are really networks of related objects. The important design question is not just whether two objects are related, but how: loosely associated, grouped, strongly owned, or simply collaborating across a boundary.

## Key Points

- **Relationships shape the model** — most useful objects exist in relation to others.
- **Association is the broad category** — one object knows about or uses another.
- **Aggregation is weaker ownership** — the whole groups parts that can still exist independently.
- **Composition is stronger ownership** — the whole meaningfully owns the part's lifecycle.
- **Collaboration is different from containment** — using another object is not the same as owning it.
- **Multiplicity matters** — one-to-one, one-to-many, and many-to-many affect the design.
- **Ownership affects cleanup and persistence** — lifecycle questions often reveal the real relationship strength.
- **Match the real rule** — do not model stronger ownership than the domain actually needs.

## Example

```python
class LineItem:
    def __init__(self, product_id: str, quantity: int) -> None:
        self.product_id = product_id
        self.quantity = quantity


class Order:
    def __init__(self) -> None:
        self.items: list[LineItem] = []

    def add_item(self, product_id: str, quantity: int) -> None:
        self.items.append(LineItem(product_id, quantity))
```

`Order` composes `LineItem` objects because the line items are meaningful as part of the order's lifecycle. That is stronger than a mere association and more precise than just saying the objects are "related."
