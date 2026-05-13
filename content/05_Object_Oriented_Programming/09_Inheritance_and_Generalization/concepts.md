## Inheritance models "is-a"

Inheritance is the OOP tool for expressing that one type is a more specific form of another. A `SavingsAccount` may be a kind of `BankAccount`; a `Dog` may be a kind of `Animal`.

This is useful when the subtype genuinely shares behavior and a meaningful contract with the supertype, not just when the code happens to look similar today.

## Generalization is the design move behind inheritance

Generalization is the step of noticing that several specific types share a more abstract idea. If `CreditCardPayment` and `BankTransferPayment` both support `authorize()`, you may have a more general `PaymentMethod`.

Inheritance is one way to implement that generalization. The key thing is the shared concept, not the syntax.

## Base classes capture common behavior

A base class is useful when several subtypes share real logic, not just field names.

```python
class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def sleep(self) -> None:
        print(f"{self.name} is sleeping")


class Dog(Animal):
    def bark(self) -> None:
        print("woof")
```

`Dog` inherits `sleep()` because that behavior belongs to the broader concept, not because inheritance is fashionable.

## Abstract classes represent incomplete concepts

Some classes exist to define shared behavior or contracts but are not meaningful to instantiate directly. A base `PaymentMethod` or `Shape` may exist only so concrete subtypes can fill in the missing pieces.

That is why many languages support abstract classes. They let you share structure without pretending the base type is a finished real-world object.

## Inheritance couples subtypes to base-class decisions

The downside of inheritance is tight coupling. Subclasses inherit not just useful behavior, but also assumptions, naming, lifecycle, and extension points from the base class.

That makes base classes expensive to change. A bad base class can spread design mistakes through every subtype.

## Code reuse alone is a weak reason

One of the most common inheritance mistakes is using it just to avoid duplication. Shared code is nice, but if the subtype is not conceptually a true specialized version of the base type, the hierarchy becomes brittle.

Composition often beats inheritance when the real goal is reuse rather than a clean subtype relationship.

## Subtypes must preserve expectations

If code expects a `BankAccount`, any subtype should still behave like a valid bank account. If the subtype breaks the expectations of the parent type, the hierarchy is lying.

That is why inheritance is partly a semantic promise. The subtype relationship has to make sense to callers, not just to the compiler.

## Prefer shallow, meaningful hierarchies

One or two levels of inheritance are often manageable. Deep inheritance trees are usually harder to understand because behavior comes from many places and override rules become subtle.

When a hierarchy starts feeling like a puzzle, that is often a sign to step back and consider interfaces, composition, or simpler modeling choices.
