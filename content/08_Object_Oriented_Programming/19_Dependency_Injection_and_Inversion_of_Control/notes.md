# Dependency Injection and Inversion of Control

Dependency Injection is the practice of supplying a class's collaborators from the outside rather than hardcoding them inside. It is the practical application of the Dependency Inversion Principle and the key enabler of testable, flexible OOP code.

## Key Points

- **Dependency Injection** — Supply dependencies from outside. Decouples creation from use, enabling swaps and mocking.
- **Inversion of Control** — The framework calls your code, not the other way around. DI is the most common form.
- **Constructor injection** — Pass required dependencies through the constructor. Explicit, complete, allows `final` fields. Preferred.
- **Setter injection** — Set dependencies after construction. Only for genuinely optional collaborators.
- **Service Locator** — A central registry for dependencies. Works, but hides dependencies and complicates testing compared to DI.

## Example

```java
public interface Clock {
    java.time.Instant now();
}

public class SystemClock implements Clock {
    public java.time.Instant now() { return java.time.Instant.now(); }
}

public class AuditLog {
    private final Clock clock;
    private final List<String> entries = new ArrayList<>();

    public AuditLog(Clock clock) { this.clock = clock; }  // constructor injection

    public void record(String event) {
        entries.add(clock.now() + " " + event);
    }

    public List<String> getEntries() {
        return Collections.unmodifiableList(entries);
    }
}

// Production
AuditLog log = new AuditLog(new SystemClock());
log.record("user login");

// Test — inject a fixed clock for deterministic assertions
Clock fixedClock = () -> java.time.Instant.parse("2026-01-01T00:00:00Z");
AuditLog testLog = new AuditLog(fixedClock);
testLog.record("test event");
// entries.get(0) is "2026-01-01T00:00:00Z test event" — predictable
```

Injecting `Clock` instead of calling `Instant.now()` directly makes `AuditLog` deterministically testable — the test controls time without mocking static methods.
