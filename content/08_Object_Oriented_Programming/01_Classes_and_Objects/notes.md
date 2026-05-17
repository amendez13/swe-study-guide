# Classes and Objects

The foundation of object-oriented programming is organizing code around objects — bundles of data and the operations that act on that data — rather than around standalone functions and global state. A class is the template; an object is a living instance of that template with its own state.

## Key Points

- **Class** — A blueprint defining fields (state) and methods (behavior) for a type. No memory is allocated until you instantiate it.
- **Object** — A runtime instance of a class with its own copy of every field. Multiple objects share behavior but hold independent state.
- **Instance variable (field)** — Per-object storage declared in the class body. Contrast with local variables, which live only during a method call.
- **Method** — A function tied to a class that operates in the context of a specific object. Defines what an object can do.
- **Constructor** — A special method called once at object creation to initialize fields and enforce invariants. In Java it shares the class name and has no return type.
- **The `this` reference** — An implicit pointer to the current object, used to disambiguate fields from parameters and to pass the current object elsewhere.
- **Identity vs. equality** — `==` compares memory addresses (identity); `.equals()` compares logical state (equality). Override both `equals()` and `hashCode()` for value-based comparison.
- **Reference semantics** — Variables hold references to objects, not objects themselves. Assignment copies the reference, creating an alias to the same object.

## Example

```java
public class Dog {
    private final String name;
    private int energy;

    public Dog(String name, int energy) {
        this.name = name;
        this.energy = energy;
    }

    public void play() {
        energy -= 10;
        System.out.println(name + " plays! Energy: " + energy);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof Dog other)) return false;
        return name.equals(other.name) && energy == other.energy;
    }

    @Override
    public int hashCode() {
        return java.util.Objects.hash(name, energy);
    }

    public static void main(String[] args) {
        Dog rex = new Dog("Rex", 100);
        Dog buddy = new Dog("Buddy", 80);
        Dog alias = rex;             // alias, not a copy

        rex.play();                  // Rex plays! Energy: 90
        System.out.println(alias == rex);          // true  — same object
        System.out.println(rex.equals(buddy));     // false — different state
    }
}
```

This small class exercises every concept from the topic: `Dog` is a class with two fields, a constructor that uses `this` to initialize them, a method that mutates state, overridden `equals`/`hashCode` for value equality, and a `main` that shows how reference semantics create aliases.
