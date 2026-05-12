## SOLID is a design checklist, not a religion

SOLID is a group of five OOP design heuristics aimed at reducing coupling and clarifying responsibilities. It is best used as a pressure test for designs that are getting messy, not as a ritual you recite over every class.

Each principle asks a useful question about change, extension, and dependency shape.

## Single Responsibility Principle (SRP)

SRP says a class should have one coherent reason to change. It is not "one method only"; it is "one axis of responsibility."

If a class changes for pricing rules, email-template changes, database schema changes, and API formatting changes, it is doing too much.

```python
class InvoiceTotalCalculator:
    def total(self, line_items: list[float]) -> float:
        return sum(line_items)


class InvoiceEmailSender:
    def send(self, email: str, amount: float) -> None:
        print(f"Sent invoice for {amount} to {email}")
```

Here calculation and email delivery are separated because they change for different reasons.

## Open/Closed Principle (OCP)

OCP says software should be open to extension but closed to risky modification. In practice, that often means new behavior comes in by new classes or strategies rather than by editing a giant central `if/elif` tree every time.

This does not forbid modification. It just pushes you to design extension seams where variation is expected.

```python
class DiscountPolicy:
    def apply(self, total: float) -> float:
        raise NotImplementedError


class NoDiscount(DiscountPolicy):
    def apply(self, total: float) -> float:
        return total


class TenPercentOff(DiscountPolicy):
    def apply(self, total: float) -> float:
        return total * 0.9
```

New discount behavior is added by creating another `DiscountPolicy`, not by rewriting one central pricing function.

## Liskov Substitution Principle (LSP)

LSP says a subtype should be safely usable anywhere its parent type is expected. If a subclass breaks the behavior callers rely on, the inheritance relationship is lying.

This is why subtype design is semantic, not merely syntactic.

```python
class Bird:
    def move(self) -> str:
        return "moving"


class Sparrow(Bird):
    def move(self) -> str:
        return "flying"


def describe_movement(bird: Bird) -> str:
    return bird.move()
```

`describe_movement()` can use `Sparrow` anywhere it expects a `Bird` because the subtype still honors the parent contract.

## Interface Segregation Principle (ISP)

ISP says callers should not be forced to depend on large interfaces they do not actually need. Smaller, more focused interfaces are often easier to implement and easier to understand.

This helps avoid giant contracts that bundle unrelated operations together.

```python
class Reader:
    def read(self, path: str) -> str:
        raise NotImplementedError


class Writer:
    def write(self, path: str, content: str) -> None:
        raise NotImplementedError


class FileReader(Reader):
    def read(self, path: str) -> str:
        return "file contents"
```

`FileReader` only implements the reading contract. It is not forced to pretend it also knows how to write.

## Dependency Inversion Principle (DIP)

DIP says high-level policy should depend on abstractions, not on concrete low-level details. A checkout flow should depend on a `PaymentGateway` contract, not on a specific Stripe client everywhere.

That keeps orchestration logic from being tightly welded to one implementation choice.

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

`Checkout` depends on the `PaymentGateway` abstraction, so the payment provider can change without rewriting checkout logic.

## SOLID works best with judgment

These principles are useful because they point to real failure modes: mixed responsibilities, giant switch statements, unsafe inheritance, bloated interfaces, and concrete dependency tangles.

Used mechanically, though, they can produce needless indirection. The goal is clearer design, not maximum layers.

## Violations often show up as change pain

When a feature is hard to extend, a class changes for unrelated reasons, or tests require too much setup, a SOLID principle is often the thing being violated in practice.

That makes SOLID most useful during redesign and review, where the pain is already visible.
