## State is what can change

In OOP, **state** is the data an object holds right now: a bank account's balance, an order's status, a user's email, a cart's items. If the object exists over time, its state is what changes as the program runs.

State matters because most business rules are really rules about state: what values are allowed, what transitions are legal, and what must stay true after an operation completes.

## Behavior is how the object changes state

**Behavior** is the set of methods an object exposes to read or change its state. `deposit()`, `cancel()`, `ship()`, `rename()`, and `mark_done()` are all examples of behavior.

The point of attaching behavior to the object is that the object can enforce its own rules while the state changes. That is much safer than letting every caller manipulate raw fields and hope they all remember the same invariants.

## Invariants are the rules you must not break

An **invariant** is something that should remain true for a valid object. A balance should not go negative if overdrafts are forbidden. An order marked `shipped` should not still be editable. A percentage should stay between `0` and `1`.

```python
class PercentageDiscount:
    def __init__(self, percent: float) -> None:
        if not 0 <= percent <= 1:
            raise ValueError("percent must be between 0 and 1")
        self.percent = percent
```

If the object does not protect its invariants, the burden shifts to every caller. That usually means the rule will be duplicated in some places, forgotten in others, and eventually violated.

## State transitions should be explicit

Many useful objects are really small state machines. An `Order` moves from `draft` to `paid` to `shipped`; a `Task` moves from `todo` to `in_progress` to `done`.

```python
class Task:
    def __init__(self) -> None:
        self.status = "todo"

    def start(self) -> None:
        if self.status != "todo":
            raise ValueError("only todo tasks can start")
        self.status = "in_progress"

    def finish(self) -> None:
        if self.status != "in_progress":
            raise ValueError("only in-progress tasks can finish")
        self.status = "done"
```

Named methods like `start()` and `finish()` are better than random external assignments to `status` because they make legal transitions obvious and illegal ones enforceable.

## Queries vs commands

A useful mental split is **queries** vs **commands**. Queries answer questions without changing state, like `total()` or `is_overdue()`. Commands change state, like `pay()`, `archive()`, or `withdraw()`.

Keeping that distinction clear makes objects easier to reason about. If every method both mutates state and computes values as a side effect, the object becomes harder to trust and harder to test.

## Responsibility answers "why does this class exist?"

Responsibility is the core design question behind a class. A good class exists for one coherent reason: represent an order, calculate pricing, manage a queue, validate an email address, schedule a retry.

If you cannot explain a class's job in one sentence, the design is probably muddy. Responsibility is less about counting methods and more about whether those methods clearly belong together.

## One reason to change

The practical version of responsibility is the **one reason to change** test. If a class changes because pricing rules changed, that is one reason. If the same class also changes because the database schema changed, the email template changed, and the API shape changed, it is doing too much.

This is the design pressure behind the Single Responsibility Principle. It is not "one method per class"; it is "one coherent axis of change per class."

## Mixed responsibilities create fragile classes

Watch for classes that mix domain rules, persistence, formatting, and orchestration all at once.

```python
class Invoice:
    def calculate_total(self): ...
    def save_to_database(self): ...
    def send_email(self): ...
    def export_pdf(self): ...
```

Nothing is impossible about this class, but it is carrying too many concerns. A change in storage, email delivery, or PDF formatting now risks breaking invoice rules even though those concerns should evolve independently.

## Behavior belongs with the object that owns the rule

If a method exists only because another part of the system needs to preserve this object's validity, that method probably belongs on the object itself. An `Order` should usually know how to apply a discount; a `Password` object should usually know how to verify itself; a `Cart` should usually know how to compute its total.

This does not mean every line of logic must live inside the class. It means the class should own the rules that define what valid behavior for that object actually is.
