## Instance members belong to one object

Instance members are fields and methods tied to a specific object. `account.balance` belongs to one `BankAccount`; `todo.done` belongs to one `TodoItem`.

That is the default mental model in OOP: most useful state lives on instances.

## Class-level members belong to the type itself

Class-level members, often called **static** members, are shared across all instances of the class. They can be useful for constants, counters, registries, or helper factories.

```python
class Order:
    next_id = 1

    def __init__(self) -> None:
        self.id = Order.next_id
        Order.next_id += 1
```

Here `next_id` belongs to the class, while `id` belongs to each instance.

## Use class-level members for shared meaning

Good class-level values include constants like status labels, shared configuration knobs, or sequence counters that are intentionally global to the type.

If the data should vary from one object to another, it usually belongs on the instance instead.

## Shared mutable state is powerful and dangerous

Because class-level mutable data is shared, changes in one place affect every instance. That can be useful, but it can also create hidden coupling and surprising behavior.

This is one reason static-heavy designs can become brittle quickly.

## Static helpers are not automatically bad

Small utility methods that do not need instance state can be perfectly fine as class-level or static methods. The problem is not the feature; the problem is using static structure to avoid modeling real object relationships.

If everything becomes a static utility, you stop getting many of the benefits of OOP.

## Prefer instance behavior when the rule depends on object state

If the logic depends on `self` or on the identity of a particular object, make it an instance method. Using a static helper for object-specific behavior often forces callers to pass the object around manually, which weakens encapsulation.

That usually means the behavior belongs on the object itself.

## Class-level state changes design pressure

Any shared state raises questions about concurrency, lifecycle, test isolation, and hidden dependencies. These concerns appear even in small programs.

That does not ban class-level state. It means you should treat it as shared infrastructure, not as harmless convenience.

## Pick the level that matches the concept

If the information belongs to each object, use an instance member. If it belongs to the type as a whole, use a class-level member. Keeping those meanings clear prevents subtle bugs and confusing APIs.
