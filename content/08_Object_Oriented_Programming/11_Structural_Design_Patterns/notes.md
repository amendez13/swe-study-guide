# Structural Design Patterns

Structural patterns deal with how classes and objects are composed to form larger structures. They ensure that pieces fit together while keeping the overall system flexible and efficient.

## Key Points

- **Adapter** — Wraps an incompatible interface to make it usable by a client expecting a different interface.
- **Facade** — Simplifies a complex subsystem behind a single entry point.
- **Composite** — Treats individual objects and tree-structured groups uniformly through a common interface.
- **Proxy** — Stands in for another object to control access: lazy loading, caching, logging, or permissions.
- **Decorator** — Wraps an object with the same interface to add behavior dynamically, stackable at runtime.
- **Bridge** — Decouples an abstraction from its implementation so both can vary independently, avoiding a subclass explosion.

## Example

```java
public interface Logger {
    void log(String message);
}

public class ConsoleLogger implements Logger {
    public void log(String message) {
        System.out.println(message);
    }
}

public class TimestampDecorator implements Logger {
    private final Logger inner;
    public TimestampDecorator(Logger inner) { this.inner = inner; }

    public void log(String message) {
        inner.log("[" + java.time.Instant.now() + "] " + message);
    }
}

public class UpperCaseDecorator implements Logger {
    private final Logger inner;
    public UpperCaseDecorator(Logger inner) { this.inner = inner; }

    public void log(String message) {
        inner.log(message.toUpperCase());
    }
}

public class Main {
    public static void main(String[] args) {
        Logger logger = new TimestampDecorator(
                            new UpperCaseDecorator(
                                new ConsoleLogger()));
        logger.log("server started");
        // prints: [2026-05-14T...] SERVER STARTED
    }
}
```

Decorators stack: `TimestampDecorator` wraps `UpperCaseDecorator` which wraps `ConsoleLogger`. Each layer adds behavior without modifying the others, and the caller sees a single `Logger` interface.
