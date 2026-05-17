## Dependency Injection (DI)

Supplying an object's dependencies from the outside — via constructor, setter, or method parameter — rather than having the object create them itself. This decouples creation from use: the class declares what it needs, and the caller (or a framework) provides it.

```java
// Without DI — tightly coupled to a concrete implementation
public class OrderService {
    private final EmailSender sender = new EmailSender();  // creates its own
}

// With DI — dependency provided from outside
public class OrderService {
    private final NotificationChannel channel;
    public OrderService(NotificationChannel channel) {
        this.channel = channel;
    }
}
```

DI makes the class easier to test (inject a mock), easier to reconfigure (swap implementations), and explicit about what it depends on.

## Inversion of Control (IoC)

A broader principle where the flow of control is inverted: instead of your code calling a library, a framework calls your code. You provide the pieces (classes, handlers, configuration), and the framework orchestrates their lifecycle and interaction. DI is the most common form of IoC.

```text
Traditional: Your code → calls library methods
IoC:         Framework → calls your code (handlers, callbacks, injected classes)
```

Spring, Guice, and CDI are Java IoC containers that manage object creation, wiring, and lifecycle automatically.

## Constructor injection

Passing all required dependencies through the constructor. This is the most common and recommended form of DI because it makes dependencies explicit in the signature, enforces completeness (you cannot create the object without providing them), and allows fields to be `final`.

```java
public class InvoiceService {
    private final OrderRepository orders;
    private final TaxCalculator tax;

    public InvoiceService(OrderRepository orders, TaxCalculator tax) {
        this.orders = orders;
        this.tax = tax;
    }
}
```

If the constructor starts taking more than 3–4 parameters, it is often a sign that the class has too many responsibilities (SRP violation) rather than a problem with constructor injection itself.

## Setter injection

Providing dependencies through setter methods after construction. This allows optional dependencies and late binding but makes the object temporarily incomplete — it can exist in a state where not all dependencies are set, which is a source of `NullPointerException`.

```java
public class ReportGenerator {
    private Formatter formatter;

    public void setFormatter(Formatter f) { this.formatter = f; }

    public String generate(Data data) {
        return formatter.format(data);  // NPE if setFormatter was never called
    }
}
```

Prefer constructor injection for required dependencies. Use setter injection only for genuinely optional collaborators.

## Service Locator

A registry that objects query to find their dependencies at runtime. It centralizes dependency resolution but hides dependencies from the class signature — you cannot tell what a class needs by looking at its constructor.

```java
public class OrderService {
    public void process() {
        // Hidden dependency — not visible in the constructor
        EmailSender sender = ServiceLocator.get(EmailSender.class);
        sender.send("...");
    }
}
```

Service Locator works but is widely considered inferior to DI because it makes dependencies implicit, complicates testing (must configure the locator), and defeats static analysis.
