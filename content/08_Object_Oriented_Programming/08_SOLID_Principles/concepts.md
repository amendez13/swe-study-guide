## Single Responsibility Principle (SRP)

A class should have only one reason to change — it should encapsulate exactly one concern. When a class mixes responsibilities (e.g., business logic and persistence), a change in one area forces a change in the other, increasing risk and reducing reusability.

```java
// Violates SRP — report logic and file I/O in one class
public class Report {
    public String generate(Data data) { return "..."; }
    public void saveToFile(String content) { /* file I/O */ }
}

// Follows SRP — separate concerns
public class Report {
    public String generate(Data data) { return "..."; }
}

public class ReportSaver {
    public void save(String content, Path path) { /* file I/O */ }
}
```

A good heuristic: describe what the class does in one sentence without using "and." If you need "and," it probably has two responsibilities.

## Open/Closed Principle (OCP)

Classes should be open for extension but closed for modification. New behavior is added by creating new subtypes or implementations, not by editing existing source code. This keeps proven, tested code stable while still allowing growth.

```java
public interface DiscountPolicy {
    double apply(double price);
}

public class SeasonalDiscount implements DiscountPolicy {
    public double apply(double price) { return price * 0.85; }
}

// Adding a new discount never touches existing classes:
public class LoyaltyDiscount implements DiscountPolicy {
    public double apply(double price) { return price * 0.90; }
}
```

The key enabler is abstraction: if you program to an interface, adding new behavior is a matter of adding a new implementation, not changing a switch statement.

## Liskov Substitution Principle (LSP)

Subtypes must be substitutable for their base types without altering the correctness of the program. If code works with a `Bird`, it must work correctly with any subclass of `Bird`. A subclass that throws unexpected exceptions, ignores method contracts, or violates preconditions/postconditions breaks LSP.

```java
// Classic violation:
public class Bird {
    public void fly() { /* ... */ }
}

public class Penguin extends Bird {
    @Override
    public void fly() {
        throw new UnsupportedOperationException();  // surprise!
    }
}
```

The fix is usually a better hierarchy. Not every bird flies — separate the contract (`Flyable` interface) from the class so non-flying birds don't inherit a promise they can't keep.

## Interface Segregation Principle (ISP)

Clients should not be forced to depend on methods they do not use. A fat interface that bundles unrelated operations forces implementors to provide stubs or throw exceptions for methods that are irrelevant to them. Prefer several small, focused interfaces.

```java
// Fat interface
public interface Worker {
    void code();
    void attendMeetings();
    void writeReports();
}

// Segregated
public interface Coder      { void code(); }
public interface Attendee   { void attendMeetings(); }
public interface Reporter   { void writeReports(); }

public class Developer implements Coder, Attendee {
    public void code()            { /* ... */ }
    public void attendMeetings()  { /* ... */ }
    // Does not implement writeReports() — not its job
}
```

## Dependency Inversion Principle (DIP)

High-level modules should not depend on low-level modules; both should depend on abstractions. And abstractions should not depend on details; details should depend on abstractions.

```java
// Violates DIP — high-level OrderService depends on concrete MySqlRepo
public class OrderService {
    private MySqlOrderRepo repo = new MySqlOrderRepo();
}

// Follows DIP — both depend on the abstraction
public interface OrderRepository {
    void save(Order order);
}

public class OrderService {
    private final OrderRepository repo;
    public OrderService(OrderRepository repo) { this.repo = repo; }
}

public class MySqlOrderRepo implements OrderRepository {
    public void save(Order order) { /* SQL */ }
}
```

DIP enables swapping implementations (MySQL to Postgres, real to mock) without touching the business logic. It is the principle that makes dependency injection and testability practical.

## SOLID as a system

The five principles reinforce each other. SRP keeps classes focused, OCP makes them extensible, LSP keeps hierarchies honest, ISP keeps interfaces lean, and DIP points dependencies toward abstractions. Violating one often cascades: a class with too many responsibilities (SRP) tends to have a fat interface (ISP) and concrete dependencies (DIP).

The principles are guidelines, not laws. Applying them rigidly to trivial code creates unnecessary abstraction. They pay off most in code that is shared, long-lived, or frequently extended.
