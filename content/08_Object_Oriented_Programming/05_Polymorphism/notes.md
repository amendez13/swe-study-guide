# Polymorphism

Polymorphism lets code work with objects through a general type while the specific behavior is determined by the actual object at runtime. It is the mechanism that makes OOP code extensible — new types can be added without changing the code that uses them.

## Key Points

- **Runtime polymorphism (dynamic dispatch)** — The JVM picks the method body based on the real type of the object, not the declared type of the variable.
- **Upcasting** — Treating a subclass as its superclass type. Implicit and always safe. The enabler of polymorphic code.
- **Downcasting** — Casting back to a subclass type. Requires an explicit cast and `instanceof` guard. Frequent downcasting is a design smell.
- **The "is-a" relationship** — The semantic test for inheritance. If "X is-a Y" doesn't make domain sense, prefer composition or interfaces.
- **Method overloading** — Same method name, different parameter lists, resolved at compile time. Distinct from overriding, which is resolved at runtime.
- **Type substitutability** — Subclass instances must honor the superclass contract so polymorphic code stays reliable.
- **Polymorphism vs. conditionals** — Replacing type-checking switches with overridden methods makes code open for extension without modification.

## Example

```java
public abstract class Shape {
    public abstract double area();
}

public class Circle extends Shape {
    private final double radius;
    public Circle(double radius) { this.radius = radius; }

    @Override
    public double area() { return Math.PI * radius * radius; }
}

public class Rectangle extends Shape {
    private final double w, h;
    public Rectangle(double w, double h) { this.w = w; this.h = h; }

    @Override
    public double area() { return w * h; }
}

public class Main {
    public static void main(String[] args) {
        List<Shape> shapes = List.of(new Circle(3), new Rectangle(4, 5));
        double total = 0;
        for (Shape s : shapes) total += s.area();  // dynamic dispatch
        System.out.println("Total area: " + total);
    }
}
```

The loop calls `area()` on a `Shape` reference, but the JVM dispatches to `Circle.area()` or `Rectangle.area()` based on the actual object. Adding a `Triangle` class requires no changes to `main`.
