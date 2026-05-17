## Class

A class is a blueprint that defines the structure (fields) and behavior (methods) of a type. It declares what data each instance will hold and what operations are available on that data. No memory is allocated for a class itself — it only becomes concrete when you create an object from it.

```java
public class BankAccount {
    private String owner;
    private double balance;

    public void deposit(double amount) {
        balance += amount;
    }
}
```

## Object

An object is a runtime instance of a class. Each object gets its own copy of the class's fields, occupies its own memory, and responds to method calls defined by its class. You can create as many objects from one class as you need — they share the same behavior but hold independent state.

```java
BankAccount aliceAccount = new BankAccount("Alice", 500.0);
BankAccount bobAccount   = new BankAccount("Bob", 0.0);

aliceAccount.deposit(100.0);  // only aliceAccount changes
```

## Instance variable (field)

A variable declared inside a class that stores per-object state. Every object gets its own copy, so changing a field on one object does not affect another. Fields define what an object "knows" — the data it carries throughout its lifetime.

```java
public class Rectangle {
    private double width;   // instance variable
    private double height;  // instance variable

    public double area() {
        return width * height;
    }
}
```

Contrast with local variables, which live only for the duration of a method call and disappear when the method returns.

## Method

A function defined on a class that operates on or returns information about the object's state. Methods define what an object can "do." A method can read fields, modify fields, call other methods, or delegate work to collaborators.

```java
public class Temperature {
    private double celsius;

    public double toFahrenheit() {
        return celsius * 9.0 / 5.0 + 32.0;
    }

    public void increase(double delta) {
        celsius += delta;
    }
}
```

The key distinction from a standalone function is that a method has implicit access to the object it was called on — it always operates in the context of a specific instance.

## Constructor

A special method invoked exactly once when an object is created with `new`. Its job is to initialize the object's fields and enforce any invariants before the object is usable. In Java, the constructor has the same name as the class and no return type.

```java
public class BankAccount {
    private final String owner;
    private double balance;

    public BankAccount(String owner, double initialBalance) {
        this.owner = owner;
        this.balance = initialBalance;
    }
}
```

If you don't declare any constructor, the compiler provides a default no-argument constructor that sets fields to zero/null/false. The moment you declare one, the default disappears — so classes that need both parameterized and no-arg construction must declare both explicitly.

## The `this` reference

An implicit reference available inside every non-static method and constructor that points to the object the method was called on. Its most common use is disambiguating when a parameter has the same name as a field, but it also lets you pass the current object to another method or constructor.

```java
public class Point {
    private int x;
    private int y;

    public Point(int x, int y) {
        this.x = x;  // this.x is the field, x is the parameter
        this.y = y;
    }

    public double distanceTo(Point other) {
        int dx = this.x - other.x;
        int dy = this.y - other.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
}
```

## Object identity vs. equality

Identity (`==`) checks whether two references point to the same object in memory. Equality (`.equals()`) checks whether two objects are logically equivalent based on their state. This is one of the most common sources of bugs for developers new to OOP.

```java
String a = new String("hello");
String b = new String("hello");

a == b       // false — different objects in memory
a.equals(b)  // true  — same character sequence
```

When you write your own class, `equals()` inherited from `Object` defaults to identity comparison. To get value-based equality, you must override both `equals()` and `hashCode()` — and the two must be consistent.

## Reference semantics

In Java (and most OOP languages), a variable does not hold an object directly — it holds a reference (a pointer) to the object in memory. Assignment copies the reference, not the object, so both variables then point to the same instance. Changes through one reference are visible through the other.

```java
BankAccount a = new BankAccount("Alice", 100.0);
BankAccount b = a;        // b points to the same object

b.deposit(50.0);
a.getBalance();           // 150.0 — a and b alias the same object
```

This aliasing behavior is powerful (cheap to pass objects around) but dangerous if you mutate shared state without realizing two references point to the same object. Defensive copying or immutability are common mitigations.
