# Composition and Relationships

Objects do not exist in isolation — they work together. The way classes relate to each other determines the system's flexibility, testability, and resilience to change. Understanding the spectrum from weak dependency to strong composition helps you choose the right coupling for each situation.

## Key Points

- **Association** — The broadest relationship: one object uses or knows about another with no implied ownership.
- **Aggregation** — A "has-a" relationship where parts have independent lifecycles and can outlive the container.
- **Composition** — A strong "has-a" where the container creates and owns the parts; destroying the container destroys the parts.
- **Dependency** — The weakest coupling: one class uses another only within a method scope, holding no long-lived reference.
- **Favor composition over inheritance** — Assemble behavior with helper objects instead of subclassing. More flexible, avoids fragile base class problems, and simplifies testing.
- **Delegation** — Forwarding a request to a contained helper. The mechanism that makes composition work in practice.

## Example

```java
public interface Engine {
    void start();
    int horsepower();
}

public class ElectricEngine implements Engine {
    @Override public void start() { System.out.println("Electric hum"); }
    @Override public int horsepower() { return 300; }
}

public class GasEngine implements Engine {
    @Override public void start() { System.out.println("Vroom!"); }
    @Override public int horsepower() { return 250; }
}

public class Car {
    private final Engine engine;   // composition + delegation

    public Car(Engine engine) { this.engine = engine; }

    public void start()       { engine.start(); }        // delegates
    public int horsepower()   { return engine.horsepower(); }
}

public class Main {
    public static void main(String[] args) {
        Car electric = new Car(new ElectricEngine());
        Car gas      = new Car(new GasEngine());

        electric.start();   // "Electric hum"
        gas.start();        // "Vroom!"
    }
}
```

`Car` composes an `Engine` rather than inheriting from one. The engine can be swapped at construction time, each variant is independently testable, and adding a `HybridEngine` requires no changes to `Car`.
