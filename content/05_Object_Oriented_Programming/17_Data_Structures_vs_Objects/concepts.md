## Objects combine data and behavior

An object is meant to carry both state and the operations that preserve or interpret that state. A `Cart` that knows how to add items and compute totals is an object in the OOP sense.

That pairing is what gives objects much of their value: the rules travel with the data they govern.

## Data structures mainly expose data

A data structure primarily stores values and lets external code decide what to do with them. Dictionaries, records, tuples, DTOs, and plain serialized payloads often fit this pattern.

That is not bad. It is just a different design choice.

## Anemic models look like objects but act like records

An anemic model is a class whose main job is to expose fields while real behavior lives elsewhere.

```python
class Invoice:
    def __init__(self, items):
        self.items = items


def total(invoice: Invoice) -> float:
    return sum(item.price for item in invoice.items)
```

This is sometimes fine, but if all meaningful logic about `Invoice` lives outside the class, the design is not getting much benefit from OOP.

## Rich objects own their rules

A richer object model puts calculations, validation, and transitions where they naturally belong.

```python
class Invoice:
    def __init__(self, items):
        self.items = items

    def total(self) -> float:
        return sum(item.price for item in self.items)
```

The object now owns a rule that clearly belongs to it.

## Use data structures at boundaries

Data structures are often the right choice at boundaries: API payloads, database rows, message-queue events, CSV imports, and configuration blobs.

In those places, the goal is often transport or serialization rather than behavior-rich modeling.

## Use objects where rules accumulate

If a concept has invariants, lifecycle, state transitions, and meaningful domain behavior, it often wants to be an object rather than a passive record.

That is especially true when many callers would otherwise keep reimplementing the same logic.

## Mixing both styles is normal

Most real systems contain both objects and data structures. An API request may be parsed into a DTO, then translated into domain objects, then later flattened again for output.

The key is using each style deliberately instead of pretending one style fits every layer equally well.

## The question is not "which is pure?"

The practical question is simpler: where should the rule live? If the answer is "inside the concept that owns the state," you likely want an object. If the answer is "this is just data crossing a boundary," a simpler structure may be enough.
