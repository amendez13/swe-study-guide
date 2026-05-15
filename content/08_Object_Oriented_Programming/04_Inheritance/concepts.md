## Subclass and superclass

A subclass (child) extends a superclass (parent), inheriting all of its non-private fields and methods. The subclass can add new members to specialize the type or override inherited methods to change behavior. In Java, a class can extend exactly one superclass.

```java
public class Vehicle {
    protected int speed;

    public void accelerate(int delta) {
        speed += delta;
    }
}

public class Car extends Vehicle {
    private int passengers;

    public void loadPassengers(int count) {
        passengers = count;
    }
}
```

`Car` inherits `speed` and `accelerate()` without re-declaring them, and adds its own `passengers` field and `loadPassengers()` method.

## Method overriding

Redefining an inherited method in a subclass to change or extend its behavior. The overriding method must have the same name, return type, and parameter list as the parent method. In Java, the `@Override` annotation makes the intent explicit and triggers a compile error if the signature doesn't match.

```java
public class Vehicle {
    public String describe() {
        return "Vehicle moving at " + speed;
    }
}

public class Car extends Vehicle {
    @Override
    public String describe() {
        return "Car with " + passengers + " passengers at " + speed;
    }
}
```

A subclass can also extend the parent behavior rather than replace it entirely by calling `super.describe()` inside the override.

## Constructor chaining

When a subclass is instantiated, its constructor must ensure the superclass portion of the object is initialized first. In Java this is done with `super(...)` as the first statement in the subclass constructor. If omitted, the compiler inserts a call to the no-arg `super()` — which fails if the superclass has no no-arg constructor.

```java
public class Animal {
    private final String species;

    public Animal(String species) {
        this.species = species;
    }
}

public class Dog extends Animal {
    private final String name;

    public Dog(String name) {
        super("Canine");       // must be the first statement
        this.name = name;
    }
}
```

## The singly rooted hierarchy

In Java, every class ultimately extends `java.lang.Object`. This guarantees that every object in the system has `toString()`, `equals()`, `hashCode()`, `getClass()`, and a few other baseline methods. It also means every object can be assigned to a variable of type `Object`, which is the foundation for generic collections and frameworks.

```java
Object obj = new Dog("Rex");
System.out.println(obj.toString());   // works on any object
System.out.println(obj.hashCode());   // works on any object
```

## `final` and sealed classes

Marking a class `final` prevents it from being subclassed entirely. Marking a method `final` prevents subclasses from overriding it. Both are tools for design intent: use them when a class or method was not designed for extension and changing it could break invariants.

```java
public final class ImmutablePoint {   // cannot be subclassed
    private final int x, y;
    public ImmutablePoint(int x, int y) { this.x = x; this.y = y; }
}
```

Sealed classes (Java 17+) offer a middle ground: they declare a fixed set of permitted subclasses. Any class not in the list is rejected by the compiler.

```java
public sealed class Shape permits Circle, Rectangle, Triangle { }
```

## Protected access

The `protected` modifier allows subclasses (and classes in the same package) to access a member. It sits between `private` (too restrictive when subclasses need the field) and `public` (too open for an implementation detail).

```java
public class Logger {
    protected String formatMessage(String msg) {    // subclasses may customize
        return "[LOG] " + msg;
    }

    public void log(String msg) {
        System.out.println(formatMessage(msg));
    }
}

public class TimestampLogger extends Logger {
    @Override
    protected String formatMessage(String msg) {
        return "[" + java.time.Instant.now() + "] " + msg;
    }
}
```

Use `protected` deliberately — it is part of the class's contract with its subclasses and can be just as hard to change later as `public`.

## Fragile base class problem

Changes to a superclass can inadvertently break subclass behavior, even when the superclass change looks safe in isolation. This happens because subclasses depend on implementation details of the parent — method call order, field values at certain points, side effects.

```java
// Superclass adds a call to validate() inside save().
// Subclass overrides validate() and calls super.save(),
// creating an infinite loop or double-validation it never expected.
```

This fragility is one of the strongest arguments for favoring composition over inheritance. When behavior is assembled by delegation rather than by subclassing, a change in one component does not ripple unpredictably through a hierarchy.
