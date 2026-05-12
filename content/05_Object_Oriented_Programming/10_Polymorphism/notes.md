# Polymorphism

Polymorphism is the OOP technique that makes variation manageable. Instead of centralizing every behavior difference in conditionals, you define one shared operation and let each concrete type implement it appropriately.

## Key Points

- **One interface, many behaviors** — callers use one contract while concrete types provide different implementations.
- **Subtype polymorphism** — subclasses can override behavior from a shared parent type.
- **Dynamic dispatch** — runtime type determines which implementation runs.
- **Replaces type switches** — object behavior can absorb branching that would otherwise live in `if/elif` chains.
- **Interface-based polymorphism** — shared contracts do not require deep inheritance.
- **Good for extension** — new variants can be added by implementing the same contract.
- **The contract must be coherent** — the shared method should mean roughly the same thing across implementations.
- **Use it where variation is real** — if there is no meaningful polymorphic variation, a simpler design may be better.

## Example

```python
class TaxCalculator:
    def total(self, amount: float) -> float:
        raise NotImplementedError


class USTaxCalculator(TaxCalculator):
    def total(self, amount: float) -> float:
        return amount * 1.07


class EUTaxCalculator(TaxCalculator):
    def total(self, amount: float) -> float:
        return amount * 1.20


def checkout(amount: float, calculator: TaxCalculator) -> float:
    return calculator.total(amount)
```

`checkout()` does not need `if region == ...` logic. It works with the shared `TaxCalculator` contract and lets the concrete object supply the right behavior.
