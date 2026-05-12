# Finding Classes from Requirements

Class discovery is one of the first practical OOP skills. The job is not to mechanically convert every noun into a class; the job is to find a model that matches the real responsibilities and workflows of the system.

## Key Points

- **Start from the problem** — model the domain first, not the language syntax.
- **Nouns help, but they are only a first pass** — some nouns become classes, others become fields or disappear entirely.
- **Verbs reveal behavior** — actions tell you what responsibilities your objects may need to own.
- **Use cases clarify boundaries** — workflows expose collaborators, state changes, and failure points.
- **CRC cards are useful** — candidate class, responsibility, and collaborator is a simple pressure test.
- **Names matter** — good class names usually reflect domain meaning; vague names often hide vague responsibilities.
- **Avoid over-modeling** — not every small concept needs its own class.
- **Refine as you learn** — a good model usually emerges through iteration, not from the first draft.

## Example

```python
# requirement:
# "A customer places an order, inventory is reserved,
# payment is charged, and a receipt is emailed."

class Order:
    pass


class Inventory:
    pass


class PaymentGateway:
    pass


class ReceiptService:
    pass
```

This is not a finished design, but it is the right kind of starting point. The requirement gives you domain nouns and actions, which in turn suggest classes and responsibilities that can be refined as implementation details become clearer.
