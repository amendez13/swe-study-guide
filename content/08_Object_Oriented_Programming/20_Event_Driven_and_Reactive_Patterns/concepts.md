## Event-driven programming

A paradigm where program flow is determined by events — user actions, sensor inputs, messages from other systems — rather than a predetermined sequence of steps. Objects publish events; other objects subscribe and react. This decouples producers from consumers and makes systems naturally extensible.

```java
// Publisher doesn't know who listens or what they do
button.addActionListener(e -> saveDocument());
button.addActionListener(e -> updateStatusBar());
```

Adding a new reaction (logging, analytics) requires only registering another listener — no existing code changes.

## Event handler / listener

A method or object registered to respond to a specific event. In Java, listeners typically implement an interface with a callback method. The Observer pattern is the OOP formalization of this concept.

```java
public interface OrderEventListener {
    void onOrderPlaced(Order order);
}

public class InventoryUpdater implements OrderEventListener {
    @Override
    public void onOrderPlaced(Order order) {
        for (Item item : order.getItems()) {
            inventory.decrease(item, 1);
        }
    }
}
```

The event source holds a list of listeners and iterates through them when the event fires. Each listener handles the event independently.

## Callback

A method (or lambda) passed to another object to be invoked later when a condition is met or an operation completes. Callbacks are a lightweight form of the Strategy and Observer patterns — they inject behavior without requiring a full class hierarchy.

```java
public class FileLoader {
    public void loadAsync(String path, Consumer<String> onComplete) {
        new Thread(() -> {
            String content = readFile(path);
            onComplete.accept(content);   // callback fires when done
        }).start();
    }
}

loader.loadAsync("data.csv", content -> System.out.println("Loaded: " + content.length() + " chars"));
```

Callbacks keep the caller in control of what happens next while the callee controls when it happens.

## Lambda expression

An anonymous function that can be passed as a value. In Java, lambdas implement functional interfaces (interfaces with one abstract method), eliminating the need for verbose anonymous inner classes.

```java
// Anonymous inner class (pre-Java 8)
button.addActionListener(new ActionListener() {
    @Override
    public void actionPerformed(ActionEvent e) {
        System.out.println("Clicked");
    }
});

// Lambda (Java 8+)
button.addActionListener(e -> System.out.println("Clicked"));
```

Lambdas reduce boilerplate for event handlers, comparators, and strategy objects. They bridge OOP and functional programming — the interface provides the type contract, the lambda provides the behavior.

## Event bus / publish-subscribe

A centralized message broker that decouples publishers from subscribers entirely. Publishers emit named events to the bus; subscribers register interest in specific event types. Neither side knows about the other.

```java
public class EventBus {
    private final Map<String, List<Consumer<Object>>> handlers = new HashMap<>();

    public void subscribe(String event, Consumer<Object> handler) {
        handlers.computeIfAbsent(event, k -> new ArrayList<>()).add(handler);
    }

    public void publish(String event, Object data) {
        handlers.getOrDefault(event, List.of()).forEach(h -> h.accept(data));
    }
}

EventBus bus = new EventBus();
bus.subscribe("order.placed", data -> System.out.println("Notify: " + data));
bus.subscribe("order.placed", data -> System.out.println("Log: " + data));
bus.publish("order.placed", order);
```

This pattern is common in UI frameworks, microservice architectures, and plugin systems where the set of subscribers is not known at compile time.
