## Interface

A contract that declares method signatures without providing implementations. A class that "implements" an interface must supply bodies for every declared method. Unlike abstract classes, interfaces carry no state and no constructor — they define what an object can do without prescribing how.

```java
public interface Sortable {
    int compareTo(Object other);
}

public class Student implements Sortable {
    private String name;
    private double gpa;

    @Override
    public int compareTo(Object other) {
        return Double.compare(this.gpa, ((Student) other).gpa);
    }
}
```

## Multiple interface implementation

A class can implement several interfaces, gaining multiple roles without the diamond-problem ambiguity that comes with multiple class inheritance. Java allows only single class inheritance, but unlimited interface implementation.

```java
public interface Printable {
    void print();
}

public interface Exportable {
    byte[] exportData();
}

public class Report implements Printable, Exportable {
    @Override
    public void print() { System.out.println("Printing report..."); }

    @Override
    public byte[] exportData() { return new byte[0]; }
}
```

`Report` plays two roles — it is both `Printable` and `Exportable` — without inheriting any implementation baggage.

## Default methods

Methods defined directly in an interface with a body (Java 8+). They allow interfaces to evolve by adding new methods without breaking every existing implementor. Classes can override a default method or inherit it as-is.

```java
public interface Logger {
    void log(String message);

    default void logError(String message) {       // has a body
        log("ERROR: " + message);
    }
}
```

Default methods solve a real backwards-compatibility problem: before Java 8, adding a method to a widely-implemented interface would break every class that implemented it. The tradeoff is that interfaces can now carry behavior, blurring the line with abstract classes.

## Programming to interfaces

Declaring variables, parameters, and return types as interface types rather than concrete classes. This decouples calling code from specific implementations and makes it easy to swap, mock, or extend behavior without changing callers.

```java
// Coupled to ArrayList
ArrayList<String> names = new ArrayList<>();

// Programmed to interface — can swap to LinkedList without changing callers
List<String> names = new ArrayList<>();
```

The same principle applies to method signatures:

```java
public void process(List<String> items) { ... }   // accepts any List
```

The rule of thumb: depend on the most general type that still gives you the operations you need.

## Functional interface

An interface with exactly one abstract method. In Java, it can be instantiated with a lambda expression, bridging OOP and functional programming styles. The `@FunctionalInterface` annotation makes the intent explicit and triggers a compile error if the interface has more than one abstract method.

```java
@FunctionalInterface
public interface Validator<T> {
    boolean isValid(T item);
}

// Lambda instantiation
Validator<String> notEmpty = s -> !s.isEmpty();
System.out.println(notEmpty.isValid("hello"));   // true
```

The JDK ships many built-in functional interfaces: `Predicate`, `Function`, `Consumer`, `Supplier`, and `Comparator` are the most common.

## Interface vs. abstract class

Both define contracts for subclasses, but they solve different problems. Use an interface when you want to define a capability that unrelated classes can share (`Comparable`, `Serializable`). Use an abstract class when subclasses share state or implementation and belong to a natural hierarchy.

```text
Interface:     no state, no constructor, multiple implementation, pure contract
Abstract class: can have state, constructor, single inheritance, partial implementation
```

When in doubt, start with an interface. You can always introduce an abstract class later if shared implementation emerges, but you cannot undo the single-inheritance constraint.
