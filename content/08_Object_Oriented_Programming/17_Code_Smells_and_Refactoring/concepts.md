## Code smell

A surface-level indicator in code that often corresponds to a deeper design problem. A smell is not a bug — the code works — but it hints that the design may be harder to understand, test, or extend than it needs to be. Recognizing smells is the first step toward targeted refactoring.

## Long Method / Large Class

A method or class that does too much. Long methods are hard to name, hard to test, and hard to reuse. Large classes accumulate unrelated responsibilities and violate SRP. The fix is usually Extract Method (pull a coherent block into its own method) or Extract Class (split into focused classes).

```java
// Smell: 200-line method doing validation, business logic, and formatting
public String processOrder(Order order) {
    // validate...
    // compute discounts...
    // format receipt...
}

// After Extract Method:
public String processOrder(Order order) {
    validate(order);
    applyDiscounts(order);
    return formatReceipt(order);
}
```

## Feature Envy

A method that uses more data from another class than from its own. It suggests the method belongs in the other class — or that the data it uses should be moved closer to the method.

```java
// Smell: calculateShipping reaches into Address for everything
public double calculateShipping(Order order) {
    Address a = order.getAddress();
    return a.getZip().startsWith("9") ? 5.0 : 10.0;
}

// Better: move shipping logic into Address or Order
public double calculateShipping() {
    return address.shippingCost();
}
```

## Shotgun Surgery

A single logical change requires modifications across many classes scattered throughout the codebase. This signals that a responsibility is spread too thin and should be consolidated into one class or module.

The opposite smell is Divergent Change — one class must be modified for many unrelated reasons. Both point to a responsibility alignment problem.

## Refused Bequest

A subclass inherits methods or fields it doesn't need, use, or make sense for. If a `Penguin` inherits `fly()` from `Bird` and has to throw an exception or do nothing, the hierarchy is wrong. Composition or a narrower interface is usually the right fix.

```java
// Smell: Square extends Rectangle but width and height must always match
public class Square extends Rectangle {
    @Override
    public void setWidth(int w) { super.setWidth(w); super.setHeight(w); }
    @Override
    public void setHeight(int h) { super.setWidth(h); super.setHeight(h); }
}
```

## Refactoring

Restructuring existing code without changing its external behavior. The goal is to improve internal design — readability, testability, extensibility — while all existing tests continue to pass. Common OOP refactorings include:

```text
Extract Method        — pull a block into a named method
Move Method           — relocate a method to the class that owns its data
Replace Conditional   — swap if/else type checks with polymorphism
  with Polymorphism
Introduce Parameter   — bundle related parameters into a small class
  Object
Extract Interface     — create an interface from a class's public methods
```

Refactoring is safest when backed by automated tests. Without tests, you're just editing and hoping.
