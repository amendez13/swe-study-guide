# Object Lifecycle and Memory

Understanding how objects are born, live, and die in memory is essential for writing correct and efficient OOP code. Java's garbage collector handles deallocation, but the programmer is still responsible for managing reachability, avoiding null-related bugs, and understanding reference semantics.

## Key Points

- **Object creation** — `new` allocates heap memory, sets defaults, runs the constructor, and returns a reference. Avoid calling overridable methods in constructors.
- **Garbage collection** — The JVM reclaims unreachable objects automatically. Memory leaks are forgotten references, not missing `free()` calls.
- **Null reference** — Calling a method on null throws `NullPointerException`. Defend with `Optional`, null checks at boundaries, and designing away null.
- **Aliasing** — Multiple references to the same object. Mutations through one alias are visible through all others. Mitigate with defensive copying or immutability.
- **Autoboxing / unboxing** — Automatic `int` ↔ `Integer` conversion. Watch for `==` traps on wrapper objects and performance costs in tight loops.

## Example

```java
public class ObjectLifecycleDemo {
    public static void main(String[] args) {
        // 1. Creation — heap allocation + constructor
        StringBuilder sb = new StringBuilder("hello");

        // 2. Aliasing — two references, one object
        StringBuilder alias = sb;
        alias.append(" world");
        System.out.println(sb);        // "hello world"

        // 3. Null danger
        String input = null;
        // input.length();              // would throw NullPointerException
        int len = Optional.ofNullable(input).map(String::length).orElse(0);
        System.out.println(len);       // 0

        // 4. Autoboxing trap
        Integer x = 300;
        Integer y = 300;
        System.out.println(x == y);        // false — identity, not value
        System.out.println(x.equals(y));   // true  — value comparison

        // 5. Eligibility for GC
        sb = null;    // original StringBuilder now eligible (if alias is also cleared)
        alias = null; // now truly unreachable → GC can reclaim it
    }
}
```

This demo walks through the full lifecycle: creation, aliasing, null handling, autoboxing pitfalls, and the moment an object becomes eligible for garbage collection.
