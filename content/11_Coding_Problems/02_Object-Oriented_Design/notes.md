# Object-Oriented Design

A design interview is a conversation that ends in a few types, the relationships between them, and one scenario you can walk as messages. The mechanics underneath that conversation are the usual object rules: hide the data behind the invariant, inherit only when a child can stand in for the parent, and vary behavior by swapping a collaborator. Patterns are names for those swaps (a policy, a listener, a wrapper, a state), not a pile of classes you announce up front.

## Key Points

- **Handle ambiguity** — state who acts, which rules you will enforce, and what is out of scope, then design against that. Name the trade-off you are deferring.
- **Define the core objects** — a type owns changing state or a cluster of decisions. Barcodes, counts, and durations are fields.
- **Analyze relationships** — say has-a, knows-a, or is-a, and say the cardinality. Most arrows are not inheritance.
- **Investigate actions** — the method lives on the object that has the data. Walk one scenario, including the refusal.
- **Encapsulation** — callers use operations. The owning type is the only code that can break, or protect, the invariant.
- **Inheritance** — a child must be usable wherever the parent is. Overriding a method to reject the parent's inputs breaks that.
- **Polymorphism** — callers invoke a method on the interface. A switch on type names is the design you are trying to leave.
- **Composition over inheritance** — a cup has additions; it is not a subclass per combination. The cage has a fee policy.
- **Interfaces vs abstract classes** — an interface is a capability with no shared representation. An abstract class earns its place when real code and fields are shared.
- **SOLID** — one reason to change, extend by new types, subtypes that substitute, small interfaces, and high-level code that depends on those interfaces.
- **Singleton** — one global instance. It hides a dependency and couples tests. Pass the object in unless there really is only one.
- **Factory method** — one place decides which concrete type to build. Callers keep the interface. Use a subclass hook only when the surrounding steps are shared.
- **Strategy** — an interchangeable algorithm in a field. Worth it when the rule will grow; noise when it will not.
- **Observer** — the subject notifies listeners and does not import them. Remove listeners, and do not promise an order you did not specify.
- **Decorator and Adapter** — a decorator adds behavior behind the same interface and can stack. An adapter translates a foreign interface. Do not mix the two jobs.
- **State machines** — name states and legal events first. A table is easy to audit; a state object is worth it when each state has real behavior.
- **Extensibility, said out loud** — "a new fee is a new strategy, and the cage does not change. I am not adding storage in this pass." That sentence is the trade-off.

## Example

```python
"""A bike cage: the fee is a strategy, stock-style capacity is encapsulated, listeners hear a full cage."""


class MemberFlat:
    def price(self, hours: int) -> int:
        return 0


class EventHourly:
    def __init__(self, cents_per_hour: int) -> None:
        self.cents_per_hour = cents_per_hour

    def price(self, hours: int) -> int:
        return hours * self.cents_per_hour


class BikeCage:
    def __init__(self, capacity: int, fee) -> None:
        if capacity < 1:
            raise ValueError("capacity")
        self._capacity = capacity
        self._parked = 0
        self.fee = fee
        self._listeners: list = []

    def listen(self, fn) -> None:
        self._listeners.append(fn)

    def park(self, hours: int) -> str:
        if self._parked >= self._capacity:
            for fn in self._listeners:
                fn("full")
            return "refused"
        self._parked += 1
        return f"parked:{self.fee.price(hours)}"


events: list[str] = []
cage = BikeCage(1, EventHourly(200))
cage.listen(events.append)
print(cage.park(2))          # parked:400
print(cage.park(1))          # refused
print(events)                # ['full']
print(BikeCage(1, MemberFlat()).park(5))  # parked:0
```

The cage does not know which fee is installed, does not let callers set `_parked` directly, and does not import the thing that records a full cage. A second fee is a new class. A second listener is a new `listen` call. Both leave `park` alone.

## More practice

Work the original exercises on the **Drills** tab. They walk a bike cage, a tool library, an office lift, a tool dispenser, and a small card-game scoring rule. Each one asks for the types, the relationship, or the pattern, and then checks the answer in a short Python model.
