## Objects rarely stand alone

Most useful object models are built from relationships: an order has line items, a team has members, a cart uses inventory, a user has a profile, a payment belongs to an invoice.

Understanding those relationships matters because they shape ownership, lifecycle, and the kinds of operations the code can support safely.

## Association is the general case

An **association** is simply that one object knows about, references, or works with another object. A `Cart` may have an `Inventory`; a `ReportGenerator` may use a `Formatter`.

Association is the broadest category. It says the objects are related, but not yet how strongly or who owns whom.

## Aggregation means "has-a" without full ownership

Aggregation is a whole-part relationship where the parts can exist independently. A `Team` can have `Player` objects, but the players can still exist even if the team changes or disappears.

This is useful when one object groups others without fully controlling their lifecycle.

## Composition means stronger ownership

Composition is a whole-part relationship where the containing object meaningfully owns the part's lifecycle. If the whole disappears, the part usually does too.

```python
class LineItem:
    def __init__(self, name: str, quantity: int) -> None:
        self.name = name
        self.quantity = quantity


class Order:
    def __init__(self) -> None:
        self.items: list[LineItem] = []
```

Here `LineItem` is naturally part of an `Order`. It usually does not make sense as a long-lived object floating independently through the system.

## Collaboration is not the same as containment

Sometimes objects work together without one containing the other. An `OrderService` calling a `PaymentGateway` is collaboration, not composition.

This distinction matters. If you confuse "uses" with "owns," your model becomes harder to reason about and harder to manage over time.

## Multiplicity changes the design

One-to-one, one-to-many, and many-to-many relationships have different consequences. A user may have one profile, one order may have many line items, and many students may enroll in many courses.

These differences affect data structures, lifecycle rules, traversal, and persistence strategy. They are not just diagram notation.

## Ownership affects cleanup and persistence

One useful question is: who is responsible for creating, updating, deleting, or persisting the related object? The answer often reveals whether the relationship is weak, strong, shared, or composed.

This is why relationship design is not only conceptual. It directly shapes implementation and operational behavior.

## Prefer relationships that match real rules

If an object truly owns another object's lifecycle, model that strongly. If the relationship is just occasional collaboration, model that more lightly. The closer the code matches the real rule, the less surprise the model creates later.

Overstating ownership is a common mistake. It makes reuse harder and couples objects more tightly than the domain actually requires.
