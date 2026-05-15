# Interfaces and Abstract Types

Interfaces define what an object can do without dictating how. They are the primary tool for decoupling in OOP: callers depend on a contract, not a concrete class, which makes code easier to extend, test, and swap.

## Key Points

- **Interface** — A pure contract declaring method signatures with no state or constructors. Classes that implement it must provide all method bodies.
- **Multiple interface implementation** — A class can implement many interfaces, gaining multiple roles without the problems of multiple class inheritance.
- **Default methods** — Interface methods with a body (Java 8+), allowing interfaces to evolve without breaking existing implementors.
- **Programming to interfaces** — Declare types as interfaces, not concrete classes, to decouple callers from specific implementations.
- **Functional interface** — An interface with one abstract method, instantiable via lambda. Bridges OOP and functional programming.
- **Interface vs. abstract class** — Interfaces for shared capability across unrelated classes; abstract classes for shared state and implementation within a hierarchy.

## Example

```java
@FunctionalInterface
public interface Discounter {
    double apply(double price);
}

public class PercentDiscount implements Discounter {
    private final double rate;
    public PercentDiscount(double rate) { this.rate = rate; }

    @Override
    public double apply(double price) { return price * (1 - rate); }
}

public class Cart {
    private final List<Double> prices = new ArrayList<>();

    public void add(double price) { prices.add(price); }

    public double total(Discounter discounter) {
        return prices.stream()
                     .mapToDouble(discounter::apply)
                     .sum();
    }

    public static void main(String[] args) {
        Cart cart = new Cart();
        cart.add(100.0);
        cart.add(50.0);

        System.out.println(cart.total(new PercentDiscount(0.1)));  // class
        System.out.println(cart.total(p -> p - 5));                // lambda
    }
}
```

`Cart.total()` programs to the `Discounter` interface. It works with any implementation — a named class, an anonymous class, or a lambda — without knowing or caring which one it receives.
