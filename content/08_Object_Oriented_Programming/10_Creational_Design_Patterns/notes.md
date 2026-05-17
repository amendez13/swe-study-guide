# Creational Design Patterns

Creational patterns abstract the instantiation process, hiding exactly which classes are created and how they are composed. They give you flexibility in what gets created, who creates it, and when.

## Key Points

- **Singleton** — One instance, global access. Convenient but hinders testing; modern code prefers DI-managed singletons.
- **Factory Method** — Subclasses decide which concrete class to instantiate. Keeps creation logic out of consumer code.
- **Abstract Factory** — Creates families of related objects. Swapping the factory swaps the entire product set.
- **Builder** — Step-by-step construction for objects with many optional parameters. Produces an immutable result via `build()`.
- **Prototype** — Clone an existing object to create a new one. Useful when setup is expensive or template-based.

## Example

```java
public interface Notification {
    void send(String message);
}

public class EmailNotification implements Notification {
    public void send(String message) { System.out.println("Email: " + message); }
}

public class SmsNotification implements Notification {
    public void send(String message) { System.out.println("SMS: " + message); }
}

public class NotificationFactory {
    public static Notification create(String channel) {
        return switch (channel) {
            case "email" -> new EmailNotification();
            case "sms"   -> new SmsNotification();
            default -> throw new IllegalArgumentException("Unknown: " + channel);
        };
    }
}

public class Main {
    public static void main(String[] args) {
        Notification n = NotificationFactory.create("email");
        n.send("Hello!");   // "Email: Hello!"
    }
}
```

The caller never mentions `EmailNotification` directly — the factory decides the concrete type based on configuration. Adding a `PushNotification` means adding one class and one switch case, without changing any caller.
