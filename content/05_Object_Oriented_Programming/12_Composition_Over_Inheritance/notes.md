# Composition Over Inheritance

Composition is the safer default for reuse. It lets objects assemble behavior from collaborators instead of inheriting every assumption and extension point from a base class.

## Key Points

- **Composition builds from collaborators** — behavior comes from contained or injected objects.
- **Inheritance is for true subtype meaning** — composition is often better when the real goal is reuse.
- **Dependencies stay visible** — collaborators appear directly in the object design.
- **Parts are easier to swap** — one strategy or provider can change without rewriting the rest.
- **Avoids fragile base classes** — composition narrows coupling compared with inheritance.
- **Strategy is a classic example** — interchangeable collaborators are composition in practice.
- **Can add indirection** — too many tiny wrappers create their own complexity.
- **Good default** — composition is usually the safer starting point when the design is not yet obvious.

## Example

```python
class PercentageDiscount:
    def apply(self, total: float) -> float:
        return total * 0.9


class Checkout:
    def __init__(self, discount_policy) -> None:
        self.discount_policy = discount_policy

    def total(self, subtotal: float) -> float:
        return self.discount_policy.apply(subtotal)
```

`Checkout` reuses discount behavior by composition. It does not need a subclass per policy, and the discount logic can be swapped independently.
