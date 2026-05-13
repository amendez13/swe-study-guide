## Composition means building from collaborators

Composition is the practice of assembling behavior by combining objects instead of inheriting from one large base class. One object delegates parts of its work to collaborators it owns or receives.

This often produces designs that are easier to change because the pieces are more loosely coupled.

## Use inheritance for subtype meaning, composition for reuse

Inheritance is strongest when the subtype relationship is semantically true. Composition is often better when the real goal is to reuse behavior or vary one part of the implementation.

That is why "favor composition over inheritance" is good default advice. It is safer to wire objects together than to commit to a rigid hierarchy too early.

## Composition makes dependencies explicit

With composition, you can see what an object relies on because those collaborators are fields or constructor arguments.

```python
class ReportService:
    def __init__(self, formatter, exporter) -> None:
        self.formatter = formatter
        self.exporter = exporter
```

This is often clearer than inheriting hidden behavior from a large base class with implicit expectations.

## Swapping one part becomes easier

If behavior is composed from collaborators, you can often replace just one piece. Use a different formatter, storage backend, pricing policy, or retry strategy without rewriting the rest of the class.

That kind of modularity is one of composition's biggest strengths.

## Composition avoids fragile base classes

Inheritance can create fragile designs where subclasses accidentally depend on subtle parent behavior. Composition reduces that risk because the relationship is usually narrower and more explicit.

The object uses the collaborator through a clear API instead of inheriting all of its assumptions.

## Strategy is composition in action

One classic example is a strategy object:

```python
class FlatRateShipping:
    def cost(self, total: float) -> float:
        return 5.0


class FreeShippingOver100:
    def cost(self, total: float) -> float:
        return 0.0 if total >= 100 else 8.0
```

A checkout class can compose one of these shipping strategies instead of inheriting a different subclass per pricing rule.

## Composition can add indirection

Composition is not automatically simpler. Too many tiny wrapper objects can create a maze of delegation that is hard to trace.

The goal is not maximal decomposition. The goal is to split along meaningful, swappable seams.

## Prefer composition until inheritance clearly earns its keep

If you are unsure whether a relationship is a real subtype or just shared behavior, composition is usually the safer first choice. You can always introduce inheritance later if the model truly demands it.

Undoing a bad hierarchy is often harder than starting with collaborators.
