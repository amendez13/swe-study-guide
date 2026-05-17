## Abstraction as a design principle

Abstraction means modeling only the characteristics of a real-world entity that are relevant to the problem at hand and ignoring everything else. A `BankAccount` class needs a balance and an owner — it does not need the account holder's shoe size. Choosing what to include and what to leave out is the first design decision when translating a domain into classes.

Good abstractions simplify the code that uses them. If callers need to understand internal mechanics to use a class correctly, the abstraction is leaking rather than helping.

## Abstract class

A class that cannot be instantiated directly. It exists to provide a partial implementation and a common interface that concrete subclasses fill in. In Java, marking a class `abstract` prevents `new` from being called on it.

```java
public abstract class Shape {
    private String color;

    public Shape(String color) {
        this.color = color;
    }

    public abstract double area();   // subclasses must implement

    public String describe() {       // shared implementation
        return color + " shape with area " + area();
    }
}
```

Use an abstract class when subclasses share state or implementation. If the only thing they share is a method contract with no common code, an interface is usually a better fit.

## Abstract method

A method declared without a body — just a signature and the `abstract` keyword. Every concrete subclass must supply its own implementation or remain abstract itself. This forces subclasses to honor a contract while leaving the details up to them.

```java
public class Circle extends Shape {
    private double radius;

    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }

    @Override
    public double area() {              // required by Shape
        return Math.PI * radius * radius;
    }
}
```

The compiler enforces the contract: if `Circle` forgot to implement `area()`, the code would not compile. This turns a potential runtime surprise into a compile-time error.

## CRC cards (Class–Responsibility–Collaborator)

A lightweight analysis technique for discovering classes before writing code. Each card names a candidate class, lists what that class is responsible for (its behavior), and names the other classes it works with (its collaborators).

```text
┌─────────────────────────────────────────┐
│  Class: Order                           │
├─────────────────────────────────────────┤
│  Responsibilities      │ Collaborators  │
│  - Track line items    │ LineItem       │
│  - Compute total       │ TaxCalculator  │
│  - Apply discounts     │ Coupon         │
└─────────────────────────────────────────┘
```

CRC cards work best as a whiteboard exercise early in design. Walking through a use case while moving cards around reveals missing classes, misplaced responsibilities, and excessive coupling before any code exists.

## Domain modeling

The process of identifying the key entities in a problem domain, their attributes, and their relationships before writing code. The output is a conceptual model — often a sketch of classes with named associations — that drives the class hierarchy.

```text
Library domain:
  Book      — title, isbn, copies
  Member    — name, membershipId
  Loan      — book, member, dueDate
  Catalog   — searches books, tracks availability
```

A good domain model uses the language of the domain ("loan," "catalog") rather than technical jargon ("data manager," "record handler"). This alignment — sometimes called ubiquitous language — makes the code readable to domain experts and developers alike.

## Levels of abstraction

Well-designed systems organize code into layers where each layer operates at a consistent level of abstraction. A high-level method should read like a summary; it delegates to lower-level methods for details.

```java
public class OrderService {
    public void placeOrder(Cart cart, Customer customer) {
        Order order = createOrder(cart);           // high-level steps
        applyDiscounts(order, customer);
        chargePayment(order, customer);
        sendConfirmation(order, customer);
    }

    private Order createOrder(Cart cart) { /* low-level detail */ }
    private void applyDiscounts(Order o, Customer c) { /* ... */ }
    // ...
}
```

Mixing levels — a method that orchestrates a workflow and also manually formats an email body — makes code harder to read and harder to change. Pushing details into well-named helper methods keeps each method at one level.

## Abstraction vs. premature abstraction

Abstraction is valuable when it removes accidental complexity, but abstracting too early — before the problem is well understood — can introduce unnecessary layers that obscure rather than clarify. Three concrete implementations that share a clear pattern are a stronger signal for an abstraction than one implementation that "might" be reused someday.

The cost of a wrong abstraction is often higher than the cost of some duplication, because an abstraction creates a coupling point that every future change must route through.
