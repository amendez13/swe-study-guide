## Association

A general relationship where one object uses or knows about another. Association is the broadest category — it simply means "these two classes interact." The strength, direction, and lifecycle of the relationship are unspecified at this level.

```java
public class Driver {
    public void drive(Car car) {    // Driver uses Car, but doesn't own it
        car.start();
    }
}
```

## Aggregation

A "has-a" relationship where the container holds references to parts, but the parts have an independent lifecycle. Destroying the container does not destroy the parts — they can exist before, during, and after the relationship.

```java
public class Department {
    private List<Employee> members;

    public Department(List<Employee> members) {
        this.members = members;
    }
}
// Employees continue to exist if the Department is disbanded.
```

In UML, aggregation is drawn as an open diamond on the container side. In practice the distinction between aggregation and plain association is subtle and often debated — the important thing is understanding who owns the lifecycle.

## Composition

A strong "has-a" relationship where the container owns the parts and controls their lifecycle. When the container is destroyed, the parts are destroyed with it. The parts have no meaningful existence outside their owner.

```java
public class House {
    private final List<Room> rooms;

    public House(int roomCount) {
        rooms = new ArrayList<>();
        for (int i = 0; i < roomCount; i++) {
            rooms.add(new Room());   // House creates and owns the Rooms
        }
    }
}
```

The key difference from aggregation: the `House` creates the `Room` objects internally and no outside code holds a reference to them. Deleting the `House` deletes the `Room`s.

## Dependency

A transient relationship where one class uses another only within a method's scope — as a parameter, local variable, or return type. Dependencies are the weakest and most desirable form of coupling because the using class holds no long-lived reference.

```java
public class OrderService {
    public Receipt checkout(Cart cart, PaymentGateway gateway) {
        double total = cart.getTotal();
        gateway.charge(total);       // uses gateway only here
        return new Receipt(total);
    }
}
```

`OrderService` depends on `PaymentGateway` but does not own or store it. If `PaymentGateway` changes, only methods that use it are affected.

## Favor composition over inheritance

A design guideline that recommends assembling behavior by holding references to helper objects rather than extending a class. Composition is more flexible (helpers can be swapped at runtime), avoids the fragile base class problem, and makes testing easier because each component can be mocked independently.

```java
// Inheritance approach — rigid
public class LoggingList<T> extends ArrayList<T> {
    @Override
    public boolean add(T item) {
        System.out.println("Adding: " + item);
        return super.add(item);
    }
}

// Composition approach — flexible
public class LoggingList<T> {
    private final List<T> inner;

    public LoggingList(List<T> inner) { this.inner = inner; }

    public boolean add(T item) {
        System.out.println("Adding: " + item);
        return inner.add(item);
    }
}
```

The composition version works with any `List` implementation and is immune to internal changes in `ArrayList`.

## Delegation

A pattern where an object forwards a request to a contained helper rather than handling it directly. Delegation is the mechanism that makes composition-based reuse work — the outer object holds a reference to the delegate and routes calls to it.

```java
public class Printer {
    private final Formatter formatter;

    public Printer(Formatter formatter) {
        this.formatter = formatter;
    }

    public void print(String text) {
        String formatted = formatter.format(text);   // delegate
        System.out.println(formatted);
    }
}
```

The `Printer` does not know how formatting works — it delegates that responsibility. Swapping the `Formatter` changes the behavior without touching `Printer`.
