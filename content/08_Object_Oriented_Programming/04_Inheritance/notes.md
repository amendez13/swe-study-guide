# Inheritance

Inheritance lets a new class reuse and extend the behavior of an existing class. The subclass inherits fields and methods from the superclass and can override or add to them. It is one of the most powerful — and most misused — mechanisms in OOP, so understanding both its benefits and its risks is essential.

## Key Points

- **Subclass / superclass** — A subclass extends a superclass, inheriting its non-private members. Java allows single inheritance only.
- **Method overriding** — A subclass redefines an inherited method. Use `@Override` to catch signature mismatches at compile time.
- **Constructor chaining** — Subclass constructors must call `super(...)` first to initialize the parent portion of the object.
- **Singly rooted hierarchy** — Every Java class extends `Object`, guaranteeing `toString()`, `equals()`, and `hashCode()` on all objects.
- **`final` and sealed classes** — `final` blocks subclassing entirely; `sealed` (Java 17+) restricts it to a declared set of permitted subtypes.
- **Protected access** — Sits between `private` and `public`; gives subclasses access without exposing the member to all callers.
- **Fragile base class problem** — Superclass changes can break subclasses in unexpected ways. Favor composition when the inheritance relationship is about reuse rather than true subtyping.

## Example

```java
public class Employee {
    private final String name;
    private double salary;

    public Employee(String name, double salary) {
        this.name = name;
        this.salary = salary;
    }

    public double bonus() {
        return salary * 0.05;
    }

    public String getName()   { return name; }
    public double getSalary() { return salary; }
}

public class Manager extends Employee {
    private final int teamSize;

    public Manager(String name, double salary, int teamSize) {
        super(name, salary);
        this.teamSize = teamSize;
    }

    @Override
    public double bonus() {
        return getSalary() * 0.10 + teamSize * 500;
    }
}
```

`Manager` extends `Employee`, chains the constructor with `super(...)`, and overrides `bonus()` with a formula that accounts for team size. A caller holding an `Employee` reference can call `bonus()` on either type and get the correct result — inheritance combined with polymorphism.
