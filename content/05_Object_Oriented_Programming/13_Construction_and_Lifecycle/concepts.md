## Construction creates usable objects

Construction is not just "allocate memory and move on." It is the point where an object should enter the world in a valid, usable state.

If callers must remember three extra setup steps after construction before the object is safe, the design is already fighting them.

## Constructors enforce required inputs

Constructors are one of the best places to demand the data an object genuinely needs.

```python
class Order:
    def __init__(self, order_id: str, customer_id: str) -> None:
        self.order_id = order_id
        self.customer_id = customer_id
```

That is better than creating a half-empty object and hoping every caller fills in the missing fields later.

## Defaults are only good when they mean something

Default values are useful when an empty or initial state is genuinely valid: an empty cart, a zero balance, an empty notes list.

They are dangerous when they let an object exist in a meaningless state. If the object cannot function without a value, force the caller to provide it.

## Construction is where invariants begin

Many invariants should be enforced at creation time, not only later. If an email must contain `@`, or a discount must be between `0` and `1`, the constructor is a natural place to validate that.

That keeps invalid objects from existing at all.

## Lifecycle ownership matters

Some objects are created and discarded locally. Others are long-lived, persisted, retried, resumed, or shared across workflows. That lifecycle affects how you design creation, cleanup, and replacement.

If one object owns another object's lifecycle, that ownership should usually be visible in the model.

## Factories can clarify complicated creation

When construction logic grows beyond a few fields, a factory or named constructor can make intent clearer.

```python
class User:
    def __init__(self, email: str, is_admin: bool) -> None:
        self.email = email
        self.is_admin = is_admin

    @classmethod
    def admin(cls, email: str):
        return cls(email=email, is_admin=True)
```

This can be clearer than pushing many optional flags into one overloaded constructor.

## Initialization work should not surprise callers

If object creation opens sockets, hits the database, or performs expensive I/O, the constructor may be hiding too much. Creation becomes harder to reason about and harder to test.

Keep heavy side effects visible unless there is a strong reason not to.

## Objects should have an obvious lifetime story

A good design makes it clear who creates the object, who owns it, who may mutate it, and when it is done. If that story is fuzzy, bugs around stale state, reuse, and cleanup become more likely.

Construction is the first chapter of lifecycle design, not a separate concern.
