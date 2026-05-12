# SOLID Principles

SOLID is a compact way to talk about several recurring OOP design problems. The principles are less useful as slogans than as concrete questions you ask when a design starts becoming brittle or hard to extend.

## Key Points

- **SRP** — classes should have one coherent reason to change.
- **OCP** — expected variation should often be handled by extension seams, not repeated edits to central branching logic.
- **LSP** — subtypes must preserve the expectations of their parent contracts.
- **ISP** — prefer smaller interfaces over large mixed-purpose ones.
- **DIP** — high-level policy should depend on abstractions instead of concrete implementation details.
- **Use judgment** — SOLID is guidance, not a ceremony.
- **Look for change pain** — difficult extension and tangled tests often reveal a principle violation.

## Example

```python
class PaymentGateway:
    def charge(self, amount: float) -> None:
        raise NotImplementedError


class Checkout:
    def __init__(self, gateway: PaymentGateway) -> None:
        self.gateway = gateway

    def complete(self, amount: float) -> None:
        self.gateway.charge(amount)
```

This small design reflects DIP directly: `Checkout` depends on a payment abstraction rather than on one concrete provider.
