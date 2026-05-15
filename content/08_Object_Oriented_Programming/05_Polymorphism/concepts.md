## Runtime polymorphism (dynamic dispatch)

The ability to call a method on a superclass reference and have the actual subclass implementation execute at runtime. The JVM looks at the real type of the object — not the declared type of the variable — to decide which method body runs. This is the cornerstone of extensible OOP code.

```java
Shape s = new Circle(5.0);
s.area();   // calls Circle.area(), not Shape.area()
```

Without polymorphism, every caller would need a chain of `if/else instanceof` checks. With it, adding a new shape requires only a new subclass — existing code that operates on `Shape` references works unchanged.

## Upcasting

Treating a subclass object as an instance of its superclass type. In Java this happens implicitly — no cast syntax is needed — and is always safe because the subclass "is-a" superclass and guarantees every method the superclass contract requires.

```java
Dog rex = new Dog("Rex");
Animal a = rex;          // implicit upcast — always safe
a.speak();               // calls Dog.speak() at runtime
```

Upcasting is the mechanism that makes polymorphic code possible. A method that accepts `Animal` can work with `Dog`, `Cat`, or any future subclass without knowing about them.

## Downcasting

Casting a superclass reference back to a subclass type. Unlike upcasting, this requires an explicit cast and can fail at runtime with a `ClassCastException` if the object is not actually that subclass. Always guard with `instanceof` first.

```java
Animal a = getAnimal();

if (a instanceof Dog dog) {   // pattern matching (Java 16+)
    dog.fetch();               // safe — only reached if a is a Dog
}
```

Frequent downcasting is a design smell. It usually means the base type's interface is too narrow and the caller needs to know the concrete type — which defeats the purpose of polymorphism.

## The "is-a" relationship

The semantic test for whether inheritance is appropriate: if "a Circle is-a Shape" makes sense in the domain, then `Circle extends Shape` is justified. If the sentence sounds forced ("a Stack is-a ArrayList"?), composition or an interface is a better fit.

Violating "is-a" creates hierarchies where subclasses don't fully honor the superclass contract, leading to surprises when polymorphic code passes the wrong subtype.

## Method overloading

Defining multiple methods with the same name but different parameter lists within a single class. The compiler chooses which overload to call based on the argument types at compile time — this is sometimes called static polymorphism.

```java
public class Printer {
    public void print(String text)   { System.out.println(text); }
    public void print(int number)    { System.out.println(number); }
    public void print(String text, int copies) {
        for (int i = 0; i < copies; i++) System.out.println(text);
    }
}
```

Overloading is resolved at compile time based on the declared types of the arguments. This is fundamentally different from overriding, which is resolved at runtime based on the actual type of the object.

## Type substitutability

Any code that works with a superclass type should work correctly when given any subclass instance, without knowing the concrete type. This is the behavioral contract behind polymorphism and is closely related to the Liskov Substitution Principle.

```java
public void printAreas(List<Shape> shapes) {
    for (Shape s : shapes) {
        System.out.println(s.area());   // works for any Shape subclass
    }
}
```

If a subclass breaks the expectations set by the superclass — for example, throwing an unexpected exception or returning a nonsensical value from an inherited method — substitutability is violated and polymorphic code becomes unreliable.

## Polymorphism vs. conditionals

A common refactoring in OOP is replacing type-checking conditionals with polymorphism. Instead of a switch on a type tag, define a method on the base type and let each subclass implement its own version.

```java
// Before: fragile switch
double area(Shape s) {
    if (s instanceof Circle c)       return Math.PI * c.radius * c.radius;
    else if (s instanceof Rectangle r) return r.width * r.height;
    else throw new IllegalArgumentException();
}

// After: polymorphic
// Each Shape subclass implements area() — no switch needed.
```

The polymorphic version is open for extension: adding a `Triangle` requires only a new class, not editing the switch statement.
