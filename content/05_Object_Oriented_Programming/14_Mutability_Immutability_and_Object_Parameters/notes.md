# Mutability, Immutability, and Object Parameters

Whether an object can change is one of the biggest forces on code clarity. Mutable objects model evolving workflows well, but immutable objects are usually easier to reason about and safer to share.

## Key Points

- **Mutable objects change over time** — useful for workflows and long-lived entities.
- **Immutable objects stay stable** — great for value-like concepts and safer sharing.
- **Value objects often want immutability** — money, dates, percentages, and identifiers are common examples.
- **Shared mutable state is risky** — it creates hidden dependencies and timing problems.
- **Passing an object shares identity** — callees may observe or mutate the same instance.
- **Returning objects can preserve meaning** — richer return types carry behavior as well as data.
- **Immutable returns are often safer** — callers can use them without worrying about later mutation.
- **Choose by concept** — use mutation where the domain needs it, not by habit.

## Example

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str


price = Money(amount=1000, currency="USD")
discounted = Money(amount=900, currency=price.currency)
```

`Money` is a good immutable value object because callers usually want to compare, pass, and return it safely without worrying that some other part of the system will mutate it in place.
