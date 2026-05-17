## Coupling

The degree to which one class depends on the internals of another. Low coupling means classes interact through narrow, well-defined interfaces — a change inside one class does not ripple through others. High coupling means classes reach deep into each other's implementation, making them fragile and hard to change independently.

```java
// High coupling — OrderService knows the internal structure of Database
orderService.getDatabase().getConnection().executeQuery("...");

// Low coupling — OrderService only knows OrderRepository's interface
orderRepository.findByStatus("pending");
```

## Cohesion

The degree to which the members of a class belong together. High cohesion means every field and method contributes to a single, focused purpose. Low cohesion means the class mixes unrelated responsibilities — a signal that it should be split.

```java
// Low cohesion — printing and persistence have nothing to do with each other
public class UserManager {
    public void createUser(String name) { /* ... */ }
    public void printReport()           { /* ... */ }
    public void backupDatabase()        { /* ... */ }
}

// High cohesion — one focused purpose
public class UserRepository {
    public void create(String name) { /* ... */ }
    public User findById(int id)    { /* ... */ }
    public void delete(int id)      { /* ... */ }
}
```

Coupling and cohesion are two sides of the same coin: high cohesion inside a class leads to low coupling between classes.

## Separation of concerns

Dividing a system so that each module addresses a distinct concern — UI, business logic, persistence, validation — without mixing them. When concerns are separated, a change to the database layer does not ripple into the presentation layer.

```text
┌────────────┐     ┌─────────────────┐     ┌────────────────┐
│ Controller │ --> │  Service Layer   │ --> │  Repository    │
│ (HTTP)     │     │  (Business rules)│     │  (SQL/storage) │
└────────────┘     └─────────────────┘     └────────────────┘
```

Each layer knows about the one below it but not above it, keeping each concern independently testable and replaceable.

## Conceptual integrity

A system designed as if one mind conceived it: consistent naming, uniform patterns, predictable behavior. When every module follows the same conventions for error handling, naming, and structure, developers can navigate unfamiliar code quickly because it behaves like code they already know.

Conceptual integrity is maintained by code reviews, shared style guides, and deliberate resistance to ad-hoc special cases — even when the special case would be slightly shorter.

## Principle of Least Knowledge (Law of Demeter)

An object should only talk to its immediate neighbors: its own fields, parameters it receives, objects it creates, and its own methods. It should not reach through an object to access a third object — that creates hidden coupling to the inner structure.

```java
// Violates Demeter — reaches through customer to address to city
String city = order.getCustomer().getAddress().getCity();

// Follows Demeter — ask the order directly
String city = order.getShippingCity();
```

The second version hides the internal structure. If `Customer` stops having a separate `Address` object tomorrow, only `Order` needs to change — not every caller.

## Tell, Don't Ask

Instead of querying an object's state, making a decision externally, and then calling back to tell it what to do, just tell the object what to do and let it use its own state internally. This keeps behavior and state together — the core idea of encapsulation.

```java
// Ask (procedural) — caller makes the decision
if (account.getBalance() >= amount) {
    account.setBalance(account.getBalance() - amount);
}

// Tell (OOP) — object makes the decision
account.withdraw(amount);  // throws if insufficient funds
```

## DRY (Don't Repeat Yourself)

Every piece of knowledge should have a single, unambiguous representation in the system. When the same logic is copy-pasted across three classes, a bug fix must be applied three times — and the third copy will inevitably be missed.

DRY is about knowledge, not characters. Two code blocks that look similar but model different domain rules are not duplication. Two code blocks that look different but encode the same rule are. The fix for genuine duplication is usually extracting a shared method or class.
