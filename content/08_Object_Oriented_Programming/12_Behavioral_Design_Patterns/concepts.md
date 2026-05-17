## Observer

Defines a one-to-many dependency so that when one object (the subject) changes state, all registered dependents (observers) are notified and updated automatically. This is the foundation of event-driven architectures and UI frameworks.

```java
public interface Observer {
    void update(String event, Object data);
}

public class EventBus {
    private final Map<String, List<Observer>> listeners = new HashMap<>();

    public void subscribe(String event, Observer obs) {
        listeners.computeIfAbsent(event, k -> new ArrayList<>()).add(obs);
    }

    public void publish(String event, Object data) {
        for (Observer obs : listeners.getOrDefault(event, List.of())) {
            obs.update(event, data);
        }
    }
}
```

The publisher does not know who is listening or what they will do — it just fires the event. This decoupling makes the system easy to extend.

## Strategy

Defines a family of interchangeable algorithms, encapsulates each one behind a common interface, and lets the client swap them at runtime. Eliminates branching logic for algorithm selection.

```java
public interface SortStrategy {
    void sort(int[] data);
}

public class QuickSort implements SortStrategy {
    public void sort(int[] data) { /* quicksort */ }
}

public class MergeSort implements SortStrategy {
    public void sort(int[] data) { /* mergesort */ }
}

public class Sorter {
    private SortStrategy strategy;
    public Sorter(SortStrategy strategy) { this.strategy = strategy; }

    public void sort(int[] data) { strategy.sort(data); }

    public void setStrategy(SortStrategy s) { this.strategy = s; }
}
```

The caller picks the strategy at construction or switches it later — `Sorter` itself never changes.

## Template Method

Defines the skeleton of an algorithm in a base class method, deferring specific steps to subclasses. The overall sequence is fixed; subclasses fill in the variable parts without changing the algorithm's structure.

```java
public abstract class DataProcessor {
    public final void process() {     // template — fixed sequence
        readData();
        transform();
        writeOutput();
    }

    protected abstract void readData();
    protected abstract void transform();
    protected abstract void writeOutput();
}

public class CsvProcessor extends DataProcessor {
    protected void readData()    { /* parse CSV */ }
    protected void transform()   { /* clean rows */ }
    protected void writeOutput() { /* write JSON */ }
}
```

The `final` keyword on `process()` prevents subclasses from altering the order of steps.

## Command

Encapsulates a request as an object, allowing parameterization, queuing, logging, and undo/redo support. The invoker knows nothing about the receiver — it just executes the command.

```java
public interface Command {
    void execute();
    void undo();
}

public class AddTextCommand implements Command {
    private final StringBuilder document;
    private final String text;

    public AddTextCommand(StringBuilder document, String text) {
        this.document = document;
        this.text = text;
    }

    public void execute() { document.append(text); }
    public void undo()    { document.delete(document.length() - text.length(), document.length()); }
}
```

A history stack of `Command` objects gives you full undo/redo with no conditionals.

## State

Allows an object to change its behavior when its internal state changes, making it appear as if the object changed its class. Each state is represented by a separate class that implements a common interface.

```java
public interface OrderState {
    void next(Order order);
    void cancel(Order order);
}

public class PendingState implements OrderState {
    public void next(Order order)   { order.setState(new ShippedState()); }
    public void cancel(Order order) { order.setState(new CancelledState()); }
}

public class ShippedState implements OrderState {
    public void next(Order order)   { order.setState(new DeliveredState()); }
    public void cancel(Order order) { throw new IllegalStateException("Already shipped"); }
}
```

State eliminates the large `switch` or `if/else` blocks that otherwise grow with every new state.

## Chain of Responsibility

Passes a request along a chain of handlers. Each handler decides whether to process the request or forward it to the next handler. The sender is decoupled from the receiver, and the chain can be composed dynamically.

```java
public abstract class Handler {
    private Handler next;

    public Handler setNext(Handler next) { this.next = next; return next; }

    public void handle(Request req) {
        if (!canHandle(req) && next != null) {
            next.handle(req);
        }
    }

    protected abstract boolean canHandle(Request req);
}
```

Middleware pipelines in web frameworks are a real-world example: authentication, logging, and rate limiting are handlers chained together.

## Iterator

Provides a way to access elements of a collection sequentially without exposing its internal structure. In Java, the `Iterable`/`Iterator` interfaces enable the enhanced for-loop.

```java
public class NumberRange implements Iterable<Integer> {
    private final int start, end;
    public NumberRange(int start, int end) { this.start = start; this.end = end; }

    @Override
    public Iterator<Integer> iterator() {
        return new Iterator<>() {
            int current = start;
            public boolean hasNext() { return current <= end; }
            public Integer next()    { return current++; }
        };
    }
}

for (int n : new NumberRange(1, 5)) {
    System.out.println(n);   // 1, 2, 3, 4, 5
}
```

## Mediator

Defines a central object that coordinates communication between components, replacing direct references with indirect communication through the mediator. This reduces coupling when many objects need to interact.

```java
public class ChatRoom {
    public void sendMessage(String message, User sender) {
        for (User user : users) {
            if (user != sender) user.receive(message);
        }
    }
}
```

Without a mediator, every user would need a reference to every other user. The mediator centralizes the wiring so components only know the mediator, not each other.
