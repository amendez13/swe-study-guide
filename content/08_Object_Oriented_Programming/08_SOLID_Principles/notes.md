# SOLID Principles

SOLID is an acronym for five design principles that guide class and interface design toward code that is easier to maintain, extend, and test. They were popularized by Robert C. Martin and apply most strongly to code that is shared across a team, long-lived, or subject to frequent change.

## Key Points

- **Single Responsibility (SRP)** — One class, one reason to change. If you need "and" to describe what it does, split it.
- **Open/Closed (OCP)** — Extend behavior by adding new types, not by editing existing code. Abstraction is the enabler.
- **Liskov Substitution (LSP)** — Subclasses must honor the superclass contract. If a substitute breaks callers, the hierarchy is wrong.
- **Interface Segregation (ISP)** — Small, focused interfaces over one fat interface. Clients should only see the methods they use.
- **Dependency Inversion (DIP)** — Depend on abstractions, not concretions. High-level policy and low-level detail both point at an interface.
- **SOLID as a system** — The five principles reinforce each other; violating one often triggers violations of the others.

## Example

```java
public interface NotificationChannel {
    void send(String recipient, String message);
}

public class EmailChannel implements NotificationChannel {
    @Override
    public void send(String recipient, String message) {
        System.out.println("Email to " + recipient + ": " + message);
    }
}

public class SmsChannel implements NotificationChannel {
    @Override
    public void send(String recipient, String message) {
        System.out.println("SMS to " + recipient + ": " + message);
    }
}

public class AlertService {
    private final NotificationChannel channel;  // DIP: depends on abstraction

    public AlertService(NotificationChannel channel) {
        this.channel = channel;
    }

    public void alert(String recipient, String text) {
        channel.send(recipient, text);            // OCP: new channels don't change this
    }
}
```

`AlertService` follows SRP (only orchestrates alerts), OCP (new channels are added by implementing the interface), ISP (the interface has one method), and DIP (it depends on `NotificationChannel`, not a concrete class). Adding `PushChannel` requires zero edits to existing code.
