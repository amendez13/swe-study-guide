# Classes, Objects, and Instances

This topic is the mechanics layer of OOP. Once you accept that objects are a useful way to package state and behavior, the next question is how that packaging actually works at runtime: what the class defines, what each instance owns, and how construction establishes valid starting state.

## Key Points

- **Class vs instance** — the class is the definition; the instance is one concrete runtime object built from it.
- **Many instances, same behavior** — one class can produce many objects that share methods but carry different state.
- **Instance state** — attributes on one object should not leak into another object unless you intentionally share them.
- **Constructors** — object creation should leave the instance immediately usable and as close to valid as possible.
- **Required inputs vs defaults** — force required data at construction time; use defaults only when an empty or zero state is genuinely meaningful.
- **Identity vs value** — two objects can look the same and still be different entities.
- **Instance methods** — methods matter because they operate on one specific object's current state.
- **Class members** — static/class-level data is shared and useful, but it introduces coupling if overused.
- **When not to use a class** — if there is no meaningful behavior or lifecycle, a lighter data shape may be clearer.

## Example

```python
class BankAccount:
    next_account_number = 1

    def __init__(self, owner: str, opening_balance: float = 0) -> None:
        self.owner = owner
        self.balance = opening_balance
        self.account_number = BankAccount.next_account_number
        BankAccount.next_account_number += 1

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount


alice = BankAccount("Alice", 100)
bob = BankAccount("Bob", 50)
alice.deposit(25)

print(alice.account_number, alice.balance)  # 1 125
print(bob.account_number, bob.balance)      # 2 50
```

This example shows the whole stack in one place: `BankAccount` is the class, `alice` and `bob` are separate instances, `balance` is instance state, `deposit()` is instance behavior, and `next_account_number` is class-level shared state. That is the basic runtime model behind most object-oriented code.
