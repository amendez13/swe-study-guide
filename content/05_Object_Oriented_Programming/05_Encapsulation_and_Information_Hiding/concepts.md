## Encapsulation means controlled access

Encapsulation is the idea that an object should control how its own state is read and changed. Instead of every caller editing raw fields directly, callers go through methods that preserve the object's rules.

This is not about making everything private for its own sake. It is about making illegal states harder to create and making valid operations obvious.

## Information hiding is about dependencies

Information hiding means callers should not depend on details they do not need. If a class stores items in a list today and a dictionary tomorrow, callers should not have to change as long as the public behavior stays the same.

That is the real payoff: fewer external dependencies on internals, which means safer refactors later.

## Public fields weaken invariants

If important fields are changed freely from the outside, the object loses control over its own validity.

```python
class BankAccount:
    def __init__(self, balance: float) -> None:
        self.balance = balance


account = BankAccount(100)
account.balance = -500  # no rule enforcement
```

This is why state that carries rules usually needs methods around it. A direct assignment has no place to validate intent.

## Methods are guarded entry points

Encapsulated objects expose methods like `deposit()`, `change_email()`, or `mark_paid()` instead of asking callers to manipulate state procedurally.

```python
class BankAccount:
    def __init__(self, balance: float) -> None:
        self._balance = balance

    def withdraw(self, amount: float) -> None:
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
```

The method is valuable because it is where the rule lives. It turns a raw field update into a meaningful domain operation.

## "Private" does not mean invisible magic

Most languages offer privacy tools such as `private`, `protected`, or naming conventions like `_balance` in Python. These are not magical safety by themselves; they are signals and barriers that steer callers toward the intended API.

Privacy is strongest when the API design is already clear. A messy API with private fields is still a messy API.

## Expose capabilities, not representation

Callers should usually ask what an object can do, not how it is stored. `cart.total_items()` is a better abstraction than forcing callers to inspect `cart._items`.

That separation lets you change representation without changing meaning. The internal data structure becomes an implementation choice instead of a public contract.

## Encapsulation reduces blast radius

When one object owns its own rules, a change to those rules usually lands in one place. If the validation logic is duplicated across callers, every rule change becomes a codebase-wide migration.

This is one of the quiet benefits of OOP: fewer places where a business rule can be accidentally implemented differently.

## Too much encapsulation can become ceremony

Not every field needs a getter and setter pair. If a type is just a simple value holder, wrapping every access in boilerplate methods may add noise without adding safety.

Use encapsulation where the object has real invariants or real behavior to protect. Do not turn it into ritual.
