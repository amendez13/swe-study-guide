## Why objects at all

The argument for object-oriented programming is not "the real world has objects, so code should too." The real argument is that non-trivial programs accumulate **state**, **rules**, and **collaboration** between parts, and objects are one way to keep those concerns packaged together instead of scattering them across functions.

You can build perfectly good software without OOP. The point is that once a program has long-lived domain state like accounts, orders, carts, users, or documents, an object model often gives you a clearer place to put the rules that govern that state.

## Object = state plus behavior

An object is not just a bag of fields. It is state plus the operations that are allowed to read or change that state.

```python
class BankAccount:
    def __init__(self, balance: float = 0) -> None:
        self.balance = balance

    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
```

The important OOP move here is not the class syntax. It is that the "no overdraft" rule lives with the account instead of being something every caller has to remember.

## Public methods are the contract

Good objects give other code a small public API and keep the internal representation flexible. Callers should care that an `Order` can calculate its total or that a `User` can change a password, not whether those classes store values in one list, three fields, or a cached dictionary.

This is why encapsulation matters. If every caller reaches in and edits raw fields directly, changing the internals later becomes dangerous because the whole codebase now depends on those details.

## Put the rule where the data lives

A common beginner mistake is to store data in one place and put all the logic somewhere else. That usually produces code where the real rules are spread across helpers, services, and utility functions.

```python
# weak model: the rule lives outside the order
def apply_discount(order, percent):
    order.total = order.total * (1 - percent)


# stronger model: the order owns the rule
class Order:
    def __init__(self, total: float) -> None:
        self.total = total

    def apply_discount(self, percent: float) -> None:
        if not 0 <= percent <= 1:
            raise ValueError("discount must be between 0 and 1")
        self.total = self.total * (1 - percent)
```

The second version is not automatically perfect, but it has the right shape: the object that owns the data also owns the rule that keeps it valid.

## "Tell, don't ask"

One useful OOP instinct is "tell, don't ask." Instead of pulling data out of an object, making a decision elsewhere, and then pushing new data back in, prefer telling the object what you want done and letting it enforce its own rules.

For example, `cart.add_item(product, qty)` is usually better than external code doing `cart.items.append(...)` and recomputing totals by hand. The caller describes the intent; the object handles the mechanics and invariants.

## Entity vs value object

Not every object is important for the same reason.

- An **entity** has identity over time. Two `User` objects with the same name are still different users if they have different IDs.
- A **value object** is defined by its value, not its identity. Two `Money(currency="USD", amount=10)` values are interchangeable.

This distinction helps you model systems more clearly. Entities usually have lifecycle and persistence concerns; value objects are often smaller, safer, and easier to compare or reuse.

## Rich object vs anemic model

An object model is called **anemic** when classes mostly expose fields and the real behavior lives elsewhere. That is often a sign that the code is using class syntax without getting much benefit from object-oriented design.

```python
class Invoice:
    def __init__(self, items):
        self.items = items


def invoice_total(invoice: Invoice) -> float:
    return sum(item.price for item in invoice.items)
```

Sometimes this is acceptable, but if every important rule for `Invoice` lives outside the class, the "object" is mostly acting like a record. A richer model would let `Invoice` own calculations, validation, and state transitions that belong to it.

## Good OOP makes common changes local

The best test of an object model is not whether the class hierarchy looks elegant. The best test is what happens when requirements change. If adding a discount rule means editing one `Order` class, that is a good sign. If it means hunting through route handlers, report generators, serializers, and utility functions, the model is weak.

That is the real promise of OOP: not beauty, not ceremony, but **localized change**. A good object boundary gives you one obvious place to put new behavior and one obvious place to protect old invariants.
