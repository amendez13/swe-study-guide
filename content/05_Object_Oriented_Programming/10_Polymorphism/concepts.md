## Polymorphism means one interface, many behaviors

Polymorphism is the ability to work with different concrete types through one shared contract. The caller does not need separate code paths for every subtype; it can ask each object to do the same thing and let the object choose the right behavior.

This is one of the biggest ways OOP reduces conditional logic and special-case branching.

## Subtype polymorphism is the classic form

The familiar OOP version is that subclasses override behavior from a base type.

```python
class Notification:
    def send(self, message: str) -> None:
        raise NotImplementedError


class EmailNotification(Notification):
    def send(self, message: str) -> None:
        print(f"Email: {message}")


class SmsNotification(Notification):
    def send(self, message: str) -> None:
        print(f"SMS: {message}")
```

Now callers can loop over `Notification` objects and call `send()` without caring which concrete subtype they received.

## Dynamic dispatch picks the concrete behavior

At runtime, the actual object type determines which implementation runs. That mechanism is called **dynamic dispatch**.

This matters because the caller writes against the contract once, and runtime binding chooses the right branch. You do not have to keep writing `if type == ...` checks everywhere.

## Polymorphism replaces type switches

Without polymorphism, code often looks like a big conditional:

```python
if channel == "email":
    send_email(message)
elif channel == "sms":
    send_sms(message)
elif channel == "push":
    send_push(message)
```

With polymorphism, you move those branching decisions into objects. The caller works with one interface, and new behavior is added by adding a new implementation instead of editing central dispatch code.

## Interface-based polymorphism is often cleaner

The shared contract does not have to come from inheritance alone. It can come from an interface, protocol, or any language mechanism that says "these types all support the same operations."

That flexibility matters because many good polymorphic designs do not need a deep class hierarchy.

## Polymorphism shifts extension cost

The big benefit is extension. Adding `PushNotification` becomes a matter of implementing the same contract, not rewriting every caller that currently knows about email and SMS.

That is why polymorphism pairs so naturally with the Open/Closed Principle: new variants come in by extension, not by patching central switch statements.

## The contract must stay coherent

Polymorphism only helps when the shared operation actually means the same kind of thing across implementations. If every subtype needs radically different parameters or returns wildly different meanings, the interface is probably wrong.

A weak shared contract creates fake polymorphism: the syntax lines up, but the design does not.

## Do not use polymorphism where a simple function is enough

Polymorphism is powerful, but it is not mandatory for every variation. If you only have one implementation, or if the branching is tiny and unlikely to grow, introducing interfaces and hierarchies may be overkill.

Use it when you have real variant behavior that deserves a stable shared contract.
