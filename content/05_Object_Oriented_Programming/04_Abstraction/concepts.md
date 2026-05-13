## Abstraction is selective hiding

An abstraction is a simplified view of something more complicated. It exposes the operations and concepts callers need while hiding the details they do not need to think about every time.

In OOP, abstraction is what lets you work with an `Order`, `Cache`, `File`, or `Queue` without carrying the full implementation in your head. The goal is not to hide everything; the goal is to hide the right things.

## Good abstractions match the problem domain

A useful abstraction names the concept the software actually cares about. If your system thinks in orders, invoices, subscriptions, and payments, those should usually appear in the model more readily than low-level tables, JSON blobs, or transport shapes.

This is why "good names" are not cosmetic. A class called `Subscription` tells the reader more than `SubscriptionDataManagerThing`, and it points at the role the object is supposed to play in the domain.

## Public API, private mechanics

Abstraction usually shows up as a clean public API over messier internals. A caller should be able to say `cart.add_item(product)` or `report.generate()` without needing to know which helper methods run, how values are cached, or how persistence is implemented.

```python
class ShoppingCart:
    def __init__(self) -> None:
        self._items = []

    def add_item(self, product, quantity: int = 1) -> None:
        self._items.append((product, quantity))

    def total_items(self) -> int:
        return sum(quantity for _, quantity in self._items)
```

The abstraction is not `_items`; the abstraction is "a cart you can add items to and ask about." Internal storage can change later if the public meaning stays stable.

## Abstraction is not just renaming

Bad abstractions often take low-level work and wrap it in a class without changing the mental model. If callers still need to know every implementation detail, the abstraction is mostly cosmetic.

For example, a method named `process_order()` that requires the caller to manually set ten flags in the correct order is not a strong abstraction. It has a nicer name, but it has not actually reduced complexity for the caller.

## The right level of detail matters

Abstractions fail in two directions:

- **Too low-level** — callers must care about internals they should not have to manage.
- **Too high-level** — the abstraction becomes vague, overloaded, or impossible to use precisely.

A good abstraction sits at the level where the caller can express intent clearly. `send_welcome_email(user)` is often a better abstraction than exposing SMTP session steps; `PaymentMethod` is often a better abstraction than one giant `SystemManager` that does everything.

## Leaky abstractions are real

An abstraction is **leaky** when callers constantly have to know the internals anyway. Maybe a repository abstraction still forces callers to think in SQL transaction quirks, or a `FileStorage` abstraction still requires knowledge of local paths versus S3 keys at every call site.

Leaky abstractions are not always avoidable, but they are a warning sign. If every caller has to understand the machinery below the API, the API is not buying much simplification.

## Abstract what is stable, not what is accidental

Good abstractions usually form around stable concepts: order status, authentication, pricing policy, storage, queueing, scheduling. Bad abstractions often form around accidental current details like "this happens to be a CSV parser today" or "this uses service X right now."

That is why abstractions help with change. If your code depends on a stable concept like `PaymentGateway`, you can swap Stripe for another provider more cleanly than if the whole codebase is full of direct Stripe-specific assumptions.

## Callers should express intent, not procedure

One test for a good abstraction is whether the caller gets to say *what* it wants instead of *how* to do it. `invoice.mark_paid()` expresses intent. A sequence like `invoice.status = "paid"; invoice.paid_at = now(); invoice.send_receipt = True` pushes procedural details back onto the caller.

That distinction matters because once many callers know the procedure, changing the procedure becomes expensive. A stronger abstraction centralizes it.

## Abstraction and encapsulation are related, but not identical

These two ideas are easy to blur together. **Abstraction** is about presenting the right model and hiding irrelevant detail. **Encapsulation** is about controlling access to state and behavior so the object can protect its own rules.

In practice they often reinforce each other. A class with a clean abstraction usually also encapsulates its internals well. But the mental questions are different: abstraction asks "what should callers see?" while encapsulation asks "what should callers be allowed to touch?"
