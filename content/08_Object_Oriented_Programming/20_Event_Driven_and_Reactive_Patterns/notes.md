# Event-Driven and Reactive Patterns

Event-driven programming shifts control from a linear sequence of calls to a model where objects react to events as they happen. It is the paradigm behind GUI frameworks, message queues, and modern reactive systems — and it relies heavily on OOP concepts like interfaces, polymorphism, and the Observer pattern.

## Key Points

- **Event-driven programming** — Flow is determined by events, not a fixed call sequence. Publishers emit; subscribers react.
- **Event handler / listener** — An object implementing a callback interface, registered to respond to a specific event type.
- **Callback** — A function or lambda passed to another object and invoked later. Lightweight strategy/observer.
- **Lambda expression** — An anonymous function implementing a functional interface. Eliminates boilerplate for handlers and strategies.
- **Event bus / publish-subscribe** — A central broker decoupling publishers from subscribers entirely. Neither side knows about the other.

## Example

```java
@FunctionalInterface
public interface EventListener<T> {
    void handle(T event);
}

public class SimpleEventBus {
    private final Map<Class<?>, List<EventListener<?>>> listeners = new HashMap<>();

    public <T> void on(Class<T> type, EventListener<T> listener) {
        listeners.computeIfAbsent(type, k -> new ArrayList<>()).add(listener);
    }

    @SuppressWarnings("unchecked")
    public <T> void emit(T event) {
        List<EventListener<?>> handlers = listeners.getOrDefault(event.getClass(), List.of());
        for (EventListener<?> h : handlers) {
            ((EventListener<T>) h).handle(event);
        }
    }
}

record OrderPlaced(int orderId, double total) {}

public class Main {
    public static void main(String[] args) {
        SimpleEventBus bus = new SimpleEventBus();

        bus.on(OrderPlaced.class, e -> System.out.println("Invoice for order " + e.orderId()));
        bus.on(OrderPlaced.class, e -> System.out.println("Ship order " + e.orderId()));

        bus.emit(new OrderPlaced(42, 99.95));
    }
}
```

Two listeners react independently to the same `OrderPlaced` event. Adding a third (analytics, notifications) is one `bus.on(...)` call — no existing code changes.
