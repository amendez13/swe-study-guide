## Overloading is one name, multiple signatures

Method overloading means several methods share a name but differ in parameter types or counts. Languages like Java and C# support this directly.

This is a convenience feature. It can make APIs nicer, but it is not the same thing as polymorphism by itself.

## Overriding means a subtype replaces behavior

Overriding happens when a subclass provides its own implementation of a method defined by a parent class.

```python
class Animal:
    def speak(self) -> str:
        return "..."


class Dog(Animal):
    def speak(self) -> str:
        return "woof"
```

The `Dog` implementation replaces the parent behavior for dog instances.

## Dynamic dispatch chooses the method at runtime

Dynamic dispatch is the runtime mechanism that picks the correct overridden method based on the actual object type.

That is what lets code call `animal.speak()` once and still get different behavior for dogs, cats, or birds.

## Overloading is about call shape; overriding is about behavior variation

These ideas are often confused because the names sound similar. Overloading gives multiple entry points with the same name. Overriding changes what one shared method means for a subtype.

Only overriding participates directly in classic subtype polymorphism.

## Overriding must preserve the parent's expectations

When a subtype overrides a method, it should still honor the contract callers expect from the parent. If the override changes the meaning too radically, the hierarchy becomes unsafe.

This is where inheritance design gets serious: overriding is not just a syntax trick, it is a behavioral promise.

## Base methods may provide defaults or require specialization

Some parent methods contain useful default behavior. Others exist mainly to force subtypes to implement them. Both patterns are common.

The design question is whether the shared contract and default behavior really belong in the parent type.

## Overriding can make behavior harder to trace

Deep hierarchies with many overrides make it harder to know what code will actually run. Readers must understand parent classes, subclass behavior, and dispatch rules together.

That is why inheritance-heavy systems can become difficult to reason about over time.

## Use these tools where the variation is real

If you do not have meaningful subtype-specific behavior, overriding may be unnecessary. If a single method with optional parameters is enough, overloading may be unnecessary too.

Choose the mechanism that matches the actual variation in the model, not the most "OOP-looking" one.
