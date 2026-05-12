## Class vs object vs instance

A **class** is the definition: what data a thing has and what operations it supports. An **object** or **instance** is one runtime realization of that definition, with its own actual state in memory.

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name


alice = User("Alice")
bob = User("Bob")
```

`User` is the class. `alice` and `bob` are two distinct instances. That distinction matters because most OOP confusion starts when people talk about the blueprint and the runtime object as if they were the same thing.

## One class, many instances

The value of a class is that it lets you create many objects with the same shape and behavior but different state. Two `BankAccount` instances can both support `deposit()` and `withdraw()` while holding different balances.

This is what makes classes more than namespacing. A class is a reusable factory for stateful objects, not just a folder for related functions.

## Instance state lives on each object

Instance attributes belong to one object, not to the class as a whole. If `cart_a.items` changes, that should not silently mutate `cart_b.items`.

```python
class Counter:
    def __init__(self) -> None:
        self.value = 0


a = Counter()
b = Counter()
a.value += 1
print(a.value, b.value)  # 1 0
```

That isolation is the point. Each instance carries its own state, which is why objects are useful for modeling many independent entities at once.

## Constructors establish valid starting state

A constructor is the code that creates an object and puts it into a usable initial state. In Python that is usually `__init__`; in Java or C# it is an explicit constructor method with the class name.

Good constructors make invalid states hard to create. If an `EmailAddress` must contain `@`, or an `Order` must start with a customer ID, the constructor is one of the first places to enforce that rule.

## Default construction vs required inputs

Some classes can safely start from defaults like an empty list or zero balance. Others are meaningless unless the caller provides real inputs.

```python
class Order:
    def __init__(self, order_id: str, customer_id: str) -> None:
        self.order_id = order_id
        self.customer_id = customer_id
```

If a class cannot do its job without certain values, forcing those values at construction time is usually better than creating a half-empty object and hoping callers remember to finish setup later.

## Identity is not the same as value

Two objects can have the same field values and still be different objects. That is identity. If two `User` instances both have `name="Alice"`, they are still different users if they were created separately or carry different IDs.

This matters for persistence, caching, relationships, and lifecycle. Equality by value is useful, but many domain objects matter because they are *this specific object over time*, not just because their fields match right now.

## Methods operate on instance state

Instance methods are useful because they automatically act on the current object. In Python, `self` is the current instance; in Java and C#, `this` plays the same role.

```python
class TodoItem:
    def __init__(self, title: str) -> None:
        self.title = title
        self.done = False

    def mark_done(self) -> None:
        self.done = True
```

`mark_done()` is meaningful because it changes the state of one specific `TodoItem`. That is the everyday mechanics of OOP: methods are behavior attached to an individual object.

## Instance members vs class members

Instance members belong to each object. Class members (often called **static** members) belong to the class itself and are shared across all instances.

```python
class RequestId:
    next_id = 1

    def __init__(self) -> None:
        self.id = RequestId.next_id
        RequestId.next_id += 1
```

Class members are useful for shared constants, factories, or counters, but they should be used deliberately. Shared mutable state can create hidden coupling fast.

## When a class is overkill

Not every concept needs a class. If you only need a short-lived bundle of values with no real behavior, a tuple, dictionary, dataclass, or plain record type may be enough.

Reach for a class when you need repeated instances, meaningful state transitions, or behavior that belongs with the data. Reach for a lighter structure when the object model adds ceremony without adding clarity.
