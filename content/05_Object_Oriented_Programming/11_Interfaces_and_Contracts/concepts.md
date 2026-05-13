## An interface is a promise

An interface defines what operations a type supports without committing to one implementation. In plain terms, it says "anything that satisfies this contract can be used here."

That makes interfaces useful wherever you want to depend on capabilities rather than concrete classes.

## Contracts matter more than concrete types

If a caller only needs "something that can send notifications," then depending on `Notifier` is cleaner than depending directly on `EmailNotifier`.

This keeps the caller focused on what it needs done instead of which specific class happens to do it today.

## Interfaces support substitution

Once multiple implementations satisfy the same interface, you can swap them with less friction: fake implementations in tests, alternate providers in production, specialized variants for certain workflows.

That flexibility is one of the strongest reasons interfaces exist at all.

## Small interfaces are usually better

Large "do everything" interfaces force callers to depend on methods they do not actually need.

```python
class PaymentProvider:
    def authorize(self): ...
    def capture(self): ...
    def refund(self): ...
    def export_csv(self): ...
    def sync_to_erp(self): ...
```

This kind of interface often mixes unrelated responsibilities. Smaller, focused contracts are easier to implement and easier for callers to use correctly.

## Interfaces are about stable behavior

Good interfaces form around operations that are likely to stay meaningful over time: `send()`, `save()`, `publish()`, `calculate_total()`, `retry()`. Bad interfaces often mirror temporary implementation details.

The more stable the concept, the more valuable the contract.

## Interfaces help testing without hardcoding mocks everywhere

If code depends on a contract like `Clock`, `PaymentGateway`, or `EmailSender`, tests can provide simple fake implementations instead of setting up real external systems.

That does not make interfaces a testing trick. It means good contracts naturally make isolated tests easier.

## Contract design affects everything downstream

Once many callers depend on an interface, changing it becomes expensive. That is why interface design deserves care: bad names, awkward method shapes, or mixed responsibilities spread pain widely.

A stable contract is one of the most valuable assets in a large codebase.

## Not every abstraction needs a formal interface

Some languages support explicit interfaces; others rely on duck typing, protocols, or conventions. The design idea still holds either way.

Use formal interfaces where substitution, clarity, or dependency boundaries matter. Do not introduce them automatically when one concrete class is enough.
