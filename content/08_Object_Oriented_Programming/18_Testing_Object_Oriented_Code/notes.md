# Testing Object-Oriented Code

Testing is not an afterthought — it is a design tool. Well-structured OOP code is inherently testable, and difficulty writing tests is one of the strongest signals that a class needs refactoring.

## Key Points

- **Unit testing** — Test one class/method in isolation with known inputs and expected outputs. Fast, repeatable, and focused.
- **TDD** — Red → Green → Refactor. Write the test first, then the minimum code to pass, then clean up.
- **Test doubles** — Mocks, stubs, and fakes stand in for real dependencies. Mock at boundaries, not between internal classes.
- **Testability as design feedback** — If a class is hard to test, it's probably too coupled. Inject dependencies and program to interfaces.

## Example

```java
public interface PricingService {
    double priceFor(String sku);
}

public class Cart {
    private final List<String> items = new ArrayList<>();
    private final PricingService pricing;

    public Cart(PricingService pricing) { this.pricing = pricing; }

    public void add(String sku) { items.add(sku); }

    public double total() {
        return items.stream()
                    .mapToDouble(pricing::priceFor)
                    .sum();
    }
}

// Test with a stub — no real pricing service needed
@Test
void totalSumsItemPrices() {
    PricingService stub = sku -> sku.equals("A") ? 10.0 : 5.0;
    Cart cart = new Cart(stub);
    cart.add("A");
    cart.add("B");
    assertEquals(15.0, cart.total());
}
```

`Cart` accepts a `PricingService` interface, making it trivially testable with a lambda stub. No database, no HTTP, no setup — just the behavior under test.
