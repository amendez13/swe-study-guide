# OOP As a Modeling Approach

This topic is the reason object-oriented programming exists at all. Before inheritance, SOLID, or design patterns, the core question is simpler: when a program has long-lived state and rules around that state, where should those rules live?

## Key Points

- **Why objects** — objects are useful when a system has state, invariants, and collaboration that would otherwise be spread across unrelated functions.
- **State + behavior** — an object is not just fields; it is fields plus the operations that keep those fields meaningful.
- **Public API as contract** — callers should rely on methods like `withdraw()` or `apply_discount()`, not on internal storage details.
- **Put rules with data** — the object that owns the data should usually own the logic that keeps that data valid.
- **Tell, don't ask** — prefer telling an object what to do over pulling out its internals and manipulating them elsewhere.
- **Entity vs value object** — some objects matter because of identity over time; others are interchangeable if their values match.
- **Anemic model warning** — if classes mostly expose fields and behavior lives elsewhere, you may have records wearing OOP clothing.
- **Localized change** — the best object models make common changes land in one obvious place.

## Example

```python
class BankAccount:
    def __init__(self, owner: str, balance: float = 0) -> None:
        self.owner = owner
        self.balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount


account = BankAccount("Ava", 100)
account.deposit(50)
account.withdraw(30)
print(account.balance)  # 120
```

This example is tiny, but it captures the core OOP idea. `BankAccount` owns both the data (`owner`, `balance`) and the rules that protect it (`deposit`, `withdraw`). No caller has to remember how to check for overdrafts or negative amounts, because the object that owns the state also owns the invariants.
