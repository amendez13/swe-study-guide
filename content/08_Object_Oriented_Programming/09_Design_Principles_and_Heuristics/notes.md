# Design Principles and Heuristics

Beyond the four pillars and SOLID, a set of practical heuristics guides everyday OOP design decisions. These principles help you evaluate trade-offs and recognize when a design is moving toward brittleness or unnecessary complexity.

## Key Points

- **Coupling** — How much one class depends on another's internals. Aim for low coupling through narrow interfaces.
- **Cohesion** — How well a class's members belong together. Aim for high cohesion — one focused purpose per class.
- **Separation of concerns** — Each module handles one concern (UI, logic, persistence) and does not mix them.
- **Conceptual integrity** — Consistent naming, uniform patterns, predictable behavior across the entire codebase.
- **Law of Demeter** — Talk only to immediate neighbors, never reach through objects to access distant internals.
- **Tell, Don't Ask** — Push behavior into the object that owns the state rather than extracting state and deciding externally.
- **DRY** — One representation per piece of knowledge. Duplication of logic means a missing abstraction, not just repeated characters.

## Example

```java
public class ShoppingCart {
    private final List<LineItem> items = new ArrayList<>();

    public void addItem(String product, int qty, double unitPrice) {
        items.add(new LineItem(product, qty, unitPrice));
    }

    public double total() {
        return items.stream()
                    .mapToDouble(LineItem::subtotal)  // Tell, Don't Ask
                    .sum();
    }
}

public class LineItem {
    private final String product;
    private final int qty;
    private final double unitPrice;

    public LineItem(String product, int qty, double unitPrice) {
        this.product = product;
        this.qty = qty;
        this.unitPrice = unitPrice;
    }

    public double subtotal() {   // behavior lives with the data
        return qty * unitPrice;
    }
}
```

`ShoppingCart` tells each `LineItem` to compute its own subtotal rather than reaching in, pulling `qty` and `unitPrice`, and multiplying externally. The result: high cohesion inside each class, low coupling between them, and the multiplication logic exists in exactly one place (DRY).
